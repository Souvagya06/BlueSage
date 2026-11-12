"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "waterbody_db"
    postgres_user: str = "waterbody_user"
    postgres_password: str = "waterbody_pass_2024"

    # App
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    secret_key: str = "change_me"

    # External
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

