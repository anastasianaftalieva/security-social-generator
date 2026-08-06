# Security Social Post Generator

_A small AI tool that turns security news into audience-tuned social content — LinkedIn, X, and executive-summary formats — for security teams and marketers who cover them._

> 🚧 Work in progress — Day 1 of a 7-day build. See commit history for the progression.

## Problem

Security marketers and comms teams constantly need to translate the same source
material (a CISA alert, a vendor blog post, a product announcement) into different
formats for different audiences — a LinkedIn post for practitioners reads nothing
like an executive briefing. Doing this by hand for every piece of news is slow.

## Solution

Paste in source text, pick a platform and an audience, and get back a
ready-to-use draft tuned to both.

## Architecture

- **Streamlit** for the UI
- **Anthropic API (Claude)** for generation
- Prompt templates in `prompts.py` separate platform and audience instructions,
  so tone and structure can be tuned independently

## Screenshots / Demo

_(coming — added once the UI is polished, Day 4)_

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...
streamlit run app.py
```

## Roadmap

- [ ] Audience-aware tone controls (Day 3)
- [ ] UI polish + copy button (Day 4)
- [ ] Tested against real CISA alerts / vendor posts (Day 5)
- [ ] Public deploy (Day 6)
- [ ] Demo GIF + lessons learned (Day 7)

## Lessons learned (Day 1)

- **Prompt instructions aren't reliable for hard constraints.** Telling the model "never use an em dash" and "stay under 900 characters" wasn't enough, it violated both repeatedly. The fix was enforcing them in code: stripping em dashes with a deterministic string replace, and adding an automatic "shorten this" follow-up call when the model overshoots the character limit. Lesson: prompting sets intent, code enforces rules.
- **Testing against real source material surfaces problems placeholder text never would.** The character limit and em-dash issues only showed up once I ran the generator against an actual breaking-news security incident, not a made-up example. Real content is messier and pushes the model toward its default habits.
- **Verify before you publish.** Before trusting an AI-generated summary of a security incident, I checked the model's output against the original source article.
