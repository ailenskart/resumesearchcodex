from pydantic import BaseModel, Field


class CandidateCard(BaseModel):
    id: int
    name: str | None
    location: str | None
    years_experience: float | None
    current_title: str | None
    top_skills: list[str]
    drive_link: str | None


class SearchResult(BaseModel):
    candidate: CandidateCard
    score: float
    score_breakdown: dict[str, float]
    why: list[str]
    snippets: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class QueryIntent(BaseModel):
    skills_keywords: list[str] = Field(default_factory=list)
    location: str | None = None
    min_years_experience: float | None = None
    title_intent: list[str] = Field(default_factory=list)
