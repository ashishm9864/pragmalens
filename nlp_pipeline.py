import streamlit as st
import os
import json
import re
from dataclasses import dataclass
import json
import os
import re
import time
from functools import lru_cache
from typing import Iterable

from dotenv import load_dotenv

from trigger_rules import (
    CHANGE_STATE_VERBS,
    CLEFT_TRIGGERS,
    FACTIVE_VERBS,
    IMPLICATIVE_VERBS_NEG,
    IMPLICATIVE_VERBS_POS,
    ITERATIVES,
    Presupposition,
    TEMPORAL_CONJUNCTIONS,
)

load_dotenv()


SYSTEM_PROMPT = """You are a computational linguist expert in formal pragmatics and presupposition theory.

A presupposition is a background assumption embedded in an utterance that must be true for the utterance to make sense. Unlike assertions, presuppositions are not usually consciously noticed by listeners.

Your tasks:
1. Verify whether the candidate is a genuine presupposition in context.
2. State the presupposition in clear, plain English.
3. Explain in 1-2 sentences what a reader implicitly accepts by hearing this sentence.
4. Rate how hidden or subtle this presupposition is for an ordinary reader.

Respond ONLY in this JSON format:
{"verified": true, "presupposition": "...", "explanation": "...", "significance": "...", "subtlety": 3}
"""


@lru_cache(maxsize=1)
@st.cache_resource(show_spinner="Loading language model...")
def load_spacy_model():
    """Load spaCy model (installed via requirements.txt at build time)."""
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error(
            "❌ spaCy model not found. "
            "Check that requirements.txt includes the en-core-web-sm line "
            "and redeploy the app."
        )
        st.stop()


def subtree_text(token) -> str:
    tokens = sorted(token.subtree, key=lambda item: item.i)
    return " ".join(item.text for item in tokens).strip()


def get_subject(verb_token) -> str:
    for child in verb_token.children:
        if child.dep_ in {"nsubj", "nsubjpass"}:
            return subtree_text(child)

    if verb_token.head is not verb_token:
        for child in verb_token.head.children:
            if child.dep_ in {"nsubj", "nsubjpass"}:
                return subtree_text(child)

    return "someone"


def get_complement(verb_token) -> str:
    token = get_complement_token(verb_token)
    if token is not None:
        return subtree_text(token)

    prep_parts = []
    for child in verb_token.children:
        if child.dep_ == "prep":
            prep_parts.append(subtree_text(child))
    return " ".join(prep_parts).strip()


def get_complement_token(verb_token):
    preferred_deps = {"ccomp", "xcomp", "dobj", "obj", "attr", "acomp", "pcomp"}
    for child in verb_token.children:
        if child.dep_ in preferred_deps:
            return child
    return None

def auxiliary_for(subject: str) -> str:
    subject_lower = subject.lower()
    if subject_lower in {"they", "we", "you"} or subject_lower.endswith("s"):
        return "were"
    return "was"


def clean_clause(text: str) -> str:
    text = re.sub(r"^\s*that\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*to\s+", "", text, flags=re.IGNORECASE)
    return text.strip(" ,.")


def sentence_case(text: str) -> str:
    text = clean_clause(text)
    if not text:
        return text
    return text[0].upper() + text[1:]


def make_presupposition(
    trigger_word: str,
    trigger_type: str,
    presupposition: str,
    explanation: str,
    start: int,
    end: int,
    subtlety: int = 3,
    confidence: float = 0.75,
    rule_name: str = "",
    rule_explanation: str = "",
    subject: str = "",
    complement: str = "",
) -> Presupposition:
    return Presupposition(
        trigger_word=trigger_word,
        trigger_type=trigger_type,
        presupposition_str=sentence_case(presupposition),
        explanation=explanation,
        span_start=start,
        span_end=end,
        subtlety=subtlety,
        confidence=confidence,
        rule_name=rule_name,
        rule_explanation=rule_explanation,
        subject=subject,
        complement=clean_clause(complement),
    )


def detect_rule_based(sentence: str) -> list[Presupposition]:
    nlp = load_spacy_model()
    doc = nlp(sentence)
    candidates: list[Presupposition] = []
    seen: set[tuple[int, str]] = set()

    for token in doc:
        lemma = token.lemma_.lower()
        lower = token.text.lower()
        key = (token.idx, token.text.lower())

        if key in seen:
            continue

        if lemma in FACTIVE_VERBS and token.pos_ in {"VERB", "AUX"}:
            complement_token = get_complement_token(token)
            complement = subtree_text(complement_token) if complement_token is not None else get_complement(token)
            if not complement and token.dep_ == "relcl" and token.head.pos_ in {"NOUN", "PROPN"}:
                complement_token = token.head
                complement = token.head.text
            if complement:
                cleaned = clean_clause(complement)
                if complement_token is not None and complement_token.dep_ in {"dobj", "obj"}:
                    cleaned = f"{cleaned} exists or occurred"
                confidence = 0.92 if complement_token is not None and complement_token.dep_ == "ccomp" else 0.78
                seen.add(key)
                candidates.append(
                    make_presupposition(
                        token.text,
                        "factive",
                        cleaned,
                        "Factive verbs present their complement as already true.",
                        token.idx,
                        token.idx + len(token.text),
                        subtlety=3,
                        confidence=confidence,
                        rule_name="factive_complement",
                        rule_explanation="A factive verb such as 'know', 'regret', 'admit', or 'confirm' treats its complement as true background information.",
                        subject=get_subject(token),
                        complement=complement,
                    )
                )

        if lemma in CHANGE_STATE_VERBS and token.pos_ in {"VERB", "AUX"}:
            subject = get_subject(token)
            complement_token = get_complement_token(token)
            complement = subtree_text(complement_token) if complement_token is not None else get_complement(token)
            action = clean_clause(complement) or f"the state connected to '{token.text}'"
            adjective_state = next((child for child in token.children if child.dep_ in {"acomp", "oprd"}), None)
            if lemma == "keep" and complement_token is not None and adjective_state is not None:
                presupposition = f"{clean_clause(subtree_text(complement_token))} was already {adjective_state.text}"
                confidence = 0.82
            elif complement_token is not None and complement_token.dep_ in {"dobj", "obj"}:
                presupposition = f"{action} was already active, underway, or expected"
                confidence = 0.72
            else:
                presupposition = f"{subject} {auxiliary_for(subject)} previously {action}"
                confidence = 0.90 if complement_token is not None and complement_token.dep_ == "xcomp" else 0.78
            seen.add(key)
            candidates.append(
                make_presupposition(
                    token.text,
                    "change_of_state",
                    presupposition,
                    "Change-of-state verbs imply an earlier state that changed.",
                    token.idx,
                    token.idx + len(token.text),
                    subtlety=2,
                    confidence=confidence,
                    rule_name="change_of_state_prior_state",
                    rule_explanation="A change-of-state verb implies that an earlier state held before the reported change.",
                    subject=subject,
                    complement=complement,
                )
            )

        if lemma in (IMPLICATIVE_VERBS_POS | IMPLICATIVE_VERBS_NEG) and token.pos_ in {"VERB", "AUX"}:
            subject = get_subject(token)
            complement_token = get_complement_token(token)
            complement = subtree_text(complement_token) if complement_token is not None else get_complement(token)
            action = clean_clause(complement) or "do the relevant action"
            confidence = 0.88 if complement_token is not None and complement_token.dep_ == "xcomp" else 0.68
            seen.add(key)
            candidates.append(
                make_presupposition(
                    token.text,
                    "implicative",
                    f"{subject} tried to {action}",
                    "Implicative verbs carry assumptions about an attempted action.",
                    token.idx,
                    token.idx + len(token.text),
                    subtlety=3,
                    confidence=confidence,
                    rule_name="implicative_attempt",
                    rule_explanation="Implicative verbs such as 'manage' and 'fail' imply that the subject made an attempt or faced a relevant effort.",
                    subject=subject,
                    complement=complement,
                )
            )

        if lemma in ITERATIVES or lower in ITERATIVES:
            head = token.head
            predicate = subtree_text(head) if head is not token else token.text
            subject = get_subject(head) if head is not token and head.pos_ in {"VERB", "AUX"} else ""
            seen.add(key)
            candidates.append(
                make_presupposition(
                    token.text,
                    "iterative",
                    f"{clean_clause(predicate)} happened or was true before",
                    "Iterative expressions signal repetition or continuation from an earlier context.",
                    token.idx,
                    token.idx + len(token.text),
                    subtlety=4,
                    confidence=0.82,
                    rule_name="iterative_prior_occurrence",
                    rule_explanation="Iterative words such as 'again', 'still', 'back', and 'restore' signal that the event or state has a prior instance.",
                    subject=subject,
                    complement=predicate,
                )
            )

        if lower in TEMPORAL_CONJUNCTIONS and token.dep_ in {"mark", "prep"}:
            if token.dep_ == "prep":
                objects = [child for child in token.children if child.dep_ in {"pobj", "pcomp"}]
                clause = subtree_text(objects[0]) if objects else subtree_text(token)
                confidence = 0.74
            else:
                clause = subtree_text(token.head)
                confidence = 0.86
            seen.add(key)
            candidates.append(
                make_presupposition(
                    token.text,
                    "temporal",
                    clean_clause(clause),
                    "Temporal clauses often treat their event as backgrounded context.",
                    token.idx,
                    token.idx + len(token.text),
                    subtlety=3,
                    confidence=confidence,
                    rule_name="temporal_background_clause",
                    rule_explanation="Temporal conjunctions often introduce an event as background context rather than the sentence's main assertion.",
                    complement=clause,
                )
            )

        if lower == "the" and token.dep_ == "det" and token.head.pos_ in {"NOUN", "PROPN"}:
            noun = token.head
            modifiers = [
                child
                for child in noun.children
                if child.dep_ in {"amod", "compound", "poss", "nmod"} and child.idx >= token.idx
            ]
            np_tokens = sorted([token, noun, *modifiers], key=lambda item: item.idx)
            np_text = " ".join(item.text for item in np_tokens)
            if modifiers or noun.text.lower() in {"king", "official", "resignation", "damage", "mess", "burden", "truth"}:
                entity = re.sub(r"^(the|a|an)\s+", "", clean_clause(subtree_text(noun)), flags=re.IGNORECASE)
                seen.add(key)
                candidates.append(
                    make_presupposition(
                        np_text,
                        "definite_np",
                        f"There is a specific {entity}",
                        "Definite noun phrases ask the reader to accept that the described entity exists.",
                        token.idx,
                        noun.idx + len(noun.text),
                        subtlety=4,
                        confidence=0.88 if noun.text.lower() == "king" else 0.76,
                        rule_name="definite_np_existence",
                        rule_explanation="Definite noun phrases with 'the' ask the reader to treat the described entity as identifiable or already present in the discourse.",
                        complement=entity,
                    )
                )

    candidates.extend(detect_clefts(sentence))
    return dedupe(candidates)


def detect_clefts(sentence: str) -> list[Presupposition]:
    candidates: list[Presupposition] = []
    patterns = [
        r"\b(it\s+(?:was|is))\s+(.+?)\s+(?:who|that)\s+(.+)",
        r"\b(what)\s+(.+?)\s+(?:was|is)\s+(.+)",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, sentence, flags=re.IGNORECASE):
            trigger = match.group(1)
            action = clean_clause(match.group(3))
            trigger_type = "cleft" if trigger.lower() in CLEFT_TRIGGERS else "cleft"
            candidates.append(
                make_presupposition(
                    trigger,
                    trigger_type,
                    f"Someone or something {action}",
                    "Cleft constructions background the event while foregrounding who or what is responsible.",
                    match.start(1),
                    match.end(1),
                    subtlety=4,
                    confidence=0.91,
                    rule_name="cleft_backgrounded_event",
                    rule_explanation="Cleft constructions make the identity of a participant the focus while treating the underlying event as already accepted.",
                    complement=action,
                )
            )
    return candidates


def dedupe(items: Iterable[Presupposition]) -> list[Presupposition]:
    output: list[Presupposition] = []
    seen: set[tuple[str, int, int] | tuple[str, str]] = set()
    for item in items:
        span_key = (item.trigger_type, item.span_start, item.span_end)
        text_key = (item.trigger_type, item.presupposition_str.lower())
        if span_key not in seen and text_key not in seen:
            seen.add(span_key)
            seen.add(text_key)
            output.append(item)
    return sorted(output, key=lambda item: item.span_start)


def build_llm_prompt(sentence: str, candidate: Presupposition) -> str:
    return f"""The user has submitted this sentence:
"{sentence}"

A rule-based parser has identified a potential presupposition trigger:
Trigger word: "{candidate.trigger_word}"
Trigger type: "{candidate.trigger_type}"
Candidate presupposition: "{candidate.presupposition_str}"

Verify and explain the candidate."""


def parse_json_response(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def call_groq(sentence: str, candidate: Presupposition) -> dict:
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_llm_prompt(sentence, candidate)},
        ],
        temperature=0.1,
        max_tokens=350,
        response_format={"type": "json_object"},
    )
    return parse_json_response(response.choices[0].message.content)


def call_openai(sentence: str, candidate: Presupposition) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_llm_prompt(sentence, candidate)},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return parse_json_response(response.choices[0].message.content)


def call_anthropic(sentence: str, candidate: Presupposition) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
        max_tokens=350,
        temperature=0.1,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_llm_prompt(sentence, candidate)}],
    )
    return parse_json_response(response.content[0].text)


def call_llm(sentence: str, candidate: Presupposition) -> dict:
    providers = [
        ("GROQ_API_KEY", "groq", call_groq),
        ("OPENAI_API_KEY", "openai", call_openai),
        ("ANTHROPIC_API_KEY", "anthropic", call_anthropic),
    ]
    available = [(key, label, fn) for key, label, fn in providers if os.environ.get(key)]
    if not available:
        return {
            "verified": True,
            "presupposition": candidate.presupposition_str,
            "explanation": candidate.explanation,
            "significance": "LLM verification is disabled because no API key is configured.",
            "subtlety": candidate.subtlety,
            "source": "rule_based",
        }

    _, label, provider = available[0]
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            result = provider(sentence, candidate)
            result["source"] = label
            return result
        except Exception as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(0.6)

    return {
        "verified": True,
        "presupposition": candidate.presupposition_str,
        "explanation": candidate.explanation,
        "significance": f"LLM verification failed, so this card shows rule-based output. Error: {type(last_error).__name__}",
        "subtlety": candidate.subtlety,
        "source": "rule_based_fallback",
    }


def verify_with_llm(sentence: str, candidates: list[Presupposition]) -> list[Presupposition]:
    verified: list[Presupposition] = []
    for candidate in candidates:
        response = call_llm(sentence, candidate)
        if not response.get("verified", True):
            continue

        candidate.verified = True
        candidate.presupposition_str = response.get("presupposition", candidate.presupposition_str)
        candidate.explanation = response.get("explanation", candidate.explanation)
        candidate.significance = response.get("significance", candidate.significance)
        candidate.subtlety = max(1, min(5, int(response.get("subtlety", candidate.subtlety))))
        candidate.source = response.get("source", candidate.source)
        verified.append(candidate)

    return verified


def run_pipeline(sentence: str, use_llm: bool = True) -> list[Presupposition]:
    sentence = sentence.strip()
    if not sentence:
        return []

    candidates = detect_rule_based(sentence)
    if not use_llm:
        return candidates
    return verify_with_llm(sentence, candidates)


def analyze(sentence: str, use_llm: bool = True) -> list[Presupposition]:
    return run_pipeline(sentence, use_llm=use_llm)
