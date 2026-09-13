from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    agent_host: str = "127.0.0.1"
    agent_port: int = 8000
    model_provider: str = "local"
    model_name: str = "local-grounded"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://127.0.0.1:11434"
    postgres_url: str = "postgresql+asyncpg://nexus:nexus@localhost:5432/nexus"
    chroma_url: str = "http://localhost:8001"
    chroma_collection: str = "nexus_documents"
    checkpoint_db: str = "./.data/checkpoints.db"
    max_agent_iterations: int = 3
    max_context_chars: int = 12000
    request_timeout_seconds: int = 30
    cors_origins: str = "http://127.0.0.1:8080,http://localhost:8080"
    mcp_allowed_tools: str = "local_search,entity_lookup"
    max_question_length: int = 4000
    log_level: str = "INFO"
    enable_docs: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_runtime_dirs(self) -> None:
        Path(self.checkpoint_db).parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_runtime_dirs()
    return settings
