from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ApiSettings(BaseModel):
    base_url: str = "http://localhost:8080"


class Settings(BaseSettings):
    api: ApiSettings = Field(default_factory=ApiSettings)


settings = Settings()
