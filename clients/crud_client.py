from config import settings
from core.base_clients import BaseClient


class CRUDClient(BaseClient):
    """
    Generic CRUD client. Requires setting `ENDPOINT_NAME` in subclasses.
    """

    ENDPOINT_NAME: str = ""

    @property
    def ep(self):
        return getattr(settings.endpoints, self.ENDPOINT_NAME)

    def create_obj(self, *, data: dict, status: int = 201):
        return self.post(endpoint=self.ep.create, data=data, expected_status=status)

    def get_obj(self, obj_id: int, *, status: int = 200):
        return self.get(endpoint=self.ep.get.format(id=obj_id), expected_status=status)

    def update_obj(self, obj_id: int, *, data: dict, status: int = 200):
        return self.put(
            endpoint=self.ep.update.format(id=obj_id), data=data, expected_status=status
        )

    def delete_obj(self, obj_id: int, *, status: int = 204):
        return self.delete(
            endpoint=self.ep.delete.format(id=obj_id), expected_status=status
        )

    def get_list_objs(self, *, params: dict | None = None, status: int = 200):
        return self.get(endpoint=self.ep.list, params=params, expected_status=status)

    def first(self, params: dict | None = None) -> dict:
        return self.get_list_objs(params=params).json()[0]

    def first_id(self, params: dict | None = None) -> int:
        return self.first(params=params)["id"]
