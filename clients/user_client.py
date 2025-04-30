from config import settings
from core.base_clients import BaseClient


class UserClient(BaseClient):
    """
    API client for interacting with User-related endpoints.
    Inherits common HTTP methods from BaseClient.
    """

    def create_user(self, data: dict, status: int):
        """
        Create a new user via API.

        :param data: User data to be sent in the request body.
        :param status: Expected HTTP response status code.
        :return: Response object from the POST request.
        """
        return self.post(
            endpoint=settings.endpoints.user.create_user,
            data=data,
            expected_status=status,
        )

    def get_list_users(self, status: int, params: dict = None):
        """
        Retrieve a list of users.

        :param status: Expected HTTP response status code.
        :param params: Optional query parameters for filtering users.
        :return: Response object from the GET request.
        """
        return self.get(
            endpoint=settings.endpoints.user.get_list_users,
            expected_status=status,
            params=params,
        )

    def get_user(self, user_id: int, status: int):
        """
        Retrieve a user by ID.

        :param user_id: ID of the user to retrieve.
        :param status: Expected HTTP response status code.
        :return: Response object from the GET request.
        """
        return self.get(
            endpoint=settings.endpoints.user.get_user.format(user_id=user_id),
            expected_status=status,
        )

    def get_first_user(self) -> dict:
        """
        Retrieve the first user from the list.

        :return: Parsed JSON of the first user object.
        """
        return self.get_list_users(status=200).json()[0]

    def get_user_id(self) -> int:
        """
        Retrieve the ID of the first user.

        :return: User ID as an integer.
        """
        return self.get_first_user()["id"]

    def get_user_email(self) -> str:
        """
        Retrieve the email of the first user.

        :return: User email as a string.
        """
        return self.get_first_user()["email"]

    def delete_user(self, user_id: int, status: int):
        """
        Delete a user by ID.

        :param user_id: ID of the user to delete.
        :param status: Expected HTTP response status code.
        :return: Response object from the DELETE request.
        """
        return self.delete(
            endpoint=settings.endpoints.user.delete_user.format(user_id=user_id),
            expected_status=status,
        )

    def update_user(self, user_id: int, data: dict, status: int):
        """
        Update an existing user by ID.

        :param user_id: ID of the user to update.
        :param data: Dictionary with updated user fields.
        :param status: Expected HTTP response status code.
        :return: Response object from the PUT request.
        """
        return self.put(
            endpoint=settings.endpoints.user.update_user.format(user_id=user_id),
            data=data,
            expected_status=status,
        )
