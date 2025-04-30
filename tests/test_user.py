import allure

from clients.user_client import UserClient
from core.base_test import BaseTest
from core.logger import Logger
from core.utils import user
from models.user_model import UserBase

log = Logger().get_logger("Test_UserClient")


@allure.feature("User API")
class TestUserClient(BaseTest):
    """
    API test suite for verifying User API functionality such as:
    - user creation
    - user update
    - user deletion
    - user filtering
    """

    class_client = UserClient

    @allure.title("Create a user with valid data")
    @allure.story("Positive: Create a new user with valid fields")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user_valid(self):
        """
        Test Steps:
        1. Send request to create a valid user.
        2. Parse response into Pydantic model.
        3. Assert that the user ID is not None.
        """
        with allure.step("Step 1: Send request to create a new user"):
            log.info("Creating a user with valid data.")
            response = self.client.create_user(data=user.valid_user, status=201)

        with allure.step("Step 2: Parse response into UserBase model"):
            log.info("Parsing response JSON into UserBase.")
            validated_user = UserBase(**response.json())

        with allure.step("Step 3: Validate user ID is not None"):
            log.info(f"Created user ID: {validated_user.id}")
            assert validated_user.id is not None

    @allure.title("Fail to create user with duplicated email")
    @allure.story("Negative: Duplicated email should trigger validation error")
    def test_create_user_duplicate_email(self):
        """
        Test Steps:
        1. Get existing user email.
        2. Try creating a new user with the same email.
        3. Assert validation error message for email duplication.
        """
        with allure.step("Step 1: Get existing user email"):
            email = self.client.get_user_email()
            log.info(f"Retrieved existing email: {email}")

        with allure.step("Step 2: Attempt to create user with duplicate email"):
            response = self.client.create_user(data=user.build_user(email), status=422)
            errors = response.json()

        with allure.step("Step 3: Assert validation error for duplicate email"):
            log.info(f"Validation errors: {errors}")
            assert any(
                e["field"] == "email" and e["message"] == "has already been taken"
                for e in errors
            )

    @allure.title("Fail to create user with invalid email")
    @allure.story("Negative: Invalid email format should be rejected")
    def test_create_user_with_invalid_email(self):
        """
        Test Steps:
        1. Try creating a user with invalid email.
        2. Assert validation error for email field.
        """
        with allure.step("Step 1: Create user with invalid email"):
            response = self.client.create_user(data=user.invalid_email_user, status=422)
            errors = response.json()

        with allure.step("Step 2: Assert validation error for email"):
            log.info(f"Validation errors: {errors}")
            assert any(
                e["field"] == "email" and e["message"] == "is invalid" for e in errors
            )

    @allure.title("Fail to create user with empty email")
    @allure.story("Negative: Empty email field should be rejected")
    def test_create_user_with_email_none(self):
        """
        Test Steps:
        1. Try creating a user without email.
        2. Assert required field validation message.
        """
        with allure.step("Step 1: Create user without email"):
            response = self.client.create_user(data=user.email_none_user, status=422)
            errors = response.json()

        with allure.step("Step 2: Assert error 'can't be blank' for email"):
            log.info(f"Validation errors: {errors}")
            assert any(
                e["field"] == "email" and e["message"] == "can't be blank"
                for e in errors
            )

    @allure.title("Get users list with no filters")
    @allure.story("Positive: Get default list of users")
    def test_get_list_users_no_params(self):
        """
        Test Steps:
        1. Get user list without filters.
        2. Assert response is not None.
        """
        with allure.step("Step 1: Request users list with no parameters"):
            response = self.client.get_list_users(status=200)

        with allure.step("Step 2: Validate response is not None"):
            log.info(f"Users list: {response.json()}")
            assert response is not None

    @allure.title("Filter users by gender")
    @allure.story("Positive: Users filtered by gender=male")
    def test_get_list_users_sort_gender(self):
        """
        Test Steps:
        1. Filter users by gender=male.
        2. Assert all users in response are male.
        """
        with allure.step("Step 1: Set gender=male as query param"):
            params = {"gender": "male"}

        with allure.step("Step 2: Send request and verify genders"):
            response = self.client.get_list_users(status=200, params=params)
            users = response.json()
            log.info(f"Filtered users: {users}")
            assert all(u["gender"] == "male" for u in users)

    @allure.title("Filter users by per_page param")
    @allure.story("Positive: Users limited to count per page")
    def test_get_list_users_sort_per_page(self):
        """
        Test Steps:
        1. Set per_page=5 parameter.
        2. Assert exactly 5 users are returned.
        """
        with allure.step("Step 1: Set per_page to 5"):
            params = {"per_page": 5}

        with allure.step("Step 2: Request users with limit"):
            response = self.client.get_list_users(status=200, params=params)
            users = response.json()
            log.info(f"Returned users: {len(users)}")

        with allure.step("Step 3: Assert 5 users returned"):
            assert len(users) == 5

    @allure.title("Get user by ID")
    @allure.story("Positive: Fetch single user by ID")
    def test_get_user(self):
        """
        Test Steps:
        1. Get a random user ID.
        2. Fetch user by that ID.
        3. Assert ID matches.
        """
        with allure.step("Step 1: Get a random user ID"):
            user_id = self.client.get_user_id()

        with allure.step("Step 2: Fetch user by ID"):
            response = self.client.get_user(user_id, status=200)
            user_data = response.json()
            log.info(f"Fetched user: {user_data}")

        with allure.step("Step 3: Assert returned user ID matches"):
            assert user_data["id"] == user_id

    @allure.title("Update user information")
    @allure.story("Positive: Update user name successfully")
    def test_update_user(self):
        """
        Test Steps:
        1. Get user ID.
        2. Send update request with new name.
        3. Assert that name is updated.
        """
        with allure.step("Step 1: Get user ID"):
            user_id = self.client.get_user_id()

        with allure.step("Step 2: Send update request"):
            updated_data = {"name": "Updated Name"}
            response = self.client.update_user(user_id, data=updated_data, status=200)
            user_data = response.json()
            log.info(f"Updated user: {user_data}")

        with allure.step("Step 3: Assert name was updated"):
            assert user_data["name"] == "Updated Name"

    @allure.title("Delete user")
    @allure.story("Positive: Successfully delete user")
    def test_delete_user(self):
        """
        Test Steps:
        1. Get user ID.
        2. Delete user.
        3. Attempt to fetch deleted user.
        4. Assert 404 returned.
        """
        with allure.step("Step 1: Get user ID"):
            user_id = self.client.get_user_id()

        with allure.step("Step 2: Delete user by ID"):
            self.client.delete_user(user_id, status=204)
            log.info(f"Deleted user with ID: {user_id}")

        with allure.step("Step 3: Attempt to fetch deleted user"):
            response = self.client.get_user(user_id, status=404)
            error = response.json()
            log.info(f"Fetch after delete response: {error}")

        with allure.step("Step 4: Assert error message is correct"):
            assert error["message"] == "Resource not found"
