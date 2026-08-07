import os
import streamlit as st
import anthropic

from prompts import (
    build_prompt,
    build_shorten_prompt,
    enforce_style,
    CHAR_LIMITS,
    PLATFORM_GUIDANCE,
    AUDIENCE_GUIDANCE,
)

st.set_page_config(page_title="Security Social Post Generator", page_icon="🛡️", layout="wide")

st.title("🛡️ Security Social Post Generator")
st.caption(
    "Paste a CISA alert, vendor blog post, or product announcement. "
    "Get back audience-tuned social content for your security team."
)

# --- API client setup ---
# Set your key as an environment variable: ANTHROPIC_API_KEY
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    st.warning(
        "No ANTHROPIC_API_KEY found in environment. "
        "Set it before running, e.g. `export ANTHROPIC_API_KEY=sk-...`"
    )

client = anthropic.Anthropic(api_key=api_key) if api_key else None


def call_claude(prompt: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


# --- Sidebar: all inputs live here, output gets the main stage ---
with st.sidebar:
    st.header("Source material")
    source_text = st.text_area(
        "Paste the CISA alert, blog post, or announcement text here",
        height=220,
        placeholder="Paste the CISA alert, blog post, or announcement text here...",
        label_visibility="collapsed",
    )

    platform = st.selectbox("Platform", list(PLATFORM_GUIDANCE.keys()))
    audience = st.selectbox("Audience", list(AUDIENCE_GUIDANCE.keys()))

    generate = st.button(
        "Generate",
        type="primary",
        use_container_width=True,
        disabled=not source_text or not client,
    )

    if not source_text:
        st.caption("Paste some source material to enable generation.")

# --- Generation ---
if generate:
    with st.spinner("Generating..."):
        try:
            output = call_claude(build_prompt(source_text, platform, audience))
            output = enforce_style(output)

            limit = CHAR_LIMITS.get(platform)
            if limit and len(output) > limit:
                # Model overshot the limit -> one automatic shortening pass
                # rather than trusting instructions alone.
                with st.spinner("First draft ran long, tightening it..."):
                    output = call_claude(build_shorten_prompt(output, limit))
                    output = enforce_style(output)

            st.session_state["output"] = output
            st.session_state["output_platform"] = platform
            st.session_state["output_audience"] = audience
        except Exception as e:
            st.error(f"Generation failed: {e}")

# --- Main area: output, or a friendly empty state ---
if "output" in st.session_state:
    output = st.session_state["output"]
    out_platform = st.session_state["output_platform"]
    out_audience = st.session_state["output_audience"]
    limit = CHAR_LIMITS.get(out_platform)
    char_count = len(output)

    st.subheader(f"{out_platform} · {out_audience}")
    st.code(output, language=None, wrap_lines=True)  # built-in copy icon, no separate copy button needed

    if limit:
        over = char_count > limit
        pct = min(char_count / limit, 1.0)
        st.progress(pct, text=f"{char_count} / {limit} characters")
        if over:
            st.warning(
                "Still over the limit after auto-shortening. "
                "Consider trimming the source material or regenerating."
            )
    else:
        st.caption(f"{char_count} characters")
else:
    st.info(
        "👈 Paste source material in the sidebar, pick a platform and audience, "
        "and hit **Generate** to see a draft here."
    )

