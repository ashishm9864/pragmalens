# PragmaLens: Revealing Hidden Presuppositions in Language

PragmaLens is a Streamlit app that detects presuppositions: background assumptions embedded in language that listeners often accept without noticing.

## Why It Matters

Presuppositions are common in politics, headlines, everyday speech, and philosophical examples. A sentence can imply that something is already true without directly asserting it. PragmaLens makes those assumptions visible.

## Technical Architecture

```text
User input
-> spaCy tokenization, POS tagging, lemmatization, dependency parsing
-> rule-based trigger detection
-> presupposition candidate generation
-> optional LLM verification and explanation
-> highlighted text, explanation cards, rule evidence, charts, and reports
```

## LLM Integration

The LLM is not the primary detector. PragmaLens first uses spaCy and rule-based NLP to identify structured presupposition candidates. The LLM then:

- verifies whether a candidate is genuine in context
- rewrites the presupposition in plain English
- explains why the wording matters to a reader
- rates subtlety from 1 to 5

If no API key is configured, the app falls back to rule-based output.

## App Features

- Single-sentence presupposition analysis
- Highlighted trigger words
- Trigger distribution and confidence charts
- Rule evidence expanders showing the NLP logic
- Negation test explanation
- Markdown and JSON report downloads
- Batch mode for multiple headlines/sentences
- Internal benchmark evaluation tab
- Demo-prep checklist and pitch text

## Trigger Types

- Factive verbs: `know`, `realize`, `discover`, `regret`, `confirm`
- Implicative verbs: `manage`, `fail`, `neglect`, `avoid`
- Change-of-state verbs: `stop`, `start`, `continue`, `resume`
- Iteratives: `again`, `still`, `back`, `restore`
- Definite noun phrases: `the corrupt official`, `the present king`
- Clefts: `It was John who...`
- Temporal clauses: `before`, `after`, `since`, `when`

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

## Deployment

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud.
3. Select this repo and set `app.py` as the entrypoint.
4. Add `GROQ_API_KEY` in Streamlit secrets for LLM verification.

## Future Work

- Multi-sentence discourse analysis
- More precise extraction for nested clauses
- Corpus-scale analysis for articles and debate transcripts
- User feedback loop for false positives and missed triggers
