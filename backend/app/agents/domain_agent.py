from __future__ import annotations

from ..config import settings

DOMAIN_KEYWORDS = {
    "Digital Assets": ["digital asset", "token", "crypto", "stablecoin", "defi", "blockchain"],
    "Private Capital": ["private equity", "private capital", "portfolio company", "fund", "lp", "gp"],
    "Technology & Modernization": ["modernization", "core transformation", "cloud", "platform", "architecture", "operating model"],
    "Quantum Technologies": ["quantum", "post-quantum", "qkd", "quantum-safe"],
    "Data & AI": ["ai", "machine learning", "genai", "analytics", "data strategy", "llm"]
}


def classify_domain(text: str) -> tuple[str, float]:
    normalized = text.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return domain, 0.82
    return "Other", 0.55
