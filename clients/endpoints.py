# endpoints.py
from dataclasses import dataclass
from typing import Final

from pydantic import BaseModel, Field

API_ROOT: Final[str] = "public/v2"


@dataclass(frozen=True, slots=True)
class ResourceURLs:
    """
    Stores CRUD endpoints for a single REST resource.

    >>> user = ResourceURLs("users")
    >>> user.create              # 'public/v2/users'
    >>> user.get                 # 'public/v2/users/{id}'
    >>> user.update              # 'public/v2/users/{id}'
    >>> user.delete              # 'public/v2/users/{id}'
    >>> user.list                # same as .create
    """

    name: str

    @property
    def create(self) -> str:
        return f"{API_ROOT}/{self.name}"

    @property
    def list(self) -> str:
        return self.create

    @property
    def get(self) -> str:
        return f"{self.create}/{{id}}"

    @property
    def update(self) -> str:
        return self.get

    @property
    def delete(self) -> str:
        return self.get


class Endpoints(BaseModel):
    user: ResourceURLs = Field(default_factory=lambda: ResourceURLs("users"))
    post: ResourceURLs = Field(default_factory=lambda: ResourceURLs("posts"))
    comment: ResourceURLs = Field(default_factory=lambda: ResourceURLs("comments"))
