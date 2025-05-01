import allure
import pytest

from clients.user_client import UserClient
from config import settings
from core.base_test import BaseTest
from core.logger import Logger
from core.utils import user_gen, EmailError
from models.user_model import UserBase

log = Logger().get_logger("Test_UserClient")


@allure.feature("User API")
class TestUserClient(BaseTest):
    """
    API test suite for verifying User API functionality, including:
    - user creation
    - user update
    - user deletion
    - user filtering
    """

    @pytest.fixture(autouse=True)
    def setup(self, _init_context):
        self.client = UserClient(self.request_context)

    @allure.title("Create a user with valid data")
    @allure.story("Positive: Create a new user with valid fields")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user_valid(self):
        """
        Test the creation of a user with valid input.

        Steps:
        1. Send a request to create a user using valid data.
        2. Assert the response using the Pydantic UserBase model.
        """
        with allure.step("Step 1: Send request to create a new user"):
            log.info("Creating a user with valid data.")
            response = self.client.create_user(data=user_gen(), status=201)

        with allure.step("Step 2: Validate response model"):
            log.info("Validating user model structure.")
            assert UserBase(**response.json())

    @allure.title("Fail to create user with duplicated email")
    @allure.story("Negative: Duplicated email should trigger validation error")
    def test_create_user_duplicate_email(self):
        """
        Test behavior when attempting to create a user with an existing email.

        Steps:
        1. Retrieve an existing user's email.
        2. Attempt to create another user with the same email.
        3. Assert that validation returns the correct error message.
        """
        with allure.step("Step 1: Get existing user email"):
            email = self.client.get_user_email()
            log.info(f"Retrieved existing email: {email}")

        with allure.step("Step 2: Attempt to create user with duplicate email"):
            response = self.client.create_user(data=user_gen(email=email), status=422)
            errors = response.json()

        with allure.step("Step 3: Assert validation error for duplicate email"):
            log.info(f"Validation errors: {errors}")
            assert any(
                e["field"] == "email" and e["message"] == "has already been taken"
                for e in errors
            )

    @allure.title("Fail to create user with invalid email formats")
    @allure.story("Negative: Invalid or empty email should trigger validation error")
    @pytest.mark.parametrize(
        "build_payload, expected_message",
        [
            pytest.param(
                lambda gen: gen(invalid=True, error_type=EmailError.INVALID),
                settings.errors.text.is_invalid,
                id="invalid email format",
            ),
            pytest.param(
                lambda gen: gen(invalid=True, error_type=EmailError.NONE),
                settings.errors.text.none,
                id="empty email",
            ),
        ],
    )
    def test_create_user_invalid_emails(self, build_payload, expected_message):
        """
        Test invalid or empty email formats.

        Steps:
        1. Attempt to create a user with invalid/empty email.
        2. Assert the returned validation message is correct.
        """
        with allure.step("Step 1: Send request with invalid/empty email"):
            data = build_payload(user_gen)
            response = self.client.create_user(data=data, status=422)
            errors = response.json()

        with allure.step("Step 2: Assert email validation message"):
            log.info(f"Validation errors: {errors}")
            assert any(
                e["field"] == "email" and e["message"] == expected_message
                for e in errors
            )

    @allure.title("Test user list retrieval with various query parameters")
    @allure.story("Positive: Get users list with and without filters")
    @pytest.mark.parametrize(
        "params, validate_fn, description",
        [
            pytest.param(
                None, lambda users: users is not None, "no parameters", id="no_params"
            ),
            pytest.param(
                {"gender": "male"},
                lambda users: all(u["gender"] == "male" for u in users),
                "gender=male",
                id="filter_gender",
            ),
            pytest.param(
                {"per_page": 5},
                lambda users: len(users) == 5,
                "per_page=5",
                id="filter_per_page",
            ),
        ],
    )
    def test_get_list_users_with_filters(self, params, validate_fn, description):
        """
        Test retrieval of the users list with optional filters.

        Steps:
        1. Send a GET request with query parameters.
        2. Validate the response using the provided function.
        """
        with allure.step(f"Step 1: GET request with {description}"):
            response = self.client.get_list_users(status=200, params=params)
            users = response.json()
            log.info(f"Users retrieved ({description}): {users}")

        with allure.step("Step 2: Validate user list content"):
            assert validate_fn(users)

    @allure.title("Get user by ID")
    @allure.story("Positive: Fetch single user by ID")
    def test_get_user(self):
        """
        Test retrieving a single user by ID.

        Steps:
        1. Get a random user ID.
        2. Fetch user using that ID.
        3. Assert the returned ID matches.
        """
        with allure.step("Step 1: Get a random user ID"):
            user_id = self.client.get_user_id()

        with allure.step("Step 2: Fetch user by ID"):
            response = self.client.get_user(user_id, status=200)
            user_data = response.json()
            log.info(f"Fetched user: {user_data}")

        with allure.step("Step 3: Validate returned user ID"):
            assert user_data["id"] == user_id

    @allure.title("Update user information")
    @allure.story("Positive: Update user name successfully")
    def test_update_user(self):
        """
        Test updating an existing user's name.

        Steps:
        1. Get a user ID.
        2. Send an update request with a new name.
        3. Assert the name is updated in the response.
        """
        with allure.step("Step 1: Get user ID"):
            user_id = self.client.get_user_id()

        with allure.step("Step 2: Update user's name"):
            updated_data = {"name": "Updated Name"}
            response = self.client.update_user(user_id, data=updated_data, status=200)
            user_data = response.json()
            log.info(f"Updated user: {user_data}")

        with allure.step("Step 3: Assert name update is reflected"):
            assert user_data["name"] == "Updated Name"

    @allure.title("Delete user")
    @allure.story("Positive: Successfully delete user")
    def test_delete_user(self):
        """
        Test deleting an existing user.

        Steps:
        1. Get a user ID.
        2. Delete the user by ID.
        3. Attempt to retrieve the user again.
        4. Assert a 404 Not Found response.
        """
        with allure.step("Step 1: Get user ID"):
            user_id = self.client.get_user_id()

        with allure.step("Step 2: Delete the user"):
            self.client.delete_user(user_id, status=204)
            log.info(f"Deleted user with ID: {user_id}")

        with allure.step("Step 3: Try fetching the deleted user"):
            response = self.client.get_user(user_id, status=404)
            error = response.json()
            log.info(f"Response after delete: {error}")

        with allure.step("Step 4: Assert correct error message"):
            assert error["message"] == "Resource not found"
