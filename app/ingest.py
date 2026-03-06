import json
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embeddings import embed_text
from app.extraction import extract_text
from app.graph import rebuild_candidate_graph
from app.models import Candidate, CandidateSkill, CandidateTitle
from app.parsing import estimate_years_experience, extract_skills, extract_titles, normalize_location, parse_contact, parse_name

logger = logging.getLogger(__name__)


def upsert_candidate_from_text(
    db: Session,
    *,
    drive_file_id: str,
    drive_link: str | None,
    raw_text: str,
    source_modified: str | None = None,
) -> Candidate:
    candidate = db.scalar(select(Candidate).where(Candidate.drive_file_id == drive_file_id))
    if not candidate:
        candidate = Candidate(drive_file_id=drive_file_id, raw_text=raw_text)
        db.add(candidate)

    contact = parse_contact(raw_text)
    name = parse_name(raw_text)
    skills = extract_skills(raw_text)
    titles = extract_titles(raw_text)

    location = None
    for token in ["gurugram", "gurgaon", "bengaluru", "bangalore", "delhi", "pune", "mumbai"]:
        if token in raw_text.lower():
            location = token
            break

    candidate.drive_link = drive_link
    candidate.full_name = name
    candidate.email = contact["email"]
    candidate.phone = contact["phone"]
    candidate.location = location
    candidate.normalized_location = normalize_location(location)
    candidate.years_experience = estimate_years_experience(raw_text)
    candidate.current_title = titles[0] if titles else None
    candidate.raw_text = raw_text
    candidate.snippet_text = "\n".join(raw_text.splitlines()[:20])
    candidate.embedding_json = json.dumps(embed_text(raw_text[:4000]))
    candidate.updated_at = datetime.utcnow()

    candidate.skills.clear()
    candidate.titles.clear()
    for s in skills:
        candidate.skills.append(CandidateSkill(skill=s))
    for t in titles:
        candidate.titles.append(CandidateTitle(title=t))

    db.flush()
    rebuild_candidate_graph(db, candidate)
    logger.info("Upserted candidate from file=%s modified=%s", drive_file_id, source_modified)
    return candidate


def ingest_drive_files(db: Session, drive_files) -> dict[str, int]:
    seen = set()
    inserted = 0
    for f in drive_files:
        seen.add(f.file_id)
        if not f.local_path:
            logger.warning("Skipping non-local file in MVP downloader-less mode: %s", f.file_id)
            continue
        text = extract_text(f.local_path)
        upsert_candidate_from_text(
            db,
            drive_file_id=f.file_id,
            drive_link=f.web_view_link,
            raw_text=text,
            source_modified=f.modified_time,
        )
        inserted += 1

    existing = db.scalars(select(Candidate.drive_file_id)).all()
    deleted = 0
    for file_id in existing:
        if file_id not in seen:
            c = db.scalar(select(Candidate).where(Candidate.drive_file_id == file_id))
            if c:
                db.delete(c)
                deleted += 1

    db.commit()
    return {"upserted": inserted, "deleted": deleted}
