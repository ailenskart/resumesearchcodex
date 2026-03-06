import re
from dataclasses import dataclass, field

from app.parsing import LOCATION_SYNONYMS


@dataclass
class QueryIntent:
    skills_keywords: list[str] = field(default_factory=list)
    location: str | None = None
    min_years_experience: float | None = None
    title_intent: list[str] = field(default_factory=list)


@dataclass
class RankingWeights:
    skill: float = 0.25
    title: float = 0.15
    experience: float = 0.2
    location: float = 0.15
    vector: float = 0.15
    keyword: float = 0.1


def parse_query(query: str) -> QueryIntent:
    q = query.lower()
    years = None
    ymatch = re.search(r"(?:more than|over|>|at least)?\s*(\d+)\s*(?:years|yrs)", q)
    if ymatch:
        years = float(ymatch.group(1))

    location = None
    for k, v in LOCATION_SYNONYMS.items():
        if k in q:
            location = v
            break

    tech_map = {
        "tech guy": ["software engineer", "developer", "engineering"],
        "backend": ["backend engineer", "python", "api"],
    }
    title_intent = []
    for key, vals in tech_map.items():
        if key in q:
            title_intent.extend(vals)

    skills_keywords = re.findall(r"[a-zA-Z]{3,}", q)
    return QueryIntent(
        skills_keywords=sorted(set(skills_keywords)),
        location=location,
        min_years_experience=years,
        title_intent=sorted(set(title_intent)),
    )
