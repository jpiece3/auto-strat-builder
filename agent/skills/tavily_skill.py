"""Tavily skill - AI-powered search and research."""

from __future__ import annotations

from typing import Any

import httpx

from agent.config import TavilyConfig
from agent.models import SearchResult
from agent.skills.base import BaseSkill
from agent.utils.retry import retry_async


class TavilySkill(BaseSkill):
    """AI-powered web search and research using the Tavily API.

    Capabilities:
    - General web search with AI relevance ranking
    - News-focused search
    - Topic research with comprehensive content extraction
    - Domain-specific search filtering
    """

    name = "tavily"
    description = "AI-powered web search and deep research via Tavily API"

    def __init__(self, config: TavilyConfig) -> None:
        super().__init__()
        self.config = config
        self._client = httpx.AsyncClient(
            base_url="https://api.tavily.com",
            timeout=60.0,
        )

    async def health_check(self) -> bool:
        """Check Tavily API connectivity."""
        try:
            resp = await self._client.post(
                "/search",
                json={"api_key": self.config.api_key, "query": "test", "max_results": 1},
            )
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def close(self) -> None:
        await self._client.aclose()

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def search(
        self,
        query: str,
        max_results: int | None = None,
        search_depth: str | None = None,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        topic: str = "general",
    ) -> list[SearchResult]:
        """Execute an AI-powered web search and return ranked results."""
        max_results = max_results or self.config.max_results
        search_depth = search_depth or self.config.search_depth
        self.logger.info("Searching: %r (depth=%s, max=%d)", query, search_depth, max_results)

        payload: dict[str, Any] = {
            "api_key": self.config.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_raw_content": self.config.include_raw_content,
            "topic": topic,
        }
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        resp = await self._client.post("/search", json=payload)
        resp.raise_for_status()
        data = resp.json()

        results: list[SearchResult] = []
        for item in data.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    content=item.get("raw_content", ""),
                    score=item.get("score", 0.0),
                    source="tavily",
                )
            )

        self.logger.info("Search returned %d results", len(results))
        return results

    async def search_news(
        self,
        query: str,
        max_results: int = 10,
        days: int = 7,
    ) -> list[SearchResult]:
        """Search recent news articles about a topic."""
        self.logger.info("Searching news: %r (last %d days)", query, days)
        return await self.search(
            query=query,
            max_results=max_results,
            topic="news",
        )

    async def research_topic(
        self,
        topic: str,
        queries: list[str] | None = None,
        max_results_per_query: int = 5,
    ) -> list[SearchResult]:
        """Deep research on a topic using multiple search queries."""
        import asyncio

        if not queries:
            queries = [topic]

        self.logger.info("Researching topic: %r with %d queries", topic, len(queries))

        tasks = [
            self.search(query=q, max_results=max_results_per_query, search_depth="advanced")
            for q in queries
        ]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)

        combined: list[SearchResult] = []
        seen_urls: set[str] = set()
        for result_set in all_results:
            if isinstance(result_set, Exception):
                self.logger.warning("Query failed: %s", result_set)
                continue
            for result in result_set:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    combined.append(result)

        # Sort by relevance score
        combined.sort(key=lambda r: r.score, reverse=True)
        self.logger.info("Research complete: %d unique results", len(combined))
        return combined

    async def find_competitors(
        self,
        brand_name: str,
        industry: str,
        domain: str,
    ) -> list[SearchResult]:
        """Search for brand competitors and alternatives."""
        queries = [
            f"{brand_name} competitors {industry}",
            f"companies similar to {brand_name}",
            f"{brand_name} alternatives",
            f"top {industry} companies like {brand_name}",
            f"{domain} competitor websites",
        ]
        return await self.research_topic(
            topic=f"competitors of {brand_name}",
            queries=queries,
            max_results_per_query=5,
        )

    async def find_brand_mentions(
        self, brand_name: str, domain: str
    ) -> list[SearchResult]:
        """Search for brand mentions, reviews, and press coverage."""
        queries = [
            f'"{brand_name}" review',
            f'"{brand_name}" press coverage',
            f'"{brand_name}" customer feedback',
            f"site:reddit.com {brand_name}",
            f"site:trustpilot.com {domain}",
        ]
        return await self.research_topic(
            topic=f"mentions of {brand_name}",
            queries=queries,
            max_results_per_query=5,
        )
