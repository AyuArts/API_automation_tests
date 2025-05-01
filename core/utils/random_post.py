from typing import Optional, Union

from faker import Faker


class RandomPost:
    """
    Utility class for generating random post data for API testing.
    Supports both valid and intentionally invalid payloads.
    """

    def __init__(self):
        """
        Initializes a Faker instance for generating random text data.
        """
        self._fake = Faker()

    @property
    def title(self) -> str:
        """
        :return: Randomly generated post title.
        """
        return self._fake.sentence(nb_words=6)

    @property
    def title_empty(self) -> str:
        return ""

    @property
    def title_too_long(self) -> str:
        return "A" * 300

    @property
    def title_none(self) -> None:
        return None

    @property
    def body(self) -> str:
        """
        :return: Randomly generated post body text.
        """
        return self._fake.text(max_nb_chars=200)

    def build_post(self, user_id: int, title: Union[str, int, None]) -> dict:
        """
        Constructs a post dictionary.

        :param user_id: ID of the user associated with the post.
        :param title: Title value to insert (can be valid or invalid).
        :return: Dictionary representing a post payload.
        """
        return {
            "user_id": user_id,
            "title": title,
            "body": self.body,
        }

    def valid_post(self, user_id: int) -> dict:
        """
        Generates a valid post.

        :param user_id: ID of the user creating the post.
        :return: Valid post dictionary.
        """
        return self.build_post(user_id, self.title)

    def invalid_post(self, user_id: int, error_type: str = "empty") -> dict:
        """
        Generates an invalid post with various types of title errors.

        :param user_id: ID of the user creating the post.
        :param error_type: Type of invalid title:
                           - "empty": empty string
                           - "too_long": over character limit
                           - "none": null value
                           - "numeric": numeric value
        :return: Invalid post dictionary.
        :raises ValueError: If an unknown error_type is passed.
        """
        if error_type == "empty":
            title = self.title_empty
        elif error_type == "too_long":
            title = self.title_too_long
        elif error_type == "none":
            title = self.title_none
        else:
            raise ValueError(f"Unknown error_type: {error_type}")

        return self.build_post(user_id, title)

    def __call__(
            self,
            user_id: int,
            invalid_title: bool = False,
            title_error: Optional[str] = None,
    ) -> dict:
        """
        Callable shortcut to generate either a valid or invalid post.

        This allows the object to be used as a function for flexible test data generation.

        :param user_id: ID of the user creating the post.
        :param invalid_title: Whether to generate a post with invalid title.
        :param title_error: Type of title error to simulate.
                            Options:
                            - "empty": Empty string as title.
                            - "too_long": Excessively long title (300+ chars).
                            - "none": Null value for title.
        :return: Dictionary representing the generated post payload.

        Examples:
            >>> post_gen = RandomPost()

            # Valid post
            >>> post_gen(user_id=1)
            {'user_id': 1, 'title': 'Example Title', 'body': 'Generated text...'}

            # Invalid post — empty title
            >>> post_gen(user_id=1, invalid_title=True, title_error="empty")
            {'user_id': 1, 'title': '', 'body': '...'}

            # Invalid post — too long title
            >>> post_gen(user_id=1, invalid_title=True, title_error="too_long")
            {'user_id': 1, 'title': 'AAAAA... (300+ chars)', 'body': '...'}

            # Invalid post — None as title
            >>> post_gen(user_id=1, invalid_title=True, title_error="none")
            {'user_id': 1, 'title': None, 'body': '...'}
        """
        if invalid_title:
            return self.invalid_post(user_id, title_error or "empty")
        return self.valid_post(user_id)


post_gen: RandomPost = RandomPost()
