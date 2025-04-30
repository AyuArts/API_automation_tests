from config import settings
from core.base_clients import BaseClient


class PostClient(BaseClient):
    """
    API client for interacting with Post-related endpoints.
    Provides methods for creating, retrieving, updating, deleting,
    and listing posts via RESTful API.
    """

    def create_post(self, status: int, data: dict):
        """
        Create a new post.

        :param status: Expected HTTP status code.
        :param data: Dictionary with post data.
        :return: Response object.
        """
        return self.post(
            endpoint=settings.endpoints.post.create_post,
            data=data,
            expected_status=status,
        )

    def get_post(self, status: int):
        """
        Retrieve a single post.

        :param status: Expected HTTP status code.
        :return: Response object.
        """
        return self.get(
            endpoint=settings.endpoints.post.get_post,
            expected_status=status,
        )

    def update_post(self, status: int, data: dict):
        """
        Update an existing post.

        :param status: Expected HTTP status code.
        :param data: Dictionary with updated post fields.
        :return: Response object.
        """
        return self.put(
            endpoint=settings.endpoints.post.update_post,
            data=data,
            expected_status=status,
        )

    def delete_post(self, status: int):
        """
        Delete a post.

        :param status: Expected HTTP status code.
        :return: Response object.
        """
        return self.delete(
            endpoint=settings.endpoints.post.delete_post,
            expected_status=status,
        )

    def get_list_posts(self, status: int, params: dict = None):
        """
        Retrieve a list of posts with optional filters.

        :param status: Expected HTTP status code.
        :param params: Optional query parameters (e.g., pagination, user_id).
        :return: Response object.
        """
        return self.get(
            endpoint=settings.endpoints.post.get_list_posts,
            params=params,
            expected_status=status,
        )

    def get_first_post(self, params: dict = None) -> dict:
        """
        Retrieve the first post from the list.

        :param params: Optional filters.
        :return: Parsed JSON dict of the first post.
        """
        return self.get_list_posts(status=200, params=params).json()[0]

    def get_post_id(self, params: dict = None) -> int:
        """
        Get the ID of the first available post.

        :param params: Optional filters.
        :return: Integer post ID.
        """
        return self.get_first_post(params=params)["id"]
