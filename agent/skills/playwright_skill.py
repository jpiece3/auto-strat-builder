"""Playwright skill - browser automation for dynamic content and social profiles."""

from __future__ import annotations

import asyncio
from typing import Any

from agent.config import PlaywrightConfig
from agent.models import SocialPresence, WebPage
from agent.skills.base import BaseSkill
from agent.utils.retry import retry_async


class PlaywrightSkill(BaseSkill):
    """Browser automation using Playwright for JavaScript-heavy pages and social profiles.

    Capabilities:
    - Render JavaScript-heavy single-page applications
    - Capture screenshots for visual analysis
    - Scrape social media profile metadata
    - Extract dynamic/interactive content
    - Collect structured data from rendered pages
    """

    name = "playwright"
    description = "Browser automation for dynamic content scraping and social profiles"

    def __init__(self, config: PlaywrightConfig) -> None:
        super().__init__()
        self.config = config
        self._playwright: Any = None
        self._browser: Any = None

    async def _ensure_browser(self) -> Any:
        """Lazily initialize the Playwright browser."""
        if self._browser is None:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.config.headless
            )
            self.logger.info("Browser launched (headless=%s)", self.config.headless)
        return self._browser

    async def health_check(self) -> bool:
        """Verify Playwright is installed and can launch a browser."""
        try:
            browser = await self._ensure_browser()
            page = await browser.new_page()
            await page.goto("https://example.com", timeout=self.config.timeout)
            await page.close()
            return True
        except Exception as exc:
            self.logger.warning("Playwright health check failed: %s", exc)
            return False

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def _new_page(self) -> Any:
        """Create a new browser page with standard configuration."""
        browser = await self._ensure_browser()
        context = await browser.new_context(
            viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
            user_agent=self.config.user_agent,
        )
        return await context.new_page()

    @retry_async(max_attempts=2, base_delay=3.0)
    async def render_page(self, url: str, wait_for: str = "networkidle") -> WebPage:
        """Navigate to a URL, wait for full render, and extract content."""
        self.logger.info("Rendering page: %s", url)
        page = await self._new_page()
        try:
            response = await page.goto(url, wait_until=wait_for, timeout=self.config.timeout)
            status_code = response.status if response else 0

            title = await page.title()
            # Extract text content
            content = await page.evaluate("() => document.body.innerText")
            # Extract meta description
            meta_desc = await page.evaluate(
                '() => document.querySelector(\'meta[name="description"]\')?.content || ""'
            )
            # Extract all headings
            headings = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('h1, h2, h3, h4'))
                    .map(h => h.innerText.trim())
                    .filter(Boolean);
            }""")
            # Extract links
            links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(h => h.startsWith('http'));
            }""")

            return WebPage(
                url=url,
                title=title,
                content=content,
                meta_description=meta_desc,
                headings=headings,
                links=list(set(links))[:100],
                status_code=status_code,
            )
        finally:
            await page.context.close()

    @retry_async(max_attempts=2, base_delay=3.0)
    async def take_screenshot(self, url: str, full_page: bool = True) -> bytes:
        """Capture a screenshot of a rendered page."""
        self.logger.info("Taking screenshot: %s", url)
        page = await self._new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.config.timeout)
            return await page.screenshot(full_page=full_page, type="png")
        finally:
            await page.context.close()

    @retry_async(max_attempts=2, base_delay=3.0)
    async def scrape_social_profile(self, platform: str, url: str) -> SocialPresence:
        """Scrape a public social media profile for metadata and stats."""
        self.logger.info("Scraping social profile: %s (%s)", url, platform)
        page = await self._new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.config.timeout)
            await asyncio.sleep(2)  # Allow dynamic content to settle

            scrapers = {
                "linkedin": self._scrape_linkedin,
                "twitter": self._scrape_twitter,
                "facebook": self._scrape_facebook,
                "instagram": self._scrape_instagram,
            }

            scraper = scrapers.get(platform.lower(), self._scrape_generic_social)
            data = await scraper(page)

            return SocialPresence(
                platform=platform,
                url=url,
                followers=data.get("followers", 0),
                engagement_rate=data.get("engagement_rate", 0.0),
                post_frequency=data.get("post_frequency", ""),
                top_content_themes=data.get("themes", []),
                sentiment=data.get("sentiment", ""),
                raw_data=data,
            )
        finally:
            await page.context.close()

    async def scrape_multiple_pages(self, urls: list[str], concurrency: int = 3) -> list[WebPage]:
        """Scrape multiple pages concurrently with controlled parallelism."""
        self.logger.info("Scraping %d pages (concurrency=%d)", len(urls), concurrency)
        semaphore = asyncio.Semaphore(concurrency)
        results: list[WebPage] = []

        async def _scrape(u: str) -> WebPage | None:
            async with semaphore:
                try:
                    return await self.render_page(u)
                except Exception as exc:
                    self.logger.warning("Failed to scrape %s: %s", u, exc)
                    return None

        tasks = [_scrape(u) for u in urls]
        completed = await asyncio.gather(*tasks)
        for page in completed:
            if page is not None:
                results.append(page)

        self.logger.info("Successfully scraped %d/%d pages", len(results), len(urls))
        return results

    async def extract_structured_data(self, url: str, selectors: dict[str, str]) -> dict[str, str]:
        """Extract specific data from a page using CSS selectors."""
        self.logger.info("Extracting structured data from: %s", url)
        page = await self._new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.config.timeout)
            results: dict[str, str] = {}
            for key, selector in selectors.items():
                try:
                    element = await page.query_selector(selector)
                    results[key] = await element.inner_text() if element else ""
                except Exception:
                    results[key] = ""
            return results
        finally:
            await page.context.close()

    # ------------------------------------------------------------------
    # Platform-specific scrapers
    # ------------------------------------------------------------------

    async def _scrape_linkedin(self, page: Any) -> dict[str, Any]:
        """Extract data from a LinkedIn company page."""
        data: dict[str, Any] = {}
        try:
            data["company_name"] = await page.evaluate(
                '() => document.querySelector("h1")?.innerText || ""'
            )
            data["tagline"] = await page.evaluate(
                '() => document.querySelector(".org-top-card-summary__tagline")?.innerText || ""'
            )
            followers_text = await page.evaluate("""() => {
                const el = document.querySelector('.org-top-card-summary-info-list__info-item');
                return el ? el.innerText : '';
            }""")
            data["followers"] = self._parse_follower_count(followers_text)
            body_text = await page.evaluate("() => document.body.innerText")
            data["full_text"] = body_text[:5000]
        except Exception as exc:
            self.logger.warning("LinkedIn scrape partial failure: %s", exc)
        return data

    async def _scrape_twitter(self, page: Any) -> dict[str, Any]:
        """Extract data from a Twitter/X profile."""
        data: dict[str, Any] = {}
        try:
            data["display_name"] = await page.evaluate(
                '() => document.querySelector("[data-testid=\'UserName\']")?.innerText || ""'
            )
            data["bio"] = await page.evaluate(
                '() => document.querySelector("[data-testid=\'UserDescription\']")?.innerText || ""'
            )
            body_text = await page.evaluate("() => document.body.innerText")
            data["full_text"] = body_text[:5000]
            data["followers"] = self._parse_follower_count(body_text)
        except Exception as exc:
            self.logger.warning("Twitter scrape partial failure: %s", exc)
        return data

    async def _scrape_facebook(self, page: Any) -> dict[str, Any]:
        """Extract data from a Facebook page."""
        data: dict[str, Any] = {}
        try:
            body_text = await page.evaluate("() => document.body.innerText")
            data["full_text"] = body_text[:5000]
            data["followers"] = self._parse_follower_count(body_text)
        except Exception as exc:
            self.logger.warning("Facebook scrape partial failure: %s", exc)
        return data

    async def _scrape_instagram(self, page: Any) -> dict[str, Any]:
        """Extract data from an Instagram profile."""
        data: dict[str, Any] = {}
        try:
            body_text = await page.evaluate("() => document.body.innerText")
            data["full_text"] = body_text[:5000]
            data["followers"] = self._parse_follower_count(body_text)
        except Exception as exc:
            self.logger.warning("Instagram scrape partial failure: %s", exc)
        return data

    async def _scrape_generic_social(self, page: Any) -> dict[str, Any]:
        """Fallback scraper for unknown social platforms."""
        body_text = await page.evaluate("() => document.body.innerText")
        return {"full_text": body_text[:5000], "followers": self._parse_follower_count(body_text)}

    @staticmethod
    def _parse_follower_count(text: str) -> int:
        """Attempt to parse a follower count from text."""
        import re

        patterns = [
            r"([\d,]+(?:\.\d+)?[KkMm]?)\s*(?:followers|Followers|FOLLOWERS)",
            r"(?:followers|Followers)[\s:]*(\d[\d,]*(?:\.\d+)?[KkMm]?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                raw = match.group(1).replace(",", "")
                multiplier = 1
                if raw[-1].lower() == "k":
                    multiplier = 1_000
                    raw = raw[:-1]
                elif raw[-1].lower() == "m":
                    multiplier = 1_000_000
                    raw = raw[:-1]
                try:
                    return int(float(raw) * multiplier)
                except ValueError:
                    continue
        return 0
