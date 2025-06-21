from functools import lru_cache
from pydantic import BaseSettings, AnyUrl, Field


class Settings(BaseSettings):
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    jwt_secret: str = Field(..., env="JWT_SECRET")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings() 