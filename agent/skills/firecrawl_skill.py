"""Firecrawl skill - website crawling, scraping, and content extraction."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

from agent.config import FirecrawlConfig
from agent.models import WebPage
from agent.skills.base import BaseSkill
from agent.utils.retry import retry_async


class FirecrawlSkill(BaseSkill):
    """Crawl and scrape websites using the Firecrawl API.

    Capabilities:
    - Single-page scrape with markdown extraction
    - Multi-page site crawl
    - Structured data extraction via LLM
    - Sitemap discovery
    """

    name = "firecrawl"
    description = "Website crawling and content extraction via Firecrawl API"

    def __init__(self, config: FirecrawlConfig) -> None:
        super().__init__()
        self.config = config
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.config.timeout,
        )

    async def health_check(self) -> bool:
        """Check Firecrawl API connectivity."""
        try:
            resp = await self._client.get("/")
            return resp.status_code < 500
        except httpx.HTTPError:
            return False

    async def close(self) -> None:
        await self._client.aclose()

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def scrape_page(self, url: str, formats: list[str] | None = None) -> WebPage:
        """Scrape a single page and return structured content."""
        formats = formats or ["markdown", "html"]
        self.logger.info("Scraping page: %s", url)

        resp = await self._client.post(
            "/scrape",
            json={
                "url": url,
                "formats": formats,
            },
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})

        return WebPage(
            url=url,
            title=data.get("metadata", {}).get("title", ""),
            content=data.get("markdown", data.get("html", "")),
            meta_description=data.get("metadata", {}).get("description", ""),
            headings=self._extract_headings(data.get("markdown", "")),
            links=data.get("metadata", {}).get("links", []),
            status_code=data.get("metadata", {}).get("statusCode", 200),
        )

    @retry_async(max_attempts=2, base_delay=5.0, exceptions=(httpx.HTTPError,))
    async def crawl_site(
        self,
        url: str,
        max_pages: int | None = None,
        include_paths: list[str] | None = None,
        exclude_paths: list[str] | None = None,
    ) -> list[WebPage]:
        """Crawl an entire website and return pages as structured content."""
        max_pages = max_pages or self.config.max_pages_per_crawl
        self.logger.info("Starting site crawl: %s (max %d pages)", url, max_pages)

        payload: dict[str, Any] = {
            "url": url,
            "limit": max_pages,
            "scrapeOptions": {"formats": ["markdown"]},
        }
        if include_paths:
            payload["includePaths"] = include_paths
        if exclude_paths:
            payload["excludePaths"] = exclude_paths

        # Start async crawl
        resp = await self._client.post("/crawl", json=payload)
        resp.raise_for_status()
        crawl_id = resp.json().get("id")

        if not crawl_id:
            self.logger.error("No crawl ID returned")
            return []

        # Poll for completion
        import asyncio

        pages: list[WebPage] = []
        for _ in range(60):  # max 5 minutes polling
            await asyncio.sleep(5)
            status_resp = await self._client.get(f"/crawl/{crawl_id}")
            status_data = status_resp.json()

            if status_data.get("status") == "completed":
                for item in status_data.get("data", []):
                    pages.append(
                        WebPage(
                            url=item.get("metadata", {}).get("sourceURL", ""),
                            title=item.get("metadata", {}).get("title", ""),
                            content=item.get("markdown", ""),
                            meta_description=item.get("metadata", {}).get("description", ""),
                            headings=self._extract_headings(item.get("markdown", "")),
                            links=item.get("metadata", {}).get("links", []),
                        )
                    )
                self.logger.info("Crawl complete: %d pages collected", len(pages))
                break
            elif status_data.get("status") == "failed":
                self.logger.error("Crawl failed: %s", status_data.get("error", "unknown"))
                break

        return pages

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def extract_structured(
        self, url: str, schema: dict[str, Any], prompt: str = ""
    ) -> dict[str, Any]:
        """Extract structured data from a page using LLM-powered extraction."""
        self.logger.info("Extracting structured data from: %s", url)

        resp = await self._client.post(
            "/scrape",
            json={
                "url": url,
                "formats": ["extract"],
                "extract": {
                    "schema": schema,
                    "prompt": prompt or "Extract the requested information from this page.",
                },
            },
        )
        resp.raise_for_status()
        return resp.json().get("data", {}).get("extract", {})

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def discover_sitemap(self, url: str) -> list[str]:
        """Discover all URLs from a site's sitemap."""
        self.logger.info("Discovering sitemap for: %s", url)

        resp = await self._client.post(
            "/map",
            json={"url": url},
        )
        resp.raise_for_status()
        links = resp.json().get("links", [])
        self.logger.info("Sitemap discovery found %d URLs", len(links))
        return links

    @staticmethod
    def _extract_headings(markdown: str) -> list[str]:
        """Pull heading lines from markdown content."""
        headings: list[str] = []
        for line in markdown.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                headings.append(stripped.lstrip("#").strip())
        return headings
