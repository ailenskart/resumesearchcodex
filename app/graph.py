from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import Candidate, GraphEdge


def rebuild_candidate_graph(db: Session, candidate: Candidate) -> None:
    db.execute(delete(GraphEdge).where(GraphEdge.source_type == "candidate", GraphEdge.source_id == str(candidate.id)))

    for skill in candidate.skills:
        db.add(
            GraphEdge(
                source_type="candidate",
                source_id=str(candidate.id),
                relation="HAS_SKILL",
                target_type="skill",
                target_id=skill.skill.lower(),
                evidence=f"Skill extracted: {skill.skill}",
            )
        )

    for title in candidate.titles:
        db.add(
            GraphEdge(
                source_type="candidate",
                source_id=str(candidate.id),
                relation="HELD_TITLE",
                target_type="title",
                target_id=title.title.lower()[:120],
                evidence=f"Title extracted: {title.title}",
            )
        )

    if candidate.normalized_location:
        db.add(
            GraphEdge(
                source_type="candidate",
                source_id=str(candidate.id),
                relation="LOCATED_IN",
                target_type="location",
                target_id=candidate.normalized_location,
                evidence=f"Location normalized from {candidate.location}",
            )
        )
