from .config import Settings


def validate_settings(settings: Settings) -> list[str]:
    warnings: list[str] = []
    if settings.app_env == "production" and settings.cors_origins == "*":
        warnings.append("wildcard CORS is unsafe in production")
    if settings.model_provider == "local":
        warnings.append("local provider is deterministic and not a semantic LLM")
    if settings.checkpoint_db.startswith("./") and settings.app_env == "production":
        warnings.append("relative SQLite checkpoint path is not durable in production")
    return warnings
