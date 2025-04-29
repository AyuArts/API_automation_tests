import allure
import pytest
from playwright.sync_api import sync_playwright

from config import settings
from core import Logger
from core.clients import BaseClient

log = Logger().get_logger("BaseTest")


class BaseTest:
    """
    Basic class for API tests with Playwright.
    Responses the initialization of request_context, API clients and logs.
    """

    class_client: BaseClient = None

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request):
        test_name = request.node.name

        with allure.step(f"Start test: {test_name}"):
            log.info(f"Start test: {test_name}")
            try:
                self.playwright = sync_playwright().start()
                self.request_context = self.playwright.request.new_context(
                    base_url=settings.api.base_url,
                    extra_http_headers={"Content-Type": "application/json"},
                )
                log.info(
                    f"Playwright RequestContext initialized: {settings.api.base_url}"
                )

                self.client = self.class_client(self.request_context)
            except Exception as e:
                log.exception(f"The error at setup: {str(e)}")
                raise

        yield

        with allure.step(f"Teardown test: {test_name}"):
            try:
                self.request_context.dispose()
                self.playwright.stop()
                log.info(f"Playwright RequestContext closed for the test: {test_name}")
            except Exception as e:
                log.exception(f"The error at teardown: {str(e)}")
                raise
