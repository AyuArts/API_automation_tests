import time

import allure
import pytest

from core.logger import Logger

log = Logger().get_logger("BaseTest")


class BaseTest:
    """
    Playwright API test base.

    • Exposes a session-wide APIRequestContext as self.request_context
      (injected from the pw_context fixture).

    • Logs start/finish of every test (console + Allure) and shows run time.
    """

    @pytest.fixture(autouse=True)
    def _init_context(self, pw_context, request):
        """Attach pw_context and wrap the test with simple timing/logging."""
        self.request_context = pw_context

        test_id = request.node.nodeid
        start = time.perf_counter()
        log.info(f"▼ Start test: {test_id}")
        with allure.step(f"Start test: {test_id}"):
            yield

        log.info(f"▲ End test: {test_id} – {time.perf_counter() - start:.2f}s")
        with allure.step(f"End test: {test_id}"):
            pass
