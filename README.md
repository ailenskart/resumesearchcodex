# Resume People Search Engine (Drive -> Graph + Hybrid Search)

MVP people-search engine over resumes with prebuilt indexes (no query-time full-scan), explainable ranking, and incremental sync.

## Stack choices
- **API**: FastAPI
- **Storage**: PostgreSQL
- **Vector**: pluggable; MVP stores embeddings in DB JSON (production: pgvector)
- **Keyword**: SQL + lightweight keyword score (production: Postgres FTS)
- **Graph backend**: relational graph edges in Postgres (`graph_edges`)
- **Ingestion**: sync endpoint suitable for cron/worker trigger

## Quick start
1. Start services:
   ```bash
   docker compose up -d
   ```
2. Generate sample data:
   ```bash
   docker compose exec api python scripts/generate_sample_data.py
   ```
3. Sync resumes:
   ```bash
   curl -X POST "http://localhost:8000/sync?local_folder=sample_data"
   ```
4. Search:
   ```bash
   curl "http://localhost:8000/search?q=tech%20guy%20based%20out%20of%20Gurugram%20with%20more%20than%205%20years%20of%20experience"
   ```
5. CLI demo:
   ```bash
   python scripts/demo_cli.py --query "tech guy based out of Gurugram with more than 5 years of experience"
   ```

## Environment variables
- `DATABASE_URL` (default Postgres in compose)
- `DRIVE_FOLDER_ID=[DRIVE_FOLDER_ID]`
- `DRIVE_AUTH_METHOD=[SERVICE_ACCOUNT or OAUTH]`
- `GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/key.json`
- `EMBEDDING_PROVIDER=[LOCAL_SENTENCE_TRANSFORMERS or HOSTED]`
- `VECTOR_BACKEND=[PGVECTOR or QDRANT]`

## Google Drive integration
- `GoogleDriveClient` is included for service-account listing.
- MVP `/sync` path currently uses local folder adapter for deterministic local demo.
- Production extension: implement Drive file download stream and Drive Changes API webhook worker.

## Endpoints
- `POST /sync?local_folder=sample_data`
- `POST /demo/bootstrap` (seed fake resumes + ingest for instant web demo)
- `GET /search?q=...&limit=20`
- `GET /candidates/{id}`
- `GET /health`

## Testing
```bash
pytest -q
```

## Notes on privacy
- Log redaction masks email and phone patterns.
- API response only returns snippets and structured fields (not full raw resume by default).


## Try it locally (fast path)
```bash
docker compose up -d
curl -X POST "http://localhost:8000/sync?local_folder=sample_data"
curl "http://localhost:8000/search?q=tech%20guy%20based%20out%20of%20Gurugram%20with%20more%20than%205%20years%20of%20experience"
```

## Can you host this?
I can’t directly host a long-running production service from this chat environment, but I added deployment scaffolding so you can host it in minutes.

### Option 1: Render (easiest)
1. Push this repo to GitHub.
2. In Render, choose **New + > Blueprint** and point to your repo.
3. Render will read `render.yaml`, create:
   - one web service (`resumesearch-api`)
   - one Postgres database (`resumesearch-db`)
4. Set `DRIVE_FOLDER_ID` and (if using real Drive) mount/provide your `GOOGLE_SERVICE_ACCOUNT_FILE` secret.
5. Deploy and open `/health` to verify service is up.
6. Call `POST /demo/bootstrap` once to seed fake resumes in the container and index them.
7. Run `/search?q=tech%20guy%20based%20out%20of%20Gurugram%20with%20more%20than%205%20years%20of%20experience`.

### Option 2: Any Docker host (Railway/Fly.io/VM/K8s)
```bash
docker build -t resumesearch-api .
docker run -p 8000:8000   -e DATABASE_URL=<postgres-url>   -e DRIVE_FOLDER_ID=<drive-folder-id>   -e DRIVE_AUTH_METHOD=SERVICE_ACCOUNT   -e EMBEDDING_PROVIDER=LOCAL_SENTENCE_TRANSFORMERS   resumesearch-api
```

### Important production note
Current `/sync` uses the local-folder adapter for deterministic demo. For real Google Drive hosting, wire `GoogleDriveClient` to file download + changes feed (already outlined in `docs/system_design.md`).


### Quick public web test after deploy
```bash
curl "https://<your-render-domain>/health"
curl -X POST "https://<your-render-domain>/demo/bootstrap"
curl "https://<your-render-domain>/search?q=tech%20guy%20based%20out%20of%20Gurugram%20with%20more%20than%205%20years%20of%20experience"
```
