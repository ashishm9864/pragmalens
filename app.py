import html
import os
from statistics import mean

import pandas as pd
import plotly.express as px
import streamlit as st

from examples import COMPARE_PAIRS, EVALUATION_CASES, EXAMPLES, KILLER_DEMOS
from nlp_pipeline import run_pipeline
from trigger_rules import TRIGGER_COLORS, TRIGGER_LABELS
from utils import (
    build_json_report,
    build_markdown_report,
    compute_media_literacy_score,
    display_confidence_chart,
    display_highlighted_text,
    display_legend,
    display_media_literacy_score,
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
    .persona-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
    }
    .persona-card h4 { margin-top: 0; color: #0F172A; }
    .persona-card .example-use {
        background: #EFF6FF;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: #2563EB;
        margin-top: 12px;
    }
    .hero-banner {
        background: linear-gradient(135deg, #EFF6FF 0%, #F5F3FF 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
    }
    .hero-banner h2 { font-size: 1.9rem; color: #0F172A; margin-bottom: 8px; }
    .hero-banner p { font-size: 1.05rem; color: #475569; margin: 0; }
    .pill-badge {
        display: inline-block;
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.82rem;
        color: #475569;
        margin: 12px 8px 0 0;
    }
    .score-card {
        border-radius: 12px;
        padding: 20px 22px;
        background: #F8FAFC;
        border-left: 5px solid;
        margin: 12px 0;
    }
    .score-number { font-size: 2.5rem; font-weight: 900; line-height: 1; }
    .score-bar-track {
        background: #E2E8F0;
        border-radius: 4px;
        height: 8px;
        margin: 10px 0;
    }
    .score-bar-fill {
        border-radius: 4px;
        height: 8px;
    }
    .compare-presup-chip {
        display: inline-block;
        background: #F0FDF4;
        border: 1px solid #86EFAC;
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 0.82rem;
        color: #166534;
        margin: 4px 0;
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


TRIGGER_SAMPLES = {
    "factive": "know, realize, discover...",
    "implicative": "manage, fail, forget...",
    "change_of_state": "stop, start, continue...",
    "iterative": "again, still, back...",
    "definite_np": "the report, the crisis...",
    "temporal": "before, after, when...",
    "cleft": "it was, what...",
}


def display_compact_presupposition(item) -> None:
    color = TRIGGER_COLORS.get(item.trigger_type, "#64748B")
    label = html.escape(TRIGGER_LABELS.get(item.trigger_type, item.trigger_type))
    presupposition = html.escape(item.presupposition_str)
    st.markdown(
        f"""
        <div style="border:1px solid #E2E8F0;border-radius:8px;padding:10px 12px;margin:8px 0;background:#FFFFFF;">
            <span style="display:inline-block;background:{color}18;color:{color};border:1px solid {color}55;
                         border-radius:999px;padding:2px 8px;font-size:0.75rem;font-weight:800;">
                {label}
            </span>
            <div style="color:#0F172A;margin-top:7px;line-height:1.45;">"{presupposition}"</div>
        </div>
        """,
        unsafe_allow_html=True,
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


st.sidebar.title("🔑 API Configuration")
entered_key = st.sidebar.text_input(
    "Groq API Key",
    value=os.environ.get("GROQ_API_KEY", ""),
    type="password",
    placeholder="gsk_...",
)
if entered_key:
    os.environ["GROQ_API_KEY"] = entered_key
    st.sidebar.success("✅ LLM verification enabled")
else:
    st.sidebar.info("Running in rule-based mode (no key)")

st.sidebar.markdown("Get a free key at [console.groq.com](https://console.groq.com)")

with st.sidebar.expander("ℹ️ About PragmaLens"):
    st.write(
        "PragmaLens is a computational linguistics tool for detecting presuppositions: "
        "hidden assumptions embedded in ordinary language. It uses spaCy dependency "
        "parsing and formal trigger rules as the core detector, then can use an LLM to "
        "verify and explain the results. The goal is to make media literacy concrete, "
        "inspectable, and fast enough for live analysis."
    )

with st.sidebar.expander("🔬 Trigger Types"):
    for trigger_type, color in TRIGGER_COLORS.items():
        label = TRIGGER_LABELS.get(trigger_type, trigger_type)
        if trigger_type in {"factive", "implicative"}:
            label = f"{label} Verb"
        sample = TRIGGER_SAMPLES.get(trigger_type, "example triggers...")
        st.markdown(
            f"<span style='color:{color};font-size:1.1rem;'>●</span> "
            f"<strong>{html.escape(label)}</strong> — \"{html.escape(sample)}\"",
            unsafe_allow_html=True,
        )


st.markdown('<div class="pl-header">', unsafe_allow_html=True)
st.title("PragmaLens")
st.markdown(
    '<div class="pl-caption">Revealing hidden assumptions in language with formal pragmatics, spaCy, and optional LLM verification.</div>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

overview_tab, impact_tab, analyze_tab, batch_tab, eval_tab, prep_tab = st.tabs(
    ["Overview", "🌍 Impact", "Analyze", "Batch Mode", "Evaluation", "Demo Prep"]
)

with overview_tab:
    st.markdown(
        """
        <section class="hero-banner">
            <h2>Language has a hidden layer.</h2>
            <p>
                Every sentence can carry background assumptions that listeners accept silently.
                PragmaLens makes that layer visible — for the first time, in real time.
            </p>
            <span class="pill-badge">📖 Grounded in formal pragmatics</span>
            <span class="pill-badge">🔬 spaCy + LLM hybrid pipeline</span>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("See it in action")
    hero_cols = st.columns([4, 1], gap="large")
    with hero_cols[0]:
        hero_input_text = st.text_input(
            "Try any sentence:",
            key="hero_input",
            value="When did politicians stop caring about ordinary people?",
        )
    with hero_cols[1]:
        st.write("")
        hero_analyze = st.button("→ Analyze")

    if hero_analyze:
        with st.spinner("Checking for hidden assumptions..."):
            hero_results = run_pipeline(hero_input_text, use_llm=has_api_key())
        if hero_results:
            display_presupposition_card(hero_results[0])
        else:
            st.info("No presuppositions detected for this sentence.")

    st.divider()

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

with impact_tab:
    st.markdown(
        """
        <section style="background:#EFF6FF;border-left:6px solid #2563EB;border-radius:12px;
                        padding:20px 24px;margin-bottom:24px;">
            <div style="font-size:1.65rem;font-weight:900;color:#0F172A;line-height:1.25;">
                1 in 3 news headlines contains at least one presupposition.
            </div>
            <div style="font-size:1.05rem;color:#475569;margin-top:6px;">
                Most readers never notice. PragmaLens changes that.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Who Benefits")
    persona_cols = st.columns(3, gap="large")
    with persona_cols[0]:
        with st.container():
            st.markdown(
                """
                <div class="pl-callout persona-card">
                    <h4>📰 Fact-Checkers & Journalists</h4>
                    <p>
                        When covering political statements or press releases, presuppositions
                        often go unchallenged because they are never stated as claims. PragmaLens
                        surfaces them so journalists can examine what is being assumed, not just asserted.
                    </p>
                    <div class="example-use">Paste a press release → identify all embedded assumptions before writing.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with persona_cols[1]:
        with st.container():
            st.markdown(
                """
                <div class="pl-callout persona-card">
                    <h4>🎓 Teachers & Students</h4>
                    <p>
                        Media literacy curricula teach students to question sources, but rarely
                        teach them to question the grammar itself. PragmaLens teaches the linguistic
                        layer — how presuppositions differ from assertions, and why that matters.
                    </p>
                    <div class="example-use">Use batch mode on a set of exam debate texts → compare assumption loads.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with persona_cols[2]:
        with st.container():
            st.markdown(
                """
                <div class="pl-callout persona-card">
                    <h4>🗳️ Citizens & Policy Researchers</h4>
                    <p>
                        Political advertising and campaign speeches are built on presuppositions.
                        A question like 'When will you fix the crisis you caused?' embeds an accusation
                        before the listener can evaluate whether a crisis exists or who caused it.
                    </p>
                    <div class="example-use">Paste any political statement → see what you are being asked to assume.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("Before PragmaLens / After PragmaLens")
    before_cols = st.columns(2, gap="large")
    with before_cols[0]:
        st.markdown("**Without PragmaLens**")
        st.write("When did politicians stop caring about ordinary people?")
        st.markdown(
            """
            <div style="background:#F1F5F9;border:1px solid #CBD5E1;border-radius:8px;
                        padding:14px 16px;color:#334155;line-height:1.55;">
                <strong>Reader sees:</strong> A question about politicians.<br>
                <strong>Reader does not see:</strong> The assumption that politicians did care before,
                and that they have stopped.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with before_cols[1]:
        st.markdown("**With PragmaLens**")
        st.markdown(
            """
            <div style="font-size:1.05rem;line-height:1.8;color:#0F172A;">
                When did politicians
                <mark style="background:#FFEDD5;border-bottom:3px solid #EA580C;
                             color:#0F172A;padding:2px 4px;border-radius:4px;font-weight:800;">
                    stop
                </mark>
                caring about ordinary people?
            </div>
            <div style="margin-top:12px;">
                <span class="compare-presup-chip">✓ Politicians previously cared about ordinary people.</span><br>
                <span class="compare-presup-chip">✓ Politicians have now stopped caring.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Where Presuppositions Are Used Against You")
    app_row_one = st.columns(2, gap="large")
    app_row_one[0].info(
        "🏛️ Politics\n\nLoaded questions in debates presuppose guilt, failure, or wrongdoing. "
        "'Will you finally address the corruption in your department?' assumes corruption exists."
    )
    app_row_one[1].info(
        "📺 Advertising\n\nProduct copy uses presuppositions to make claims feel like facts. "
        "'When you're tired of your old phone...' assumes you are tired of it."
    )
    app_row_two = st.columns(2, gap="large")
    app_row_two[0].info(
        "⚖️ Legal Language\n\nLeading questions in courtrooms presuppose the answer. "
        "'Why were you driving so fast?' assumes speeding occurred."
    )
    app_row_two[1].info(
        "🏥 Health Communication\n\nPublic health messaging can use presuppositions to shape behavior. "
        "'Now that we know vaccines cause side effects...' presupposes an established fact."
    )

    st.subheader("Scale of the Problem")
    metric_cols = st.columns(3, gap="large")
    metric_cols[0].metric("Languages with presuppositions", "All of them")
    metric_cols[1].metric("Trigger types detected", "7")
    metric_cols[2].metric("Potential users", "Anyone who reads news")
    st.write(
        "Presuppositions are not a bug in language — they are a feature. Every language "
        "uses them. The problem is not that speakers presuppose things. The problem is "
        "that listeners are rarely taught to notice when it is happening. PragmaLens "
        "is the first practical tool to surface this layer in real time."
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
            display_media_literacy_score(compute_media_literacy_score([]))
        else:
            results = st.session_state.last_results
            display_result_summary(results)
            display_media_literacy_score(compute_media_literacy_score(results))
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

    st.divider()
    st.subheader("⚡ Compare Two Texts")
    st.caption(
        "Paste two headlines or statements covering the same topic. See which one embeds more hidden assumptions."
    )

    compare_options = [pair["name"] for pair in COMPARE_PAIRS] + ["Custom"]
    selected_pair_name = st.selectbox("Load example pair", compare_options)
    selected_pair = next((pair for pair in COMPARE_PAIRS if pair["name"] == selected_pair_name), None)

    if "compare_pair_loaded" not in st.session_state:
        st.session_state.compare_pair_loaded = selected_pair_name
        if selected_pair:
            st.session_state.compare_a = selected_pair["a"]
            st.session_state.compare_b = selected_pair["b"]
        else:
            st.session_state.setdefault("compare_a", "")
            st.session_state.setdefault("compare_b", "")
    elif selected_pair_name != st.session_state.compare_pair_loaded:
        st.session_state.compare_pair_loaded = selected_pair_name
        if selected_pair:
            st.session_state.compare_a = selected_pair["a"]
            st.session_state.compare_b = selected_pair["b"]

    compare_cols = st.columns(2, gap="large")
    with compare_cols[0]:
        text_a = st.text_area("Text A", height=90, key="compare_a")
    with compare_cols[1]:
        text_b = st.text_area("Text B", height=90, key="compare_b")

    if st.button("⚡ Compare Presupposition Load"):
        with st.spinner("Comparing presupposition load..."):
            results_a = run_pipeline(text_a, use_llm=use_llm)
            results_b = run_pipeline(text_b, use_llm=use_llm)

        result_cols = st.columns(2, gap="large")
        with result_cols[0]:
            st.markdown("**Text A**")
            display_highlighted_text(text_a, results_a)
            st.markdown(f"**{len(results_a)} presuppositions detected**")
            for presupposition in results_a:
                display_compact_presupposition(presupposition)
        with result_cols[1]:
            st.markdown("**Text B**")
            display_highlighted_text(text_b, results_b)
            st.markdown(f"**{len(results_b)} presuppositions detected**")
            for presupposition in results_b:
                display_compact_presupposition(presupposition)

        compare_df = pd.DataFrame(
            {
                "Text": ["Text A", "Text B"],
                "Count": [len(results_a), len(results_b)],
            }
        )
        compare_fig = px.bar(
            compare_df,
            x="Text",
            y="Count",
            color="Text",
            color_discrete_map={"Text A": "#4A90E2", "Text B": "#E67E22"},
            text="Count",
            title="Presupposition Count Comparison",
        )
        compare_fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(compare_fig, width="stretch")

        if len(results_a) > len(results_b):
            st.warning(
                f"Text A carries a heavier presupposition load ({len(results_a)} vs {len(results_b)}). "
                "Its framing embeds more assumptions that readers accept without questioning."
            )
        elif len(results_b) > len(results_a):
            st.warning(
                f"Text B carries a heavier presupposition load ({len(results_b)} vs {len(results_a)}). "
                "Its framing embeds more assumptions that readers accept without questioning."
            )
        else:
            st.success(f"Both texts carry a similar presupposition load ({len(results_a)} each).")

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
        batch_scores = []
        progress = st.progress(0)
        for index, sentence in enumerate(sentences, start=1):
            results = run_pipeline(sentence, use_llm=batch_use_llm)
            media_score = compute_media_literacy_score(results)["score"]
            batch_scores.append(media_score)
            detail_rows.extend(presuppositions_to_rows(sentence, results))
            summary_rows.append(
                {
                    "sentence": sentence,
                    "count": len(results),
                    "avg_confidence": round(mean(item.confidence for item in results), 2) if results else 0,
                    "avg_subtlety": round(mean(item.subtlety for item in results), 2) if results else 0,
                    "media_literacy_score": media_score,
                    "trigger_types": ", ".join(sorted({TRIGGER_LABELS.get(item.trigger_type, item.trigger_type) for item in results})),
                }
            )
            progress.progress(index / len(sentences))

        summary_df = pd.DataFrame(summary_rows)
        detail_df = pd.DataFrame(detail_rows)
        st.markdown("**Summary**")
        st.dataframe(summary_df, width="stretch", hide_index=True)
        if batch_scores:
            avg_score = round(mean(batch_scores), 1)
            st.metric("Average Manipulation Load", f"{avg_score}/10")
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
