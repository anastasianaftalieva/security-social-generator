"""
Prompt templates for generating security-team social content.

This is the core intellectual property of the app — the prompts encode
audience-specific tone, structure, and framing decisions. Keep iterating
on these as you test with real content.
"""

AUDIENCE_GUIDANCE = {
    "Security practitioners": (
        "Write for a technical security audience (SOC analysts, security engineers, "
        "CISOs' technical staff). Use precise security terminology. It's fine to reference "
        "CVEs, TTPs, or specific attack techniques. Skip basic explanations they'd already know."
    ),
    "Business executives": (
        "Write for a business executive audience (CEOs, boards, non-technical leadership). "
        "Avoid jargon and acronyms unless you define them briefly. Focus on business impact, "
        "risk, and what action (if any) is needed. Keep it concrete and outcome-oriented."
    ),
    "General public": (
        "Write for a general audience with no security background. Explain any technical "
        "concept in plain language using a brief analogy if helpful. Focus on what this means "
        "for them personally or for the organization, not implementation detail."
    ),
}

PLATFORM_GUIDANCE = {
    "LinkedIn": (
        "Write a LinkedIn post, MAXIMUM 900 characters total (count carefully — this is a hard "
        "limit, not a target). 2-3 short paragraphs, professional but conversational tone, "
        "can include 1-2 relevant hashtags at the end (hashtags count toward the limit). "
        "The first sentence must be a hook: a surprising fact, a consequence, or a question — "
        "never a restatement of what the source material is (e.g. never start with 'OpenAI "
        "confirmed...' or 'A new report shows...'). If you can cut a sentence without losing "
        "the core point, cut it."
    ),
    "X": (
        "Write a post for X (Twitter). Maximum 280 characters. Punchy, direct, no fluff. "
        "One clear idea. Hashtags optional and used sparingly."
    ),
    "Executive summary": (
        "Write a 3-4 sentence executive summary suitable for an internal briefing doc or "
        "email to leadership. Lead with the 'so what.' No hashtags, no social-media framing — "
        "this is an internal document, not a public post."
    ),
}


# Hard character caps enforced in code, not just prompted for. None = no cap.
CHAR_LIMITS = {
    "LinkedIn": 900,
    "X": 280,
    "Executive summary": None,
}


def enforce_style(text: str) -> str:
    """Deterministic cleanup the model can't 'forget' to do.

    Prompt instructions alone don't reliably stop em dash usage, so we
    strip them in code instead of hoping the model complies.
    """
    # Em dash -> comma if mid-sentence-ish, otherwise a period. Simple and
    # good enough: replace with ", " and let the reader's eye do the rest.
    text = text.replace(" — ", ", ").replace("—", ", ")
    # Collapse any double spaces/punctuation left behind by the swap.
    text = " ".join(text.split())
    return text.strip()


def build_prompt(source_text: str, platform: str, audience: str) -> str:
    """Construct the generation prompt from source material + platform + audience selections."""
    return f"""You are a senior cybersecurity marketing writer. Turn the source material below into
a single piece of content following the platform and audience instructions exactly.

STYLE RULES (apply to every output, no exceptions):
- Never use an em dash (—) anywhere in the output. Use a period, comma, or parenthesis instead.
- Avoid other obvious AI-writing tells: no "in today's landscape," no "it's not just X, it's Y"
  constructions, no rhetorical-question openers, no rule-of-three lists crammed into one sentence.
- Write like a specific person with a point of view, not a summary engine.

PLATFORM INSTRUCTIONS:
{PLATFORM_GUIDANCE[platform]}

AUDIENCE INSTRUCTIONS:
{AUDIENCE_GUIDANCE[audience]}

SOURCE MATERIAL:
\"\"\"
{source_text}
\"\"\"

Return ONLY the finished post/summary text. No preamble, no explanation, no quotation marks
around the output. Before you finish, re-read your draft and delete any em dash you wrote,
replacing it with a comma or period instead."""


def build_shorten_prompt(draft: str, limit: int) -> str:
    """Follow-up prompt used when the first draft comes back over the character limit."""
    return f"""The draft below is too long. Rewrite it to fit within {limit} characters total
(count carefully, this is a hard limit). Cut sentences and phrases rather than compressing
everything slightly, a shorter piece with fewer ideas reads better than a cramped one with all
of them. Keep the strongest hook and the single most important fact. Do not use an em dash (—)
anywhere.

DRAFT:
\"\"\"
{draft}
\"\"\"

Return ONLY the revised text, nothing else."""
