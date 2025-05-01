import types
from typing import Any, Callable, List, Tuple

import allure
import pytest


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def default_parent_id() -> None:
    """Return None if no external foreign key is required."""
    return None


def _assert_error(resp, field: str, expected_msg: str) -> None:
    """
    Assert that the response contains a specific validation error.

    :param resp: Response object
    :param field: Field name expected to contain an error
    :param expected_msg: Expected error message for the field
    """
    errors: List[dict[str, Any]] = resp.json()
    assert any(
        e["field"] == field and e["message"] == expected_msg for e in errors
    ), errors


# --------------------------------------------------------------------------- #
#  CRUD-Mixin                                                                 #
# --------------------------------------------------------------------------- #
class CRUDMixin:
    """
    Create / Read / Update / Delete test package, including negative scenarios.

    Overridable attributes:
    - CLIENT_CLS      – API client class (e.g., UserClient, PostClient)
    - GEN             – Payload generator function
    - MODEL           – Pydantic model for response validation
    - INVALID_CASES   – List of tuples (builder, expected_msg, field, id)
    - RESOURCE_ID_FN  – Function that returns parent_id if needed
    """

    CLIENT_CLS: type = None
    GEN: Callable = None
    MODEL: type = None
    INVALID_CASES: List[Tuple[Callable, str, str, str]] = []
    RESOURCE_ID_FN: Callable[[], Any] = staticmethod(default_parent_id)
    PATCH_FIELD = None
    PATCH_VALUE = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cases = getattr(cls, "INVALID_CASES", [])
        ids = [id_ for *_, id_ in cases] or ["no_invalid_cases"]

        def apply_parametrize(func):
            return pytest.mark.parametrize(
                "builder, expected, field",
                [(b, m, f) for b, m, f, _ in cases],
                ids=ids,
            )(func)

        orig = getattr(cls, "test_create_invalid", None)

        already_parametrized = hasattr(orig, "pytestmark") and any(
            getattr(mark, "name", None) == "parametrize" and "builder" in str(mark.args)
            for mark in getattr(orig, "pytestmark", [])
        )

        if orig is not None and not already_parametrized:
            method_copy = types.FunctionType(
                orig.__code__,
                globals(),
                name=orig.__name__,
                argdefs=orig.__defaults__,
                closure=orig.__closure__,
            )
            method_copy.__dict__.update(orig.__dict__)
            setattr(cls, "test_create_invalid", apply_parametrize(method_copy))

    @pytest.fixture(autouse=True)
    def _setup_client(self, pw_context):
        """
        Initialize API client and optional parent_id before each test.

        :param pw_context: Playwright request context fixture
        """
        self.client = self.CLIENT_CLS(pw_context)
        self.parent_id = self.RESOURCE_ID_FN()

    def test_create_valid(self):
        """
        Create an object with valid data and validate the response model.
        """
        allure.dynamic.title(f"{self.client.__class__.__name__} | create valid")
        data = self.GEN(parent_id=self.parent_id)
        resp = self.client.create_obj(data=data, status=201)
        self.MODEL.model_validate_json(resp.text())

    def test_create_invalid(self, builder, expected, field):
        """
        Create an object with invalid data and check validation errors.

        Parameters are injected by __init_subclass__ from INVALID_CASES.

        :param builder: Function that builds invalid payload
        :param expected: Expected error message
        :param field: Field name expected to be invalid
        """
        data = builder(self.GEN)
        resp = self.client.create_obj(data=data, status=422)
        _assert_error(resp, field, expected)

    def _create_entity(self) -> int:
        """
        Helper method to create a valid object and return its ID.

        :return: Created object's ID
        """
        resp = self.client.create_obj(
            data=self.GEN(parent_id=self.parent_id), status=201
        )
        return resp.json()["id"]

    def test_get_update_delete(self):
        """
        Full test flow:
        - Create an object
        - Retrieve it
        - Update it
        - Delete it
        - Assert it's deleted
        """
        entity_id = self._create_entity()

        resp = self.client.get_obj(entity_id, status=200)
        self.MODEL.model_validate_json(resp.text())

        patch = {self.PATCH_FIELD: self.PATCH_VALUE}
        resp = self.client.update_obj(entity_id, data=patch, status=200)
        assert resp.json()[self.PATCH_FIELD] == self.PATCH_VALUE

        self.client.delete_obj(entity_id, status=204)
        self.client.get_obj(entity_id, status=404)


# --------------------------------------------------------------------------- #
#  List-Mixin                                                                 #
# --------------------------------------------------------------------------- #
class ListMixin:
    """
    Test suite for list and filtering behavior of API endpoints.

    Overridable attributes:
    - CLIENT_CLS       – API client class
    - MODEL   – Pydantic model for list items
    - LIST_CASES       – Parametrized test inputs (params, validator, label)
    - FILTER_NAME      – Query param used for filtering (e.g., parent_id)
    - FILTER_VALUE_FN  – Function that returns filter value
    """

    CLIENT_CLS: type = None
    MODEL: type = None
    LIST_CASES: List[pytest.param] = []

    FILTER_NAME: str | None = None
    FILTER_VALUE_FN: Callable[[], Any] = staticmethod(default_parent_id)

    @pytest.fixture(autouse=True)
    def _setup_client(self, pw_context):
        """
        Initialize the API client before running the test.

        :param pw_context: Playwright request context fixture
        """
        self.client = self.CLIENT_CLS(pw_context)

    @allure.title("List resource with various query params")
    @pytest.mark.parametrize(
        "params, validator, label", LIST_CASES or [({}, lambda *_: True, "dummy")]
    )
    def test_list_generic(self, params, validator, label):
        """
        Test generic listing with optional query parameters.

        :param params: Query parameters
        :param validator: Validation function for the list
        :param label: Descriptive label for the test case
        """
        resp = self.client.get_list_objs(status=200, params=params or None)
        items = resp.json()

        for itm in items:
            self.MODEL.model_validate(itm)

        assert validator(items)

    def test_list_filtered_by_fk(self):
        """
        Test filtering list results by a foreign key (if FILTER_NAME is set).
        """
        if self.FILTER_NAME is None:
            pytest.skip("FK filter not configured")

        allure.dynamic.title(f"Filter list by {self.FILTER_NAME}")
        fk_value = self.FILTER_VALUE_FN()
        resp = self.client.get_list_objs(
            status=200, params={self.FILTER_NAME: fk_value}
        )
        items = resp.json()
        assert {i[self.FILTER_NAME] for i in items} == {fk_value}
