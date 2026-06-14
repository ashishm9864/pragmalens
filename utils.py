import html
import json
from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from trigger_rules import Presupposition, TRIGGER_COLORS, TRIGGER_LABELS


TYPE_IMPACT = {
    "factive": "This wording treats the embedded claim as already true rather than presenting it as something to debate.",
    "implicative": "This wording makes the reader accept that effort, difficulty, or an attempted action was involved.",
    "change_of_state": "This wording shifts attention to a change while quietly importing the earlier state.",
    "iterative": "This wording frames the event as a recurrence or continuation, so the reader infers a prior instance.",
    "definite_np": "This wording asks the reader to accept that the described entity exists and is identifiable.",
    "temporal": "This wording turns the time clause into background context for interpreting the main claim.",
    "cleft": "This wording treats the event as settled while making the identity of the participant the focus.",
}


def build_highlighted_html(text: str, presuppositions: list[Presupposition]) -> str:
    sorted_items = sorted(presuppositions, key=lambda item: item.span_start)
    parts: list[str] = []
    cursor = 0

    for item in sorted_items:
        if item.span_start < cursor:
            continue

        color = TRIGGER_COLORS.get(item.trigger_type, "#64748B")
        parts.append(html.escape(text[cursor:item.span_start]))
        trigger = html.escape(text[item.span_start:item.span_end])
        label = html.escape(TRIGGER_LABELS.get(item.trigger_type, item.trigger_type))
        parts.append(
            f"<mark title='{label}' style='background:{color}22;"
            f"border-bottom:3px solid {color};color:#0F172A;"
            "padding:2px 4px;border-radius:4px;font-weight:700;'>"
            f"{trigger}</mark>"
        )
        cursor = item.span_end

    parts.append(html.escape(text[cursor:]))
    body = "".join(parts)
    return f"""
    <div style="font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                color:#0F172A;background:#F8FAFC;border:1px solid #E2E8F0;
                border-radius:8px;padding:18px 20px;font-size:20px;line-height:1.7;">
        {body}
    </div>
    """


def display_highlighted_text(text: str, presuppositions: list[Presupposition]) -> None:
    components.html(build_highlighted_html(text, presuppositions), height=125)


def display_legend() -> None:
    cols = st.columns(len(TRIGGER_COLORS))
    for (trigger_type, color), col in zip(TRIGGER_COLORS.items(), cols):
        label = TRIGGER_LABELS.get(trigger_type, trigger_type).replace("_", " ")
        col.markdown(
            f"<span style='color:{color};font-size:18px;'>■</span> "
            f"<span style='font-size:13px;color:#334155;'>{label}</span>",
            unsafe_allow_html=True,
        )


def subtlety_meter(score: int) -> str:
    score = max(1, min(5, int(score or 3)))
    return "●" * score + "○" * (5 - score)


def display_presupposition_card(item: Presupposition) -> None:
    color = TRIGGER_COLORS.get(item.trigger_type, "#64748B")
    label = TRIGGER_LABELS.get(item.trigger_type, item.trigger_type)
    significance = item.significance or TYPE_IMPACT.get(
        item.trigger_type,
        "This assumption is carried by the wording rather than asserted directly.",
    )

    st.markdown(
        f"""
        <section style="border:1px solid #E2E8F0;border-left:5px solid {color};
                        border-radius:8px;padding:16px 18px;margin:14px 0;background:#FFFFFF;">
            <div style="font-size:12px;text-transform:uppercase;letter-spacing:.08em;
                        color:#64748B;font-weight:700;">
                {html.escape(label)} · trigger: "{html.escape(item.trigger_word)}"
            </div>
            <div style="font-size:20px;font-weight:750;color:#0F172A;margin-top:8px;">
                {html.escape(item.presupposition_str)}
            </div>
            <p style="color:#334155;margin:10px 0 0 0;line-height:1.55;">
                {html.escape(item.explanation)}
            </p>
            <p style="color:#475569;margin:8px 0 0 0;line-height:1.55;">
                {html.escape(significance)}
            </p>
            <div style="font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
                        color:#0F172A;margin-top:12px;font-size:14px;">
                Subtlety: {subtlety_meter(item.subtlety)} · Confidence: {item.confidence:.0%} · Source: {html.escape(item.source)}
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def presuppositions_to_rows(sentence: str, presuppositions: list[Presupposition]) -> list[dict]:
    return [
        {
            "sentence": sentence,
            "trigger": item.trigger_word,
            "type": TRIGGER_LABELS.get(item.trigger_type, item.trigger_type),
            "presupposition": item.presupposition_str,
            "confidence": round(item.confidence, 2),
            "subtlety": item.subtlety,
            "source": item.source,
            "rule": item.rule_name,
        }
        for item in presuppositions
    ]


def display_trigger_chart(presuppositions: list[Presupposition]) -> None:
    if not presuppositions:
        return

    counts = Counter(item.trigger_type for item in presuppositions)
    data = pd.DataFrame(
        {
            "Trigger type": [TRIGGER_LABELS.get(key, key) for key in counts.keys()],
            "Count": list(counts.values()),
            "Color": [TRIGGER_COLORS.get(key, "#64748B") for key in counts.keys()],
        }
    )
    fig = px.bar(
        data,
        x="Trigger type",
        y="Count",
        color="Trigger type",
        color_discrete_sequence=data["Color"].tolist(),
        text="Count",
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10),
        height=260,
        yaxis=dict(dtick=1),
    )
    st.plotly_chart(fig, width="stretch")


def display_confidence_chart(presuppositions: list[Presupposition]) -> None:
    if not presuppositions:
        return

    data = pd.DataFrame(
        {
            "Trigger": [item.trigger_word for item in presuppositions],
            "Confidence": [item.confidence for item in presuppositions],
            "Type": [TRIGGER_LABELS.get(item.trigger_type, item.trigger_type) for item in presuppositions],
        }
    )
    fig = px.bar(
        data,
        x="Confidence",
        y="Trigger",
        orientation="h",
        color="Type",
        range_x=[0, 1],
        text=data["Confidence"].map(lambda value: f"{value:.0%}"),
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        height=max(220, 55 * len(presuppositions)),
        xaxis_tickformat=".0%",
    )
    st.plotly_chart(fig, width="stretch")


def display_pipeline_visual() -> None:
    labels = [
        "Input",
        "spaCy Parse",
        "Trigger Rules",
        "Candidates",
        "LLM Verification",
        "Output",
    ]
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="fixed",
                node=dict(
                    pad=20,
                    thickness=18,
                    line=dict(color="#CBD5E1", width=1),
                    label=labels,
                    color=["#0F172A", "#2563EB", "#EA580C", "#7C3AED", "#059669", "#CA8A04"],
                ),
                link=dict(
                    source=[0, 1, 2, 3, 4],
                    target=[1, 2, 3, 4, 5],
                    value=[1, 1, 1, 1, 1],
                    color=["#CBD5E1"] * 5,
                ),
            )
        ]
    )
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), font_size=13)
    st.plotly_chart(fig, width="stretch")


def build_markdown_report(sentence: str, presuppositions: list[Presupposition]) -> str:
    lines = [
        "# PragmaLens Analysis",
        "",
        f"**Sentence:** {sentence}",
        "",
        f"**Detected presuppositions:** {len(presuppositions)}",
        "",
    ]
    for index, item in enumerate(presuppositions, start=1):
        significance = item.significance or TYPE_IMPACT.get(
            item.trigger_type,
            "This assumption is carried by the wording rather than asserted directly.",
        )
        lines.extend(
            [
                f"## {index}. {TRIGGER_LABELS.get(item.trigger_type, item.trigger_type)}",
                f"- Trigger: `{item.trigger_word}`",
                f"- Presupposition: {item.presupposition_str}",
                f"- Explanation: {item.explanation}",
                f"- Why it matters: {significance}",
                f"- Rule: `{item.rule_name}`",
                f"- Confidence: {item.confidence:.0%}",
                f"- Subtlety: {item.subtlety}/5",
                f"- Source: {item.source}",
                "",
            ]
        )
    return "\n".join(lines)


def build_json_report(sentence: str, presuppositions: list[Presupposition]) -> str:
    payload = {
        "sentence": sentence,
        "presupposition_count": len(presuppositions),
        "results": presuppositions_to_rows(sentence, presuppositions),
    }
    return json.dumps(payload, indent=2)


def display_rule_evidence(item: Presupposition) -> None:
    with st.expander(f"Evidence for '{item.trigger_word}'"):
        st.write(item.rule_explanation or "Detected by a rule-based linguistic pattern.")
        cols = st.columns(4)
        cols[0].metric("Trigger", item.trigger_word)
        cols[1].metric("Rule", item.rule_name or item.trigger_type)
        cols[2].metric("Confidence", f"{item.confidence:.0%}")
        cols[3].metric("Subtlety", f"{item.subtlety}/5")
        if item.subject or item.complement:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "subject": item.subject or "n/a",
                            "complement / phrase": item.complement or "n/a",
                            "span": f"{item.span_start}-{item.span_end}",
                        }
                    ]
                ),
                width="stretch",
                hide_index=True,
            )


def negation_probe_text(item: Presupposition) -> str:
    return (
        "Presuppositions usually survive denial or questioning. Even if someone rejects "
        f"the sentence, the wording still tends to carry this background assumption: "
        f"'{item.presupposition_str}'."
    )
