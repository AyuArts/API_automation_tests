import allure
import pytest

from clients.post_client import PostClient
from clients.user_client import UserClient
from config import settings
from core.base_test import BaseTest
from core.logger import Logger
from core.utils import post_gen, CommonError
from models.post_model import PostResponse, PostRequest

log = Logger().get_logger("Test_PostClient")


@allure.feature("Post API")
class TestPostClient(BaseTest):
    """
    TestPostClient

    This test suite verifies the correctness and reliability of the Post API by testing the following functionalities:

    - Creating posts with valid and invalid data
    - Updating existing posts and validating updates
    - Fetching individual posts by ID
    - Filtering lists of posts by user_id and pagination (per_page)
    - Deleting posts and verifying they are no longer accessible

    Each test includes:
    - Allure step-by-step reporting for clarity in execution flow
    - Pydantic model validation to ensure response structure correctness
    - Dynamic logging for debugging
    """

    @pytest.fixture(autouse=True)
    def setup(self, _init_context):
        self.post = PostClient(self.request_context)
        self.user = UserClient(self.request_context)
        self.user_id = self.user.get_user_id()
        self.post_id = self.post.get_post_id()
        self.user_id_with_posts = self.post.get_user_id_with_posts()

    @allure.title("Create a post with valid data")
    @allure.story("Positive: Successfully create a post")
    def test_create_post_valid(self):
        """
        Test the creation of a post with valid input.

        Steps:
        1. Generate valid post data.
        2. Send a POST request.
        3. Assert the response using PostResponse model.
        """
        with allure.step("Step 1: Generate valid post data"):
            data_valid = dict(PostRequest(**post_gen(parent_id=self.user_id)))
        with allure.step("Step 2: Create a post"):
            response = self.post.create_post(data=data_valid, status=201)
        with allure.step("Step 3: Validate response model"):
            assert PostResponse(**response.json())

    @allure.title("Fail to create post with invalid title")
    @allure.story("Negative: Title validation scenarios")
    @pytest.mark.parametrize(
        "title_error, expected_message",
        [
            pytest.param(
                CommonError.EMPTY, settings.errors.text.none, id="title empty"
            ),
            pytest.param(
                CommonError.TOO_LONG, settings.errors.text.too_long, id="title too long"
            ),
            pytest.param(CommonError.NONE, settings.errors.text.none, id="title none"),
        ],
    )
    def test_create_post_invalid_title(self, title_error, expected_message):
        """
        Test post creation with various invalid titles.

        Steps:
        1. Generate post data with invalid title.
        2. Send a POST request.
        3. Assert the response contains proper validation error for title.
        """
        with allure.step(
                f"Step 1: Generate post with invalid title: {title_error.name}"
        ):
            data = post_gen(
                parent_id=self.user_id, invalid=True, error_type=title_error
            )
        with allure.step("Step 2: Try to create post"):
            response = self.post.create_post(data=data, status=422)
        with allure.step("Step 3: Check error message"):
            errors = response.json()
            assert any(
                e["field"] == "title" and e["message"] == expected_message
                for e in errors
            )

    @allure.title("Retrieve a single post by ID")
    @allure.story("Positive: Fetch post by ID")
    def test_get_post(self):
        """
        Test fetching a post by its ID.

        Steps:
        1. Send a GET request with a valid post ID.
        2. Assert response matches PostResponse structure.
        """
        with allure.step("Step 1: Retrieve post by ID"):
            response = self.post.get_post(status=200, post_id=self.post_id)
        with allure.step("Step 2: Validate response"):
            assert PostResponse(**response.json())

    @allure.title("Update a post with valid data")
    @allure.story("Positive: Successfully update post title")
    def test_update_post_valid(self):
        """
        Test updating a post with valid input.

        Steps:
        1. Generate new title.
        2. Send an update request.
        3. Assert the response contains updated title.
        """
        with allure.step("Step 1: Generate new title"):
            title = post_gen.title.valid
            data_update = {"title": title}
        with allure.step("Step 2: Update the post"):
            response = self.post.update_post(
                data=data_update, status=200, post_id=self.post_id
            )
        with allure.step("Step 3: Validate title update"):
            validate_response = PostResponse(**response.json())
            assert validate_response.title == title

    @allure.title("Fail to update post with invalid title")
    @allure.story("Negative: Title validation on update")
    @pytest.mark.parametrize(
        "title_builder, expected_message",
        [
            pytest.param(
                lambda b: b.title.empty,
                settings.errors.text.none,
                id="title empty",
            ),
            pytest.param(
                lambda b: b.title.too_long,
                settings.errors.text.too_long,
                id="title too long",
            ),
            pytest.param(
                lambda b: b.title.none,
                settings.errors.text.none,
                id="title none",
            ),
        ],
    )
    def test_update_post_invalid(self, title_builder, expected_message):
        """
        Test updating a post with invalid titles.

        Steps:
        1. Prepare invalid title.
        2. Send a PATCH/PUT request.
        3. Assert validation error is returned for the title field.
        """
        with allure.step("Step 1: Prepare invalid title"):
            title = title_builder(post_gen)
            data_update = {"title": title}
        with allure.step("Step 2: Try to update the post"):
            response = self.post.update_post(
                data=data_update, status=422, post_id=self.post_id
            )
        with allure.step("Step 3: Validate title error"):
            errors = response.json()
            assert any(
                e["field"] == "title" and e["message"] == expected_message
                for e in errors
            )

    @allure.title("Get list of posts filtered by user_id")
    @allure.story("Positive: Filter posts by user ID")
    def test_get_list_posts_filter_by_user(self):
        """
        Test retrieving a list of posts filtered by user_id.

        Steps:
        1. Send a GET request with user_id parameter.
        2. Assert all returned posts belong to that user.
        """
        with allure.step("Step 1: Filter posts by user_id"):
            params = {"user_id": self.user_id_with_posts}
            response = self.post.get_list_posts(status=200, params=params)
            posts = response.json()
        with allure.step("Step 2: Validate user_id in results"):
            assert all(post["user_id"] == self.user_id_with_posts for post in posts)

    @allure.title("Get list of posts with and without filters")
    @allure.story("Positive: Retrieve posts with different filters")
    @pytest.mark.parametrize(
        "params, validate_fn, label",
        [
            (
                    None,
                    lambda r: all(PostResponse(**post) for post in r.json()),
                    "no_params",
            ),
            ({"per_page": 5}, lambda r: len(r.json()) == 5, "filter_per_page"),
        ],
    )
    def test_get_list_posts_parametrized(self, params, validate_fn, label):
        """
        Test retrieving a list of posts with optional filters.

        Steps:
        1. Send GET request with query parameters.
        2. Validate the response using provided function.
        """
        with allure.step(f"Step 1: Retrieve posts using: {label}"):
            response = self.post.get_list_posts(status=200, params=params)
        with allure.step("Step 2: Validate post list"):
            assert validate_fn(response)

    @allure.title("Delete a post")
    @allure.story("Positive: Successfully delete a post")
    def test_delete_post(self):
        """
        Test deleting a post.

        Steps:
        1. Send DELETE request for a post.
        2. Attempt to retrieve the same post.
        3. Assert 404 error is returned.
        """
        with allure.step("Step 1: Delete a post"):
            self.post.delete_post(status=204, post_id=self.post_id)
        with allure.step("Step 2: Try to get the deleted post"):
            response = self.post.get_post(status=404, post_id=self.post_id)
            error = response.json()
            log.info(f"Fetch after delete response: {error}")
        with allure.step("Step 3: Validate not found error"):
            assert error["message"] == "Resource not found"
