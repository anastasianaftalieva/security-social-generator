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
        "Write a LinkedIn post. 3-5 short paragraphs, professional but conversational tone, "
        "can include 1-2 relevant hashtags at the end. Open with a hook, not a summary. "
        "No more than ~1,300 characters."
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


def build_prompt(source_text: str, platform: str, audience: str) -> str:
    """Construct the generation prompt from source material + platform + audience selections."""
    return f"""You are a senior cybersecurity marketing writer. Turn the source material below into
a single piece of content following the platform and audience instructions exactly.

PLATFORM INSTRUCTIONS:
{PLATFORM_GUIDANCE[platform]}

AUDIENCE INSTRUCTIONS:
{AUDIENCE_GUIDANCE[audience]}

SOURCE MATERIAL:
\"\"\"
{source_text}
\"\"\"

Return ONLY the finished post/summary text. No preamble, no explanation, no quotation marks
around the output."""
