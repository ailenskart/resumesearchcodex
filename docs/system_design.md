# Resume People Search Engine – System Design

## Overview
MVP pipeline:
1. `POST /sync` polls a Google Drive folder (MVP uses local-folder adapter for offline demo).
2. Resume files are text-extracted (PDF/DOCX/TXT; DOC skipped with warning).
3. Structured parser extracts identity, location, experience estimate, titles, and skills.
4. Candidate metadata is stored in PostgreSQL; embedding vectors are stored per candidate.
5. Graph edges are materialized in relational graph tables (`graph_edges`) to preserve explainability.
6. `GET /search?q=...` runs hybrid retrieval (filters + keyword + vector) and weighted ranking.

## ASCII Architecture
```text
Google Drive / Local Folder
          |
          v
     Sync Worker (/sync)
          |
          v
  Extraction + Parsing + Embedding
          |
          +--> Postgres candidates + skills + titles
          |
          +--> Graph edges table (candidate->skill/title/location)

User Query --> Query Parser --> Hybrid Retrieval --> Weighted Ranker --> Explanations + snippets
```

## Data Model
- `candidates`: file metadata, structured fields, raw text (access-controlled), snippets, embedding payload.
- `candidate_skills`: normalized extracted skills.
- `candidate_titles`: extracted role/title history.
- `graph_edges`: explainability graph edges.

## Indexing Strategy
- B-tree indexes: drive file id, normalized location, years experience.
- Skill/title indexes for keyword retrieval.
- Embeddings persisted in `embedding_json` for MVP portability; production path upgrades to pgvector column + ivfflat/hnsw.

## Ranking Strategy
Final score is weighted sum of:
- skill overlap
- title intent match
- experience closeness
- location match
- vector similarity
- keyword relevance

Weights are configurable in `RankingWeights`.

## Explainability Strategy
Each result includes:
- `score_breakdown` by component
- `why` list grounded in extracted fields
- matched snippets from resume text
- graph-backed relationship evidence (`HAS_SKILL`, `HELD_TITLE`, `LOCATED_IN`)

## Privacy & Security
- PII redaction filter for logs (email/phone masking).
- No full-resume forwarding to LLMs; query-only interpretation if LLM parser is added later.
- Raw resume text kept in DB only; API exposes only snippets by default.
- Service account scope is read-only for Drive ingestion.

## Incremental Sync
MVP:
- periodic polling via `/sync`.
- upsert by `drive_file_id`; delete candidates absent from latest listing.

Production path:
- Drive Changes API + push notifications.
- ingest queue (Celery/Redis) with file-level retries and dedupe by modifiedTime/checksum.

## Production Hardening Path
- Replace JSON embeddings with pgvector and ANN indexes.
- Add Postgres FTS (`tsvector`) for BM25-like retrieval.
- Worker queue with concurrency controls and observability metrics.
- Multi-tenant org scoping and row-level security.
- AuthN/AuthZ for candidate profile access.
