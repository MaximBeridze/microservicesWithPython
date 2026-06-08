from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Services available from Module 3
    user_service_url: str = "http://localhost:8001"
    game_service_url: str = "http://localhost:8002"
    activity_service_url: str = "http://localhost:8003"

    # Added in Module 4
    notification_service_url: str = "http://localhost:8004"

    # Added in Module 5
    # logging_service_url: str = "http://localhost:8006"

    # Added in Module 6
    # auth_service_url: str = "http://localhost:8005"
    # secret_key: str = "dev-secret-change-in-production"

    model_config = {"env_file": ".env"}


settings = Settings()
