import time

import pytest
from playwright.sync_api import sync_playwright

from config import settings
from core.logger import Logger
from core.utils.data_generators import set_seed

log = Logger().get_logger("conftest")


@pytest.fixture(scope="session")
def pw_context():
    log.info("▶ Starting Playwright")
    pw = sync_playwright().start()
    ctx = pw.request.new_context(
        base_url=settings.api.base_url,
        extra_http_headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.api.token}",
        },
    )
    yield ctx
    ctx.dispose()
    pw.stop()
    log.info("⏹ Stopping Playwright")


@pytest.fixture(autouse=True)
def _reset_faker_seed() -> None:
    set_seed(int(time.time() * 1_000) & 0xFFFFFFFF)
