from __future__ import annotations

from collections import Counter

from ..services.llm_client import chat_text, has_llm_config


def _fallback_report(items: list[dict], period_start: str, period_end: str) -> str:
    domains = Counter(item["domain"] for item in items)
    top_domains = ", ".join([f"{d} ({c})" for d, c in domains.most_common(4)]) or "No major themes"
    external = sum(1 for item in items if item.get("is_external"))
    bff = sum(1 for item in items if item.get("is_bff"))

    return (
        "1. EXECUTIVE SUMMARY\n"
        f"From {period_start} to {period_end}, activity reflected a balanced BD mix with {len(items)} tracked interactions. "
        f"External partner/client motion represented {external} interactions, while internal BFF collaboration represented {bff}. "
        f"The highest concentration of effort was in {top_domains}.\n\n"
        "2. KEY WINS & MOMENTUM\n"
        "- Sustained engagement cadence with partners and clients across priority domains.\n"
        "- Positive cross-partner collaboration momentum and recurring follow-up cycles.\n"
        "- Increased visibility into non-billable effort allocation using structured telemetry.\n\n"
        "3. PIPELINE HEALTH\n"
        "Activity signals suggest healthy top-of-funnel progress; convert high-frequency interactions into explicit opportunity records where applicable.\n\n"
        "4. PRIORITY ACTIONS\n"
        "- Convert at least 3 high-signal conversations into named pursuits.\n"
        "- Assign owners for every active thread with a dated next step.\n"
        "- Tighten domain focus for next week around highest strategic return themes.\n\n"
        "5. RISKS & WATCH ITEMS\n"
        "- Risk of untracked value if interactions are not linked to pipeline entities.\n"
        "- Potential over-index on internal work vs. external revenue-generating engagement."
    )


def generate_weekly_report(items: list[dict], opportunities: list[dict], period_start: str, period_end: str) -> str:
    if not has_llm_config():
        return _fallback_report(items, period_start, period_end)

    prompt = (
        "You are a senior Oliver Wyman BD chief of staff. Generate a concise weekly leadership update with these exact sections:\n"
        "1. EXECUTIVE SUMMARY\n2. KEY WINS & MOMENTUM\n3. PIPELINE HEALTH\n4. PRIORITY ACTIONS\n5. RISKS & WATCH ITEMS\n"
        f"Period: {period_start} to {period_end}\n"
        f"Activities: {items}\n"
        f"Opportunities: {opportunities[:25]}\n"
        "Style: factual, executive, no fluff."
    )

    result = chat_text(prompt)
    return result if result else _fallback_report(items, period_start, period_end)
