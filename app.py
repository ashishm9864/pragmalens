import os
from statistics import mean

import pandas as pd
import plotly.express as px
import streamlit as st

from examples import EVALUATION_CASES, EXAMPLES, KILLER_DEMOS
from nlp_pipeline import run_pipeline
from trigger_rules import TRIGGER_LABELS
from utils import (
    build_json_report,
    build_markdown_report,
    display_confidence_chart,
    display_highlighted_text,
    display_legend,
    display_pipeline_visual,
    display_presupposition_card,
    display_rule_evidence,
    display_trigger_chart,
    negation_probe_text,
    presuppositions_to_rows,
)


st.set_page_config(page_title="PragmaLens", page_icon="PL", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --navy: #0F172A;
        --muted: #475569;
        --line: #E2E8F0;
        --panel: #F8FAFC;
        --accent: #2563EB;
    }
    html, body, [class*="css"] {
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--navy);
    }
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 2.5rem;
        max-width: 1220px;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    .pl-header {
        border-bottom: 1px solid var(--line);
        padding-bottom: 1rem;
        margin-bottom: 1.2rem;
    }
    .pl-caption {
        color: var(--muted);
        font-size: 1.05rem;
        margin-top: -.6rem;
    }
    .pl-callout {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 15px 17px;
        color: #334155;
        line-height: 1.55;
        min-height: 100%;
    }
    .pl-tag {
        display: inline-block;
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 4px 8px;
        margin: 3px 4px 3px 0;
        font-size: 12px;
        color: #334155;
        background: #FFFFFF;
    }
    .stButton > button, .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 700;
    }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def has_api_key() -> bool:
    return any(
        os.environ.get(name)
        for name in ("GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY")
    )


def source_label(use_llm: bool) -> str:
    if not use_llm:
        return "Rule-based"
    if os.environ.get("GROQ_API_KEY"):
        return "Groq LLM"
    if os.environ.get("OPENAI_API_KEY"):
        return "OpenAI LLM"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "Anthropic LLM"
    return "Rule-based fallback"


def display_result_summary(results) -> None:
    if not results:
        return
    cols = st.columns(4)
    cols[0].metric("Detected", len(results))
    cols[1].metric("Avg confidence", f"{mean(item.confidence for item in results):.0%}")
    cols[2].metric("Avg subtlety", f"{mean(item.subtlety for item in results):.1f}/5")
    cols[3].metric("Trigger types", len({item.trigger_type for item in results}))


def display_downloads(sentence: str, results) -> None:
    col_md, col_json = st.columns(2)
    col_md.download_button(
        "Download Markdown report",
        build_markdown_report(sentence, results),
        file_name="pragmalens-analysis.md",
        mime="text/markdown",
        width="stretch",
    )
    col_json.download_button(
        "Download JSON report",
        build_json_report(sentence, results),
        file_name="pragmalens-analysis.json",
        mime="application/json",
        width="stretch",
    )


def run_evaluation() -> pd.DataFrame:
    rows = []
    for case in EVALUATION_CASES:
        results = run_pipeline(case["sentence"], use_llm=False)
        detected = {item.trigger_type for item in results}
        expected = case["expected"]
        passed = expected.issubset(detected)
        rows.append(
            {
                "sentence": case["sentence"],
                "expected": ", ".join(sorted(expected)),
                "detected": ", ".join(sorted(detected)) or "none",
                "pass": passed,
                "count": len(results),
            }
        )
    return pd.DataFrame(rows)


st.markdown('<div class="pl-header">', unsafe_allow_html=True)
st.title("PragmaLens")
st.markdown(
    '<div class="pl-caption">Revealing hidden assumptions in language with formal pragmatics, spaCy, and optional LLM verification.</div>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

overview_tab, analyze_tab, batch_tab, eval_tab, prep_tab = st.tabs(
    ["Overview", "Analyze", "Batch Mode", "Evaluation", "Demo Prep"]
)

with overview_tab:
    st.subheader("Project Summary")
    summary_cols = st.columns([1.2, 1])
    with summary_cols[0]:
        st.markdown(
            """
            <div class="pl-callout">
            <strong>Problem:</strong> people often accept hidden assumptions because wording
            makes them feel like background facts rather than claims to inspect.
            <br><br>
            <strong>Solution:</strong> PragmaLens detects presupposition triggers, extracts
            the implied assumption, highlights the trigger, and explains why the assumption matters.
            <br><br>
            <strong>Method:</strong> the detector uses dependency parsing and formal
            pragmatics rules first. An LLM is then used as a verifier and explanation layer,
            not as the primary detector.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[1]:
        st.markdown(
            """
            <div class="pl-callout">
            <strong>What it uses</strong><br>
            <span class="pl-tag">Streamlit UI</span>
            <span class="pl-tag">spaCy parsing</span>
            <span class="pl-tag">Dependency trees</span>
            <span class="pl-tag">Rule-based NLP</span>
            <span class="pl-tag">Groq/OpenAI/Anthropic optional</span>
            <span class="pl-tag">Plotly visuals</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Method Visual")
    display_pipeline_visual()

    st.subheader("What the LLM Adds")
    llm_cols = st.columns(4)
    llm_cols[0].info("Verifies whether a rule-based candidate is genuine in context.")
    llm_cols[1].info("Rewrites technical candidates into plain English.")
    llm_cols[2].info("Explains the reader impact and why the wording matters.")
    llm_cols[3].info("Rates subtlety so judges can see which assumptions are hardest to notice.")

    with st.expander("Why this is stronger than a generic chatbot"):
        st.write(
            "The app does not ask an LLM to guess from scratch. It first uses spaCy to find "
            "grammatical evidence: lemmas, part-of-speech tags, dependency labels, subjects, "
            "objects, complements, and clause structure. The LLM only receives structured "
            "candidates from that engine, then verifies and explains them."
        )

with analyze_tab:
    col_input, col_info = st.columns([3, 1], gap="large")

    with col_input:
        example_category = st.selectbox("Try an example", list(EXAMPLES.keys()))
        example = st.selectbox("Example sentence", EXAMPLES[example_category], label_visibility="collapsed")

        user_input = st.text_area(
            "Or enter your own sentence",
            value=example,
            height=115,
            placeholder="Type one sentence to inspect its hidden assumptions.",
        )

        settings_cols = st.columns([1, 2])
        with settings_cols[0]:
            use_llm = st.toggle("Use LLM verification", value=has_api_key())
        with settings_cols[1]:
            if use_llm and not has_api_key():
                st.caption("No API key found. Add GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY to .env.")
            elif use_llm:
                st.caption(f"{source_label(use_llm)} enabled.")
            else:
                st.caption("Rule-based analysis only.")

        analyze_btn = st.button("Analyze Presuppositions", type="primary", width="stretch")

    with col_info:
        st.info(
            "A presupposition is a background assumption embedded in language. "
            "It is not the main claim, but listeners often accept it for the sentence to make sense."
        )
        st.markdown(
            """
            <div class="pl-callout">
            <strong>Detected trigger families</strong><br>
            Factive verbs<br>
            Change-of-state verbs<br>
            Implicatives<br>
            Iteratives<br>
            Definite noun phrases<br>
            Clefts<br>
            Temporal clauses
            </div>
            """,
            unsafe_allow_html=True,
        )

    if "last_input" not in st.session_state:
        st.session_state.last_input = ""
    if "last_results" not in st.session_state:
        st.session_state.last_results = []
    if "last_error" not in st.session_state:
        st.session_state.last_error = ""

    if analyze_btn:
        with st.spinner("Analyzing linguistic structure..."):
            try:
                st.session_state.last_results = run_pipeline(user_input, use_llm=use_llm)
                st.session_state.last_input = user_input
                st.session_state.last_error = ""
            except Exception as exc:
                st.session_state.last_results = []
                st.session_state.last_input = user_input
                st.session_state.last_error = str(exc)

    if st.session_state.last_input:
        st.divider()
        st.subheader("Results")

        if st.session_state.last_error:
            st.error(st.session_state.last_error)
        elif not st.session_state.last_results:
            st.success("No presuppositions detected. This sentence is relatively transparent.")
        else:
            results = st.session_state.last_results
            display_result_summary(results)
            display_highlighted_text(st.session_state.last_input, results)
            display_legend()

            chart_cols = st.columns(2)
            with chart_cols[0]:
                st.markdown("**Trigger Distribution**")
                display_trigger_chart(results)
            with chart_cols[1]:
                st.markdown("**Confidence by Trigger**")
                display_confidence_chart(results)

            st.markdown("**Presupposition Cards**")
            for presupposition in results:
                display_presupposition_card(presupposition)
                display_rule_evidence(presupposition)
                with st.expander(f"Negation test for '{presupposition.trigger_word}'"):
                    st.write(negation_probe_text(presupposition))

            display_downloads(st.session_state.last_input, results)

with batch_tab:
    st.subheader("Batch Headline and Sentence Analysis")
    st.write(
        "Paste one sentence per line to compare how many hidden assumptions appear across a set of headlines, claims, or debate lines."
    )
    batch_text = st.text_area(
        "Sentences",
        value="\n".join(
            [
                "New report confirms the damage done by previous policies.",
                "When did politicians stop caring about ordinary people?",
                "The agency finally stopped hiding the inspection failures.",
                "She managed to finish before the deadline.",
            ]
        ),
        height=150,
    )
    batch_use_llm = st.toggle("Use LLM in batch mode", value=False)
    if st.button("Run Batch Analysis", type="primary"):
        sentences = [line.strip() for line in batch_text.splitlines() if line.strip()]
        summary_rows = []
        detail_rows = []
        progress = st.progress(0)
        for index, sentence in enumerate(sentences, start=1):
            results = run_pipeline(sentence, use_llm=batch_use_llm)
            detail_rows.extend(presuppositions_to_rows(sentence, results))
            summary_rows.append(
                {
                    "sentence": sentence,
                    "count": len(results),
                    "avg_confidence": round(mean(item.confidence for item in results), 2) if results else 0,
                    "avg_subtlety": round(mean(item.subtlety for item in results), 2) if results else 0,
                    "trigger_types": ", ".join(sorted({TRIGGER_LABELS.get(item.trigger_type, item.trigger_type) for item in results})),
                }
            )
            progress.progress(index / len(sentences))

        summary_df = pd.DataFrame(summary_rows)
        detail_df = pd.DataFrame(detail_rows)
        st.markdown("**Summary**")
        st.dataframe(summary_df, width="stretch", hide_index=True)
        if not summary_df.empty:
            fig = px.bar(summary_df, x="sentence", y="count", text="count", title="Presuppositions per Sentence")
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=45, b=10), xaxis_tickangle=-25)
            st.plotly_chart(fig, width="stretch")
        st.markdown("**Detailed Results**")
        st.dataframe(detail_df, width="stretch", hide_index=True)
        st.download_button(
            "Download batch CSV",
            detail_df.to_csv(index=False),
            file_name="pragmalens-batch.csv",
            mime="text/csv",
            width="stretch",
        )

with eval_tab:
    st.subheader("Internal Benchmark")
    st.write(
        "This lightweight benchmark checks whether the rule engine detects the expected trigger families for curated examples."
    )
    if st.button("Run Evaluation", type="primary"):
        eval_df = run_evaluation()
        pass_rate = eval_df["pass"].mean() if not eval_df.empty else 0
        metric_cols = st.columns(3)
        metric_cols[0].metric("Cases", len(eval_df))
        metric_cols[1].metric("Pass rate", f"{pass_rate:.0%}")
        metric_cols[2].metric("Total detections", int(eval_df["count"].sum()))
        st.dataframe(eval_df, width="stretch", hide_index=True)
        chart_df = eval_df.assign(result=eval_df["pass"].map({True: "Pass", False: "Fail"}))
        fig = px.histogram(chart_df, x="result", color="result", title="Evaluation Results")
        fig.update_layout(height=280, margin=dict(l=10, r=10, t=45, b=10), showlegend=False)
        st.plotly_chart(fig, width="stretch")

with prep_tab:
    st.subheader("Demo Sequence")
    for item in KILLER_DEMOS:
        with st.expander(item["title"]):
            st.code(item["sentence"], language=None)
            st.write(item["why"])

    st.subheader("60-Second Pitch")
    st.markdown(
        """
        PragmaLens reveals hidden assumptions in language. It solves the problem that
        loaded questions, headlines, and everyday phrasing can make readers accept a
        background claim without noticing. The system uses spaCy dependency parsing and
        formal presupposition trigger rules to detect candidates, then optionally uses
        an LLM to verify and explain the result in plain English.
        """
    )

    st.subheader("Prize-Ready Checklist")
    st.checkbox("Run the single-sentence demo with LLM verification enabled.")
    st.checkbox("Run batch mode on 3-5 news/political examples.")
    st.checkbox("Run the evaluation tab and mention the pass rate.")
    st.checkbox("Show one rule evidence expander to prove real NLP is used.")
    st.checkbox("Download the Markdown report as a polished artifact.")

st.caption("Built at LingHacks VII | Grounded in formal pragmatics theory")
