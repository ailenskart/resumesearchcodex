import json
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.embeddings import cosine_similarity, embed_text
from app.models import Candidate
from app.schemas import CandidateCard, SearchResponse, SearchResult
from app.query import RankingWeights, parse_query


def _keyword_score(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    t = text.lower()
    hits = sum(1 for k in keywords if k in t)
    return hits / len(keywords)


def search_candidates(db: Session, query: str, limit: int = 20, weights: RankingWeights | None = None) -> SearchResponse:
    weights = weights or RankingWeights()
    intent = parse_query(query)

    stmt = select(Candidate).options(selectinload(Candidate.skills), selectinload(Candidate.titles))
    if intent.location:
        stmt = stmt.where(Candidate.normalized_location == intent.location)
    if intent.min_years_experience is not None:
        stmt = stmt.where(Candidate.years_experience.is_not(None), Candidate.years_experience >= intent.min_years_experience)

    candidates = db.scalars(stmt).all()
    if not candidates:
        candidates = db.scalars(select(Candidate).options(selectinload(Candidate.skills), selectinload(Candidate.titles))).all()

    query_vec = embed_text(query)
    results = []
    for c in candidates:
        skill_set = {s.skill.lower() for s in c.skills}
        skill_match = len(skill_set.intersection(intent.skills_keywords)) / max(1, len(intent.skills_keywords))
        title_text = " ".join(t.title.lower() for t in c.titles)
        title_match = _keyword_score(title_text, intent.title_intent)
        if intent.min_years_experience is None or c.years_experience is None:
            experience_match = 0.5
        else:
            experience_match = min(1.0, c.years_experience / max(intent.min_years_experience, 1.0))
        location_match = 1.0 if intent.location and c.normalized_location == intent.location else 0.4
        vec = json.loads(c.embedding_json) if c.embedding_json else []
        vector_match = cosine_similarity(query_vec, vec) if vec else 0.0
        keyword_match = _keyword_score(c.raw_text, intent.skills_keywords)

        breakdown = {
            "skill": round(weights.skill * skill_match, 4),
            "title": round(weights.title * title_match, 4),
            "experience": round(weights.experience * experience_match, 4),
            "location": round(weights.location * location_match, 4),
            "vector": round(weights.vector * vector_match, 4),
            "keyword": round(weights.keyword * keyword_match, 4),
        }
        total = round(sum(breakdown.values()), 4)

        why = []
        matched_skills = sorted(skill_set.intersection(intent.skills_keywords))
        if matched_skills:
            why.append(f"Matched skills: {', '.join(matched_skills)}")
        if c.current_title:
            why.append(f"Current/parsed title evidence: {c.current_title}")
        if c.years_experience is not None:
            why.append(f"Estimated experience: {c.years_experience} years")
        if c.location:
            why.append(f"Location evidence: {c.location} (normalized to {c.normalized_location})")

        snippets = [line for line in (c.snippet_text or "").splitlines() if any(k in line.lower() for k in intent.skills_keywords[:5])][:3]

        results.append(
            SearchResult(
                candidate=CandidateCard(
                    id=c.id,
                    name=c.full_name,
                    location=c.normalized_location,
                    years_experience=c.years_experience,
                    current_title=c.current_title,
                    top_skills=sorted(skill_set)[:8],
                    drive_link=c.drive_link,
                ),
                score=total,
                score_breakdown=breakdown,
                why=why,
                snippets=snippets,
            )
        )

    results.sort(key=lambda r: r.score, reverse=True)
    return SearchResponse(query=query, results=results[:limit])
