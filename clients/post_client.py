from clients.crud_client import CRUDClient


class PostClient(CRUDClient):
    ENDPOINT_NAME = "post"

    def first_user_id(self, params: dict | None = None) -> int:
        return self.first(params=params)["user_id"]
