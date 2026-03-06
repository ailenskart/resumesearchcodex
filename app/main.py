from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.db import Base, engine, get_db
from app.drive_sync import LocalFolderDriveClient
from app.ingest import ingest_drive_files
from app.logging_utils import configure_logging
from app.models import Candidate
from app.schemas import CandidateCard
from app.search import search_candidates

configure_logging(settings.log_level)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/sync")
def sync(local_folder: str = Query(default="sample_data"), db: Session = Depends(get_db)):
    client = LocalFolderDriveClient(local_folder)
    stats = ingest_drive_files(db, client.list_files())
    return {"status": "ok", **stats}


@app.get("/search")
def search(q: str, limit: int = 20, db: Session = Depends(get_db)):
    return search_candidates(db, q, limit)


@app.get("/candidates/{candidate_id}")
def candidate_profile(candidate_id: int, db: Session = Depends(get_db)):
    c = db.scalar(
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .options(selectinload(Candidate.skills), selectinload(Candidate.titles))
    )
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return {
        "card": CandidateCard(
            id=c.id,
            name=c.full_name,
            location=c.normalized_location,
            years_experience=c.years_experience,
            current_title=c.current_title,
            top_skills=sorted({s.skill for s in c.skills}),
            drive_link=c.drive_link,
        ),
        "titles": [t.title for t in c.titles],
        "snippet": c.snippet_text,
    }
