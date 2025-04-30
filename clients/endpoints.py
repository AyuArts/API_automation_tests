from pydantic import BaseModel, Field


class BaseEndpoints(BaseModel):
    base: str = "public/v2"


class UserEndpoints(BaseEndpoints):
    @property
    def create_user(self) -> str:
        return f"{self.base}/users"

    @property
    def get_list_users(self) -> str:
        return self.create_user

    @property
    def get_user(self) -> str:
        return f"{self.create_user}/{{user_id}}"

    @property
    def update_user(self) -> str:
        return f"{self.create_user}/{{user_id}}"

    @property
    def delete_user(self) -> str:
        return f"{self.create_user}/{{user_id}}"


class PostEndpoints(BaseEndpoints):
    @property
    def create_post(self) -> str:
        return f"{self.base}/post"

    @property
    def get_list_posts(self) -> str:
        return self.create_post

    @property
    def get_post(self) -> str:
        return f"{self.create_post}/{{post_id}}"

    @property
    def update_post(self) -> str:
        return f"{self.create_post}/{{post_id}}"

    @property
    def delete_post(self) -> str:
        return f"{self.create_post}/{{post_id}}"


class Endpoints(BaseModel):
    user: UserEndpoints = Field(default_factory=UserEndpoints)
    post: PostEndpoints = Field(default_factory=PostEndpoints)
