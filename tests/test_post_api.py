import allure
import pytest

from clients.post_client import PostClient
from config import settings
from core.base_clients import VALID_USER_ID, user_id_with_posts
from core.core_tests import CRUDMixin, ListMixin
from core.utils import RandomPost, CommonError
from models.post_model import PostResponse
from tests.auto_allure import auto_allure

INVALID_TITLE_CASES = [
    (
        lambda gen, uid=VALID_USER_ID: gen(
            parent_id=uid, invalid=True, error_type=CommonError.EMPTY
        ),
        settings.errors.text.none,
        "title",
        "title_empty",
    ),
    (
        lambda gen, uid=VALID_USER_ID: gen(
            parent_id=uid, invalid=True, error_type=CommonError.TOO_LONG
        ),
        settings.errors.text.too_long,
        "title",
        "title_too_long",
    ),
    (
        lambda gen, uid=VALID_USER_ID: gen(
            parent_id=uid, invalid=True, error_type=CommonError.NONE
        ),
        settings.errors.text.none,
        "title",
        "title_none",
    ),
]

LIST_CASES_POST = [
    pytest.param({}, lambda xs: xs, "no_params", id="no_params"),
    pytest.param({"per_page": 5}, lambda xs: len(xs) == 5, "per_page=5", id="p5"),
    pytest.param(
        {"user_id": user_id_with_posts},
        lambda xs: all(x["user_id"] == user_id_with_posts for x in xs),
        f"user_id={user_id_with_posts}",
        id="user_id_with_posts",
    ),
]


@auto_allure("post_api")
@allure.feature("Post API")
class TestPostAPI(CRUDMixin, ListMixin):
    """
    Test-OST API, built on universal mixins Crudmixin + Listmixin.
    """

    # ---------- CRUD-mixin ---------------------------------------------------
    CLIENT_CLS = PostClient
    GEN = RandomPost()
    MODEL = PostResponse
    INVALID_CASES = INVALID_TITLE_CASES
    RESOURCE_ID_FN = staticmethod(lambda: VALID_USER_ID)
    PATCH_FIELD = "title"
    PATCH_VALUE = "Updated title from test"
    # ---------- List-mixin ---------------------------------------------------
    LIST_CASES = LIST_CASES_POST
    FILTER_NAME = "user_id"
    FILTER_VALUE_FN = staticmethod(user_id_with_posts)
