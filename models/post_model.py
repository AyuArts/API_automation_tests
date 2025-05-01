from pydantic import BaseModel


class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    body: str


class PostRequest(BaseModel):
    user_id: int
    title: str
    body: str
