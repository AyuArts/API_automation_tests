import json
from abc import ABC
from typing import Any, Iterable

import allure
import pytest
import requests
from playwright.sync_api import APIRequestContext, Response

from core.decorators import retry_on_failure
from core.logger import Logger

logger = Logger(debug=True).get_logger("api_client")


class BaseClient(ABC):
    """Thin wrapper around Playwright's APIRequestContext with logging + retries."""

    RETRIES: int = 3
    RETRY_DELAY: int = 2

    def __init__(self, ctx: APIRequestContext):
        self.ctx = ctx

    # ------------------------------------------------------------------ public
    def get(self, endpoint: str, **kw) -> Response:
        return self._request("get", endpoint, **kw)

    def post(self, endpoint: str, **kw) -> Response:
        return self._request("post", endpoint, **kw)

    def put(self, endpoint: str, **kw) -> Response:
        return self._request("put", endpoint, **kw)

    def patch(self, endpoint: str, **kw) -> Response:
        return self._request("patch", endpoint, **kw)

    def delete(self, endpoint: str, **kw) -> Response:
        return self._request("delete", endpoint, **kw)

    # ------------------------------------------------------------------ core
    @retry_on_failure(max_retries=RETRIES, delay=RETRY_DELAY)
    def _request(
            self,
            method: str,
            endpoint: str,
            *,
            expected_status: int | Iterable[int] = 200,
            **kwargs: Any,
    ) -> Response:
        """Low-level request executor with logging, Allure attachment and status check."""
        resp = getattr(self.ctx, method)(endpoint, **kwargs)
        self._log(method, endpoint, resp, kwargs)
        return self._assert_status(resp, expected_status)

    # ------------------------------------------------------------------ helpers
    def _log(
            self,
            method: str,
            endpoint: str,
            response: Response,
            request_params: dict,
    ) -> None:
        """
        Detailed log + Allure investments.
        """
        # ------------------------------------------ console
        logger.info(f"Request method: {method.upper()}")
        logger.info(f"Request URL: {endpoint}")
        logger.info(f"Request headers: {request_params.get('headers')}")
        logger.info(
            f"Request data: {request_params.get('data') or request_params.get('json')}"
        )
        logger.info(f"Response status: {response.status}")
        logger.info(f"Response headers: {dict(response.headers)}")
        logger.info(f"Response body: {response.text()}")

        # ------------------------------------------- Allure
        with allure.step(f"{method.upper()} {endpoint}"):
            allure.attach(
                name="Request",
                body=json.dumps(
                    {
                        "method": method.upper(),
                        "url": endpoint,
                        "headers": request_params.get("headers"),
                        "body": request_params.get("data")
                                or request_params.get("json"),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                attachment_type=allure.attachment_type.JSON,
            )
            allure.attach(
                name="Response",
                body=json.dumps(
                    {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "body": (
                            response.json()
                            if response.headers.get("content-type", "").startswith(
                                "application/json"
                            )
                            else response.text()
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                attachment_type=allure.attachment_type.JSON,
            )

    @staticmethod
    def _assert_status(resp: Response, expected: int | Iterable[int]) -> Response:
        """Fail test if response status not in expected."""
        exp_set = {expected} if isinstance(expected, int) else set(expected)
        if resp.status not in exp_set:
            msg = f"Expected {exp_set}, got {resp.status}\nBody: {resp.text()}"
            allure.attach(resp.text(), "failed body", allure.attachment_type.JSON)
            logger.error(msg)
            pytest.fail(msg)
        return resp


BASE_URL = "https://gorest.co.in/public/v2"


def _existing_id(endpoint: str) -> int:
    return requests.get(f"{BASE_URL}/{endpoint}", timeout=10).json()[0]["id"]


def user_id_with_posts() -> int:
    return requests.get(f"{BASE_URL}/posts", params={"per_page": 1}, timeout=10).json()[
        0
    ]["user_id"]


VALID_USER_ID = _existing_id(endpoint="users")
VALID_POST_ID = _existing_id(endpoint="posts")
