from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "local"
    database_url: str = "postgresql+asyncpg://asila:asila@localhost:5432/asila"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")


settings = Settings()
