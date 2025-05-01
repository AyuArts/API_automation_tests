import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from clients.endpoints import Endpoints
from tests.errors import Errors


class ApiSettings(BaseSettings):
    base_url: str = "https://gorest.co.in"
    token: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        case_sensitive=False,
        env_prefix="APP_CONFIG__",
        env_nested_delimiter="__",
    )

    api: ApiSettings = Field(default_factory=ApiSettings)
    endpoints: Endpoints = Field(default_factory=Endpoints)
    errors: Errors = Field(default_factory=Errors)


settings = Settings()
