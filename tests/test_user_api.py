import allure
import pytest

from clients.user_client import UserClient
from config import settings
from core.core_tests import CRUDMixin, ListMixin
from core.utils import RandomUser, EmailError
from models.user_model import UserResponse
from tests.auto_allure import auto_allure

INVALID_CASES_EMAIL = [
    (
        lambda gen: gen(invalid=True, error_type=EmailError.INVALID),
        settings.errors.text.is_invalid,
        "email",
        "invalid_email_format",
    ),
    (
        lambda gen: gen(invalid=True, error_type=EmailError.NONE),
        settings.errors.text.none,
        "email",
        "empty_email",
    ),
]

LIST_CASES_USER = [
    pytest.param({}, lambda xs: xs, "no_params", id="no_params"),
    pytest.param({"per_page": 5}, lambda xs: len(xs) == 5, "per_page=5", id="p5"),
    pytest.param(
        {"gender": "male"},
        lambda xs: all(x["gender"] == "male" for x in xs),
        "gender=male",
        id="gender_male",
    ),
]


@auto_allure("user_api")
@allure.feature("User API")
class TestUserAPI(CRUDMixin, ListMixin):
    # ---------- CRUD-mixin ---------------------------------------------------
    CLIENT_CLS = UserClient
    GEN = RandomUser()
    MODEL = UserResponse
    PATCH_FIELD = "status"
    PATCH_VALUE = "inactive"
    INVALID_CASES = INVALID_CASES_EMAIL
    # ---------- List-mixin ---------------------------------------------------
    LIST_CASES = LIST_CASES_USER
    FILTER_NAME = "gender"
    FILTER_VALUE_FN = staticmethod(lambda: "male")
