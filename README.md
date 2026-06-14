# PragmaLens: Revealing Hidden Presuppositions in Language

> Built at LingHacks VII — Computational Linguistics Hackathon

## What Problem Does It Solve?
One in three news headlines contains at least one linguistic presupposition — a hidden 
assumption that readers accept without realizing it is there. When a journalist asks 
"When will you fix the mess you created?", they have embedded two claims before the 
interviewee speaks: that a mess exists, and that the interviewee created it.

PragmaLens is the first practical tool to detect, explain, and score these hidden 
assumptions in real time.

## Who Benefits?
- **Journalists** — surface framing in headlines, drafts, press releases, and uploaded documents before publication
- **Educators** — teach media literacy at the grammatical layer
- **Citizens** — evaluate political speech critically

## How It Works
[Technical architecture section — keep existing]

## What Makes It Different?
Unlike fact-checkers (which check what is stated), PragmaLens checks what is assumed.
Unlike sentiment analyzers (which check tone), PragmaLens checks logical structure.
It is grounded in 70+ years of formal pragmatics theory — Frege (1892), Strawson (1950),
Karttunen (1973) — implemented with spaCy dependency parsing and optional LLM verification.

## Why It Matters

Presuppositions are common in politics, headlines, everyday speech, and philosophical examples. A sentence can imply that something is already true without directly asserting it. PragmaLens makes those assumptions visible.

## Features
- Single-sentence presupposition analysis
- Highlighted trigger words
- Media Literacy Score for hidden-assumption load
- Headline comparison for newsroom framing decisions
- Trigger distribution and confidence charts
- Rule evidence expanders showing the NLP logic
- Negation test explanation
- Markdown and JSON report downloads
- Batch mode for multiple headlines/sentences
- Article Lab for pasted articles, transcripts, Markdown files, text files, and Word documents
- Sentence-by-sentence article risk ranking
- Downloadable assumption ledger CSV and editor brief
- Internal benchmark evaluation tab
- Demo-prep sequence and pitch text


## Technical Architecture

```text
User input
-> spaCy tokenization, POS tagging, lemmatization, dependency parsing
-> rule-based trigger detection
-> presupposition candidate generation
-> optional LLM verification and explanation
-> highlighted text, explanation cards, rule evidence, charts, and reports
```

For full documents, PragmaLens extracts text from pasted drafts or uploads, segments the
article into sentences with spaCy, scores each sentence, ranks the highest-risk lines,
and exports an editor-facing assumption ledger.

## LLM Integration

The LLM is not the primary detector. PragmaLens first uses spaCy and rule-based NLP to identify structured presupposition candidates. The LLM then:

- verifies whether a candidate is genuine in context
- rewrites the presupposition in plain English
- explains why the wording matters to a reader
- rates subtlety from 1 to 5

If no API key is configured, the app falls back to rule-based output.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
streamlit run app.py
```

LLM verification is optional. For the recommended setup, add `GROQ_API_KEY` to `.env`. The app also supports `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.

## Demo Sentences

```text
The present king of France is bald.
When did politicians stop caring about ordinary people?
She managed to finish before the deadline.
New report confirms the damage done by previous policies.
```


## Trigger Types

- Factive verbs: `know`, `realize`, `discover`, `regret`, `confirm`
- Implicative verbs: `manage`, `fail`, `neglect`, `avoid`
- Change-of-state verbs: `stop`, `start`, `continue`, `resume`
- Iteratives: `again`, `still`, `back`, `restore`
- Definite noun phrases: `the corrupt official`, `the present king`
- Clefts: `It was John who...`
- Temporal clauses: `before`, `after`, `since`, `when`
