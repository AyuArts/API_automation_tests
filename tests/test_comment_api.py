import allure
import pytest

from clients.comment_client import CommentClient
from config import settings
from core.base_clients import VALID_POST_ID
from core.core_tests import CRUDMixin, ListMixin
from core.utils import EmailError, RandomComment, CommonError
from models.comment_model import CommentResponse
from tests.auto_allure import auto_allure


@auto_allure("comment_api")
@allure.feature("Comment API")
class TestCommentAPI(CRUDMixin, ListMixin):
    # ---------- CRUD-mixin ---------------------------------------------------
    CLIENT_CLS = CommentClient
    GEN = RandomComment()
    MODEL = CommentResponse
    PATCH_FIELD = "body"
    PATCH_VALUE = "Updated via test"
    RESOURCE_ID_FN = staticmethod(lambda: VALID_POST_ID)
    INVALID_CASES = [
        (
            lambda gen, uid=VALID_POST_ID: gen(
                parent_id=uid, invalid=True, error_type=CommonError.EMPTY
            ),
            settings.errors.text.none,
            "name",
            "empty_name",
        ),
        (
            lambda gen, uid=VALID_POST_ID: gen(
                parent_id=uid, invalid=True, error_type=EmailError.INVALID
            ),
            settings.errors.text.is_invalid,
            "email",
            "invalid_email",
        ),
        (
            lambda gen, uid=VALID_POST_ID: gen(
                parent_id=uid, invalid=True, error_type=EmailError.NONE
            ),
            "can't be blank, is invalid",
            "email",
            "empty_email",
        ),
        (
            lambda gen, uid=VALID_POST_ID: gen(
                parent_id=uid, invalid=True, error_type=CommonError.NONE
            ),
            settings.errors.text.none,
            "body",
            "empty_body",
        ),
    ]

    # ---------- List-mixin ---------------------------------------------------
    LIST_CASES = [
        pytest.param({}, lambda xs: xs, "no_params", id="no_params"),
        pytest.param({"per_page": 5}, lambda xs: len(xs) == 5, "per_page=5", id="p5"),
        pytest.param(
            {"post_id": VALID_POST_ID},
            lambda xs: all(x["post_id"] == VALID_POST_ID for x in xs),
            f"post_id={VALID_POST_ID}",
            id="post_id",
        ),
    ]

    FILTER_NAME = "post_id"
    FILTER_VALUE_FN = staticmethod(lambda: VALID_POST_ID)
