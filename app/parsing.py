import re
from datetime import datetime

KNOWN_SKILLS = {
    "python", "java", "sql", "aws", "docker", "kubernetes", "react", "node", "fastapi", "ml", "ai"
}
LOCATION_SYNONYMS = {
    "gurugram": "gurugram",
    "gurgaon": "gurugram",
    "bangalore": "bengaluru",
    "bengaluru": "bengaluru",
}
TECH_TITLE_HINTS = ["software", "engineer", "developer", "tech", "architect", "backend", "frontend"]


def normalize_location(text: str | None) -> str | None:
    if not text:
        return None
    lower = text.strip().lower()
    return LOCATION_SYNONYMS.get(lower, lower)


def parse_contact(text: str) -> dict[str, str | None]:
    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.search(r"(?:\+?\d{1,3}[-. ]?)?(?:\(?\d{3}\)?[-. ]?)?\d{3}[-. ]?\d{4}", text)
    return {"email": email.group(0) if email else None, "phone": phone.group(0) if phone else None}


def parse_name(text: str) -> str | None:
    first_line = text.strip().splitlines()[0] if text.strip() else ""
    if 1 < len(first_line.split()) <= 4:
        return first_line.strip()
    return None


def estimate_years_experience(text: str) -> float | None:
    explicit = re.search(r"(\d{1,2})\+?\s*(?:years|yrs)", text.lower())
    if explicit:
        return float(explicit.group(1))

    years = [int(y) for y in re.findall(r"(20\d{2})", text)]
    if years:
        current = datetime.utcnow().year
        earliest = min(years)
        if 1990 < earliest <= current:
            return float(max(0, current - earliest))
    return None


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    return sorted({s for s in KNOWN_SKILLS if re.search(rf"\b{re.escape(s)}\b", text_lower)})


def extract_titles(text: str) -> list[str]:
    titles = []
    for line in text.splitlines():
        l = line.lower().strip()
        if any(h in l for h in TECH_TITLE_HINTS) and len(l) < 120:
            titles.append(line.strip())
    return titles[:8]
