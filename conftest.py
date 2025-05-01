import pytest
from playwright.sync_api import sync_playwright

from config import settings
from core.logger import Logger

log = Logger().get_logger("playwright_session")


@pytest.fixture(scope="session")
def pw_context():
    log.info("▶ Starting Playwright")
    pw = sync_playwright().start()

    ctx = pw.request.new_context(
        base_url=settings.api.base_url,
        timeout=15_000,  # 15 s на каждый запрос
        extra_http_headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.api.token}",
        },
    )

    yield ctx

    log.info("⏹ Stopping Playwright")
    ctx.dispose()
    pw.stop()
