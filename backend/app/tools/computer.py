from __future__ import annotations

import os
from typing import Any, Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from backend.app.tools.tool import Tool


class ComputerTool(Tool):
    """
    Browser-based computer interaction tool for AURA.

    Uses the Chrome browser already installed on Windows,
    so Playwright does not need to download Chromium.

    Supported actions:
    - open
    - click
    - type
    - press
    - extract_text
    - screenshot
    - current_page
    - close
    """

    name = "computer"

    description = (
        "Interact with websites through a real Chrome browser. "
        "Can open pages, click elements, type text, press keyboard keys, "
        "read page content, and take screenshots."
    )

    CHROME_PATHS = [
        os.path.expandvars(
            r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"
        ),
        os.path.expandvars(
            r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"
        ),
        os.path.expandvars(
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
        ),
    ]

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def _find_chrome(self) -> Optional[str]:
        for path in self.CHROME_PATHS:
            if os.path.isfile(path):
                return path

        return None

    def _ensure_browser(self) -> Page:
        if self.page is not None:
            return self.page

        chrome_path = self._find_chrome()

        if not chrome_path:
            raise RuntimeError(
                "Google Chrome was not found on this computer. "
                "Install Google Chrome or provide a valid Chrome path."
            )

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            executable_path=chrome_path,
        )

        self.context = self.browser.new_context(
            viewport={
                "width": 1440,
                "height": 900,
            }
        )

        self.page = self.context.new_page()

        return self.page

    def execute(
        self,
        action: str,
        url: Optional[str] = None,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        key: Optional[str] = None,
        path: Optional[str] = None,
        timeout: int = 10000,
    ) -> dict[str, Any]:

        action = (action or "").strip().lower()

        try:
            if action == "open":
                return self._open(url, timeout)

            if action == "click":
                return self._click(selector, timeout)

            if action == "type":
                return self._type(selector, text, timeout)

            if action == "press":
                return self._press(selector, key, timeout)

            if action == "extract_text":
                return self._extract_text()

            if action == "screenshot":
                return self._screenshot(path)

            if action == "current_page":
                return self._current_page()

            if action == "close":
                return self.close()

            return {
                "success": False,
                "tool": self.name,
                "action": action,
                "error": (
                    f"Unsupported computer action: {action}. "
                    "Supported actions: open, click, type, press, "
                    "extract_text, screenshot, current_page, close."
                ),
            }

        except Exception as error:
            return {
                "success": False,
                "tool": self.name,
                "action": action,
                "error": str(error),
            }

    def _open(
        self,
        url: Optional[str],
        timeout: int,
    ) -> dict[str, Any]:

        if not url:
            return {
                "success": False,
                "tool": self.name,
                "action": "open",
                "error": "URL is required.",
            }

        page = self._ensure_browser()

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=timeout,
        )

        return {
            "success": True,
            "tool": self.name,
            "action": "open",
            "url": page.url,
            "title": page.title(),
        }

    def _click(
        self,
        selector: Optional[str],
        timeout: int,
    ) -> dict[str, Any]:

        if not selector:
            return {
                "success": False,
                "tool": self.name,
                "action": "click",
                "error": "Selector is required.",
            }

        page = self._ensure_browser()

        page.locator(selector).first.click(
            timeout=timeout
        )

        return {
            "success": True,
            "tool": self.name,
            "action": "click",
            "selector": selector,
            "url": page.url,
            "title": page.title(),
        }

    def _type(
        self,
        selector: Optional[str],
        text: Optional[str],
        timeout: int,
    ) -> dict[str, Any]:

        if not selector:
            return {
                "success": False,
                "tool": self.name,
                "action": "type",
                "error": "Selector is required.",
            }

        if text is None:
            return {
                "success": False,
                "tool": self.name,
                "action": "type",
                "error": "Text is required.",
            }

        page = self._ensure_browser()

        page.locator(selector).first.fill(
            text,
            timeout=timeout,
        )

        return {
            "success": True,
            "tool": self.name,
            "action": "type",
            "selector": selector,
            "text_length": len(text),
            "url": page.url,
        }

    def _press(
        self,
        selector: Optional[str],
        key: Optional[str],
        timeout: int,
    ) -> dict[str, Any]:

        if not key:
            return {
                "success": False,
                "tool": self.name,
                "action": "press",
                "error": "Key is required.",
            }

        page = self._ensure_browser()

        if selector:
            page.locator(selector).first.press(
                key,
                timeout=timeout,
            )
        else:
            page.keyboard.press(key)

        return {
            "success": True,
            "tool": self.name,
            "action": "press",
            "selector": selector,
            "key": key,
            "url": page.url,
        }

    def _extract_text(self) -> dict[str, Any]:

        page = self._ensure_browser()

        text = page.locator("body").inner_text()

        return {
            "success": True,
            "tool": self.name,
            "action": "extract_text",
            "url": page.url,
            "title": page.title(),
            "text": text[:20000],
        }

    def _screenshot(
        self,
        path: Optional[str],
    ) -> dict[str, Any]:

        page = self._ensure_browser()

        screenshot_path = path or "aura_screenshot.png"

        page.screenshot(
            path=screenshot_path,
            full_page=True,
        )

        return {
            "success": True,
            "tool": self.name,
            "action": "screenshot",
            "path": screenshot_path,
            "url": page.url,
        }

    def _current_page(self) -> dict[str, Any]:

        page = self._ensure_browser()

        return {
            "success": True,
            "tool": self.name,
            "action": "current_page",
            "url": page.url,
            "title": page.title(),
        }

    def close(self) -> dict[str, Any]:

        try:
            if self.context is not None:
                self.context.close()

            if self.browser is not None:
                self.browser.close()

            if self.playwright is not None:
                self.playwright.stop()

        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None

        return {
            "success": True,
            "tool": self.name,
            "action": "close",
        }


computer_tool = ComputerTool(headless=True)