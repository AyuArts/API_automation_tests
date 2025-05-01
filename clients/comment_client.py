from clients.crud_client import CRUDClient


class CommentClient(CRUDClient):
    ENDPOINT_NAME = "comment"
