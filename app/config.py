from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Resume Search Engine"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/resumes"
    drive_folder_id: str = "[DRIVE_FOLDER_ID]"
    drive_auth_method: str = "SERVICE_ACCOUNT"
    google_service_account_file: str | None = None
    embedding_provider: str = "LOCAL_SENTENCE_TRANSFORMERS"
    embedding_dimension: int = 384
    vector_backend: str = "PGVECTOR"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
