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

st.set_page_config(page_title="Security Social Post Generator", page_icon="🛡️", layout="centered")

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

# --- Inputs ---
source_text = st.text_area(
    "Source material",
    height=200,
    placeholder="Paste the CISA alert, blog post, or announcement text here...",
)

col1, col2 = st.columns(2)
with col1:
    platform = st.selectbox("Platform", list(PLATFORM_GUIDANCE.keys()))
with col2:
    audience = st.selectbox("Audience", list(AUDIENCE_GUIDANCE.keys()))

generate = st.button("Generate", type="primary", disabled=not source_text or not client)

def call_claude(prompt: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


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
        except Exception as e:
            st.error(f"Generation failed: {e}")

# --- Output ---
if "output" in st.session_state:
    output = st.session_state["output"]
    limit = CHAR_LIMITS.get(platform)

    st.subheader("Generated post")
    st.text_area("Output", value=output, height=200, label_visibility="collapsed")
    st.code(output, language=None)  # easy one-click copy via the code block

    char_count = len(output)
    if limit:
        if char_count > limit:
            st.warning(f"{char_count} / {limit} characters, still over the limit after auto-shortening. Consider trimming the source material or regenerating.")
        else:
            st.caption(f"{char_count} / {limit} characters")
    else:
        st.caption(f"{char_count} characters")
