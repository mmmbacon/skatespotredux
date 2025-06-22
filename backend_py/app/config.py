from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
import os
import boto3


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    JWT_SECRET: str = Field(..., env="JWT_SECRET")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_TOKEN = os.getenv("R2_TOKEN")

def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCOUNT_ID,
        aws_secret_access_key=R2_TOKEN,
        region_name="auto",
    ) 