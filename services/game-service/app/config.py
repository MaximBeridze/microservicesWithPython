from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./games.db"
    redis_url: str = "redis://localhost:6379"

    # Added in Module 6 — must match SECRET_KEY in auth-service
    auth_secret_key: str = "dev-secret-change-in-production"

    model_config = {"env_file": ".env"}


settings = Settings()
