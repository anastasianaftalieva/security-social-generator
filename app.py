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

st.set_page_config(page_title="Social Content Payload", page_icon="🛡️", layout="wide")

# --- Custom styling: dark green sidebar, cream canvas, serif headlines, mono labels ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Source+Serif+4:wght@600;700&display=swap');

    h1, h2, h3 {
        font-family: 'Source Serif 4', Georgia, serif !important;
        color: #16241a;
    }

    /* Sidebar: dark green, light text, mono labels */
    section[data-testid="stSidebar"] {
        background-color: #0f2818;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stCaption {
        color: #e9f2e2 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    section[data-testid="stSidebar"] textarea {
        background-color: #16351f !important;
        color: #e9f2e2 !important;
        border: 1px solid #3a5a44 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #16351f !important;
        border: 1px solid #3a5a44 !important;
        color: #e9f2e2 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #e9f2e2 !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #baff3d !important;
        color: #0f2818 !important;
        border: none !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"]:disabled {
        background-color: #2c4636 !important;
        color: #a9c4a0 !important;
        opacity: 1 !important;
    }

    /* Small uppercase mono badge, used for the output header */
    .post-badge {
        display: inline-block;
        background-color: #baff3d;
        color: #0f2818;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.3rem 0.7rem;
        border-radius: 4px;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛡️ Social Content Payload")
st.caption(
    "Paste a CISA alert, vendor blog post, or product announcement. "
    "Get back audience-tuned social content, ready for you to review and post."
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

    st.markdown(
        f'<span class="post-badge">{out_platform} · {out_audience}</span>',
        unsafe_allow_html=True,
    )
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

