import html

import streamlit as st
import streamlit.components.v1 as components

from trigger_rules import Presupposition, TRIGGER_COLORS, TRIGGER_LABELS


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
    significance = item.significance or "This assumption is carried by the wording rather than asserted directly."

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
                Subtlety: {subtlety_meter(item.subtlety)}
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

