from abc import ABC

import allure
import pytest
from playwright.sync_api import APIRequestContext, Response

from core.decorators import retry_on_failure
from core.logger import Logger

logger = Logger(debug=True).get_logger(name="api_client")


class BaseClient(ABC):
    """
    Abstract base class for HTTP API clients using Playwright's APIRequestContext.
    Provides wrapper methods for GET, POST, PUT, PATCH, and DELETE with built-in
    logging, Allure reporting, retrying, and response status validation.
    """

    def __init__(self, request_context: APIRequestContext):
        """
        :param request_context: An instance of Playwright's APIRequestContext.
        """
        self.context = request_context

    def _log_request_response(
            self, method: str, endpoint: str, response: Response, request_params: dict
    ):
        """
        Logs and attaches request and response data to Allure reports.

        :param method: HTTP method used (GET, POST, etc.)
        :param endpoint: API endpoint called
        :param response: Response object from the request
        :param request_params: Parameters sent with the request
        """
        with allure.step(f"{method.upper()} {endpoint}"):
            logger.info(f"Request method: {method.upper()}")
            logger.info(f"Request URL: {endpoint}")
            logger.info(f"Request headers: {request_params.get('headers')}")
            logger.info(
                f"Request data: {request_params.get('data') or request_params.get('json')}"
            )
            logger.info(f"Response status: {response.status}")
            logger.info(f"Response headers: {response.headers}")
            logger.info(f"Response body: {response.text()}")

            allure.attach(
                body=str(
                    {
                        "method": method.upper(),
                        "url": endpoint,
                        "headers": request_params.get("headers"),
                        "body": request_params.get("data")
                                or request_params.get("json"),
                    }
                ),
                name="Request",
                attachment_type=allure.attachment_type.JSON,
            )

            allure.attach(
                body=str(
                    {
                        "status": response.status,
                        "headers": response.headers,
                        "body": response.text(),
                    }
                ),
                name="Response",
                attachment_type=allure.attachment_type.JSON,
            )

    def _assert_status(self, response: Response, expected_status=200) -> Response:
        """
        Asserts that the actual status code matches the expected one(s).
        If not, fails the test and attaches the response to Allure.

        :param response: Response object to validate
        :param expected_status: Expected status code or list of acceptable codes
        :return: Response object if valid
        """
        if isinstance(expected_status, (list, tuple)):
            if response.status not in expected_status:
                error_message = (
                    f"Expected status in {expected_status}, but got {response.status}\n"
                    f"Response body: {response.text()}"
                )
                logger.error(error_message)
                allure.attach(
                    name="Failed response body",
                    body=response.text(),
                    attachment_type=allure.attachment_type.JSON,
                )
                pytest.fail(error_message)
        else:
            if response.status != expected_status:
                error_message = (
                    f"Expected status {expected_status}, but got {response.status}\n"
                    f"Response body: {response.text()}"
                )
                logger.error(error_message)
                allure.attach(
                    name="Failed response body",
                    body=response.text(),
                    attachment_type=allure.attachment_type.JSON,
                )
                pytest.fail(error_message)

        return response

    @retry_on_failure(max_retries=3, delay=2)
    def get(self, endpoint: str, expected_status=200, **kwargs) -> Response:
        """
        Sends a GET request.

        :param endpoint: URL path of the API
        :param expected_status: Expected HTTP status code
        :param kwargs: Optional query params, headers, etc.
        :return: Validated response object
        """
        response = self.context.get(endpoint, **kwargs)
        self._log_request_response("GET", endpoint, response, request_params=kwargs)
        return self._assert_status(response, expected_status)

    @retry_on_failure(max_retries=3, delay=2)
    def post(self, endpoint: str, data=None, expected_status=200, **kwargs) -> Response:
        """
        Sends a POST request.

        :param endpoint: URL path of the API
        :param data: Request payload
        :param expected_status: Expected HTTP status code
        :param kwargs: Optional headers, etc.
        :return: Validated response object
        """
        response = self.context.post(endpoint, data=data, **kwargs)
        params = {**kwargs, "data": data}
        self._log_request_response("POST", endpoint, response, request_params=params)
        return self._assert_status(response, expected_status)

    @retry_on_failure(max_retries=3, delay=2)
    def put(self, endpoint: str, data=None, expected_status=200, **kwargs) -> Response:
        """
        Sends a PUT request.

        :param endpoint: URL path of the API
        :param data: Request payload
        :param expected_status: Expected HTTP status code
        :param kwargs: Optional headers, etc.
        :return: Validated response object
        """
        response = self.context.put(endpoint, data=data, **kwargs)
        params = {**kwargs, "data": data}
        self._log_request_response("PUT", endpoint, response, request_params=params)
        return self._assert_status(response, expected_status)

    @retry_on_failure(max_retries=3, delay=2)
    def patch(
            self, endpoint: str, data=None, expected_status=200, **kwargs
    ) -> Response:
        """
        Sends a PATCH request.

        :param endpoint: URL path of the API
        :param data: Request payload
        :param expected_status: Expected HTTP status code
        :param kwargs: Optional headers, etc.
        :return: Validated response object
        """
        response = self.context.patch(endpoint, data=data, **kwargs)
        params = {**kwargs, "data": data}
        self._log_request_response("PATCH", endpoint, response, request_params=params)
        return self._assert_status(response, expected_status)

    @retry_on_failure(max_retries=3, delay=2)
    def delete(self, endpoint: str, expected_status=200, **kwargs) -> Response:
        """
        Sends a DELETE request.

        :param endpoint: URL path of the API
        :param expected_status: Expected HTTP status code
        :param kwargs: Optional query params, headers, etc.
        :return: Validated response object
        """
        response = self.context.delete(endpoint, **kwargs)
        self._log_request_response("DELETE", endpoint, response, request_params=kwargs)
        return self._assert_status(response, expected_status)
