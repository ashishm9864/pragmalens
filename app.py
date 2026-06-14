import os

import streamlit as st

from examples import DEMO_SENTENCES, EXAMPLES
from nlp_pipeline import run_pipeline
from utils import display_highlighted_text, display_legend, display_presupposition_card


st.set_page_config(page_title="PragmaLens", page_icon="PL", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --navy: #0F172A;
        --muted: #475569;
        --line: #E2E8F0;
        --panel: #F8FAFC;
    }
    html, body, [class*="css"] {
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--navy);
    }
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }
    h1 {
        letter-spacing: 0;
        font-weight: 800;
    }
    .pl-header {
        border-bottom: 1px solid var(--line);
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }
    .pl-caption {
        color: var(--muted);
        font-size: 1.05rem;
        margin-top: -.6rem;
    }
    .pl-diagram {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 14px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.55;
    }
    .stButton > button {
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


with st.container():
    st.markdown('<div class="pl-header">', unsafe_allow_html=True)
    st.title("PragmaLens")
    st.markdown(
        '<div class="pl-caption">Revealing the hidden assumptions in language</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

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
            st.caption("LLM verification enabled.")
        else:
            st.caption("Rule-based analysis only.")

    analyze_btn = st.button("Analyze Presuppositions", type="primary", use_container_width=True)

with col_info:
    st.info(
        "A presupposition is a background assumption embedded in language. "
        "It is not the main claim, but listeners often accept it for the sentence to make sense."
    )
    st.markdown(
        """
        <div class="pl-diagram">
        <strong>How it works</strong><br>
        Input sentence<br>
        -> spaCy dependency parse<br>
        -> trigger detection rules<br>
        -> optional LLM verification<br>
        -> highlighted assumptions
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
        display_highlighted_text(st.session_state.last_input, st.session_state.last_results)
        display_legend()
        for presupposition in st.session_state.last_results:
            display_presupposition_card(presupposition)

with st.expander("Demo sequence"):
    for sentence in DEMO_SENTENCES:
        st.code(sentence, language=None)

with st.expander("What is this?"):
    st.write(
        "PragmaLens is a small formal-pragmatics demo. It looks for linguistic triggers "
        "such as factive verbs, change-of-state verbs, iteratives, clefts, definite noun "
        "phrases, and temporal clauses. Those constructions often smuggle background "
        "assumptions into ordinary sentences."
    )
    st.write(
        "The rule engine proposes candidate presuppositions from the dependency parse. "
        "When an API key is configured, an LLM verifies each candidate and rewrites it "
        "in plain English."
    )

st.caption("Built at LingHacks VII | Grounded in formal pragmatics theory")

