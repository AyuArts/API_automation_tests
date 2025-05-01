from clients.crud_client import CRUDClient


class UserClient(CRUDClient):
    ENDPOINT_NAME = "user"

    def first_email(self) -> str:
        return self.first()["email"]
