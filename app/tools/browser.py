"""
browser.py — One shared Playwright browser that all tools use.

Playwright is a free, open-source browser automation library. The browser is
started lazily (the first time a tool needs it) and then reused, so
"open YouTube" followed by "scroll down" works on the same page.

Env vars:
    BROWSER_HEADLESS=1   run without a visible window (default: visible)
"""

import os
import logging
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

logger = logging.getLogger(__name__)


class BrowserController:
    def __init__(self):
        self._pw: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def page(self) -> Page:
        """Return the current page, starting the browser if needed."""
        if self._browser is None or not self._browser.is_connected():
            headless = os.environ.get("BROWSER_HEADLESS", "0") == "1"
            logger.info(f"[browser] launching Chromium (headless={headless})")
            self._pw = await async_playwright().start()
            self._browser = await self._pw.chromium.launch(
                headless=headless, args=["--start-maximized"]
            )
            self._context = await self._browser.new_context(no_viewport=True)
            self._page = None

        if self._page is None or self._page.is_closed():
            self._page = await self._context.new_page()
        return self._page

    async def close(self):
        if self._browser is not None:
            await self._browser.close()
        if self._pw is not None:
            await self._pw.stop()
        self._pw = self._browser = self._context = self._page = None


# One shared instance for the whole app
browser = BrowserController()
