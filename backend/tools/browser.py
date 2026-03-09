"""Browser Automation Tool - powered by Playwright."""
import logging
import json
from pathlib import Path

logger = logging.getLogger("probharatai.tools.browser")


class BrowserTool:
    """Browser automation using Playwright."""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    def _ensure_browser(self):
        """Launch browser if not already running."""
        if self.page is None:
            try:
                from playwright.sync_api import sync_playwright
                self._playwright = sync_playwright().start()
                self.browser = self._playwright.chromium.launch(headless=False)
                self.context = self.browser.new_context(
                    viewport={"width": 1280, "height": 720},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                self.page = self.context.new_page()
                logger.info("Browser launched successfully")
            except Exception as e:
                logger.error(f"Failed to launch browser: {e}")
                raise

    def execute(self, action: str, params: dict) -> dict:
        """Execute a browser action."""
        action_map = {
            "open": self.open_url,
            "navigate": self.open_url,
            "click": self.click,
            "type": self.type_text,
            "fill": self.fill_form,
            "scrape": self.scrape,
            "screenshot": self.screenshot,
            "wait": self.wait,
            "scroll": self.scroll,
            "get_text": self.get_text,
            "execute": self.smart_execute,
        }

        handler = action_map.get(action)
        if handler:
            return handler(params)
        return {"status": "error", "message": f"Unknown browser action: {action}"}

    def open_url(self, params):
        self._ensure_browser()
        url = params.get("url", "")
        if not url.startswith("http"):
            url = f"https://{url}"
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return {"status": "success", "url": self.page.url, "title": self.page.title()}

    def click(self, params):
        self._ensure_browser()
        selector = params.get("selector", "")
        text = params.get("text", "")
        if text:
            self.page.get_by_text(text, exact=params.get("exact", False)).click()
        elif selector:
            self.page.click(selector, timeout=10000)
        return {"status": "success", "action": "clicked"}

    def type_text(self, params):
        self._ensure_browser()
        selector = params.get("selector", "")
        text = params.get("text", "")
        self.page.fill(selector, text)
        return {"status": "success", "action": "typed", "text": text[:50]}

    def fill_form(self, params):
        self._ensure_browser()
        fields = params.get("fields", {})
        for selector, value in fields.items():
            self.page.fill(selector, value)
        return {"status": "success", "fields_filled": len(fields)}

    def scrape(self, params):
        self._ensure_browser()
        selector = params.get("selector", "body")
        elements = self.page.query_selector_all(selector)
        data = []
        for el in elements[:params.get("limit", 50)]:
            data.append({
                "text": el.inner_text(),
                "href": el.get_attribute("href"),
            })
        return {"status": "success", "count": len(data), "data": data}

    def screenshot(self, params):
        self._ensure_browser()
        path = params.get("path", "screenshot.png")
        self.page.screenshot(path=path)
        return {"status": "success", "path": path}

    def wait(self, params):
        self._ensure_browser()
        selector = params.get("selector")
        timeout = params.get("timeout", 5000)
        if selector:
            self.page.wait_for_selector(selector, timeout=timeout)
        else:
            self.page.wait_for_timeout(timeout)
        return {"status": "success"}

    def scroll(self, params):
        self._ensure_browser()
        direction = params.get("direction", "down")
        amount = params.get("amount", 500)
        if direction == "down":
            self.page.evaluate(f"window.scrollBy(0, {amount})")
        else:
            self.page.evaluate(f"window.scrollBy(0, -{amount})")
        return {"status": "success"}

    def get_text(self, params):
        self._ensure_browser()
        selector = params.get("selector", "body")
        text = self.page.inner_text(selector)
        return {"status": "success", "text": text[:5000]}

    def smart_execute(self, params):
        """Use AI to figure out what to do on the current page."""
        self._ensure_browser()
        prompt = params.get("prompt", "")
        # Get page content for context
        title = self.page.title()
        url = self.page.url
        return {
            "status": "success",
            "page_title": title,
            "page_url": url,
            "message": f"Smart execution for: {prompt}",
        }

    def close(self):
        """Close the browser."""
        if self.browser:
            self.browser.close()
        if hasattr(self, "_playwright"):
            self._playwright.stop()
        self.browser = None
        self.context = None
        self.page = None
