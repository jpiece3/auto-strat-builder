"""DataForSEO skill - SEO analytics, keyword data, and competitive intelligence."""

from __future__ import annotations

import base64
from typing import Any
from urllib.parse import urlparse

import httpx

from agent.config import DataForSEOConfig
from agent.models import SEOMetrics
from agent.skills.base import BaseSkill
from agent.utils.retry import retry_async


class DataForSEOSkill(BaseSkill):
    """Comprehensive SEO data and analytics via the DataForSEO API.

    Capabilities:
    - Domain overview and metrics
    - Keyword rankings and organic traffic
    - Backlink profile analysis
    - Competitor domain discovery
    - Technology stack detection
    - SERP analysis
    """

    name = "dataforseo"
    description = "SEO analytics, keyword rankings, and competitive data via DataForSEO API"

    def __init__(self, config: DataForSEOConfig) -> None:
        super().__init__()
        self.config = config
        creds = base64.b64encode(
            f"{config.login}:{config.password}".encode()
        ).decode()
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Basic {creds}",
                "Content-Type": "application/json",
            },
            timeout=self.config.timeout,
        )

    async def health_check(self) -> bool:
        """Check DataForSEO API connectivity."""
        try:
            resp = await self._client.get("/appendix/user_data")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def close(self) -> None:
        await self._client.aclose()

    def _clean_domain(self, url_or_domain: str) -> str:
        """Normalize a URL or domain string to a bare domain."""
        if "://" in url_or_domain:
            parsed = urlparse(url_or_domain)
            return parsed.netloc.replace("www.", "")
        return url_or_domain.replace("www.", "").strip("/")

    # ------------------------------------------------------------------
    # Domain-level analysis
    # ------------------------------------------------------------------

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def get_domain_overview(self, domain: str, location_code: int = 2840) -> SEOMetrics:
        """Get comprehensive domain SEO metrics."""
        domain = self._clean_domain(domain)
        self.logger.info("Getting domain overview: %s", domain)

        resp = await self._client.post(
            "/dataforseo_labs/google/domain_metrics_by_categories/live",
            json=[{
                "target": domain,
                "location_code": location_code,
                "language_code": "en",
            }],
        )
        resp.raise_for_status()

        # Also fetch from domain_rank endpoint for richer data
        rank_resp = await self._client.post(
            "/dataforseo_labs/google/domain_rank_overview/live",
            json=[{
                "target": domain,
                "location_code": location_code,
                "language_code": "en",
            }],
        )
        rank_data = {}
        if rank_resp.status_code == 200:
            tasks = rank_resp.json().get("tasks", [])
            if tasks and tasks[0].get("result"):
                rank_data = tasks[0]["result"][0] if tasks[0]["result"] else {}

        return SEOMetrics(
            domain=domain,
            domain_rank=rank_data.get("rank", 0),
            organic_traffic=rank_data.get("organic_etv", 0),
            organic_keywords=rank_data.get("organic_count", 0),
            backlinks_total=rank_data.get("backlinks", 0),
            referring_domains=rank_data.get("referring_domains", 0),
            domain_authority=rank_data.get("domain_authority", 0.0),
        )

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def get_organic_keywords(
        self, domain: str, limit: int = 50, location_code: int = 2840
    ) -> list[dict[str, Any]]:
        """Get top organic keywords for a domain."""
        domain = self._clean_domain(domain)
        self.logger.info("Fetching organic keywords for: %s", domain)

        resp = await self._client.post(
            "/dataforseo_labs/google/ranked_keywords/live",
            json=[{
                "target": domain,
                "location_code": location_code,
                "language_code": "en",
                "limit": limit,
                "order_by": ["keyword_data.keyword_info.search_volume,desc"],
            }],
        )
        resp.raise_for_status()
        data = resp.json()

        keywords: list[dict[str, Any]] = []
        tasks = data.get("tasks", [])
        if tasks and tasks[0].get("result"):
            for item in tasks[0]["result"][0].get("items", []):
                kw_data = item.get("keyword_data", {})
                kw_info = kw_data.get("keyword_info", {})
                keywords.append({
                    "keyword": kw_data.get("keyword", ""),
                    "position": item.get("ranked_serp_element", {}).get("serp_item", {}).get("rank_absolute", 0),
                    "search_volume": kw_info.get("search_volume", 0),
                    "cpc": kw_info.get("cpc", 0.0),
                    "competition": kw_info.get("competition_level", ""),
                    "url": item.get("ranked_serp_element", {}).get("serp_item", {}).get("url", ""),
                })

        self.logger.info("Found %d organic keywords", len(keywords))
        return keywords

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def get_backlink_summary(self, domain: str) -> dict[str, Any]:
        """Get backlink profile summary for a domain."""
        domain = self._clean_domain(domain)
        self.logger.info("Fetching backlink summary for: %s", domain)

        resp = await self._client.post(
            "/backlinks/summary/live",
            json=[{"target": domain, "internal_list_limit": 10, "include_subdomains": True}],
        )
        resp.raise_for_status()
        data = resp.json()

        tasks = data.get("tasks", [])
        if tasks and tasks[0].get("result"):
            return tasks[0]["result"][0]
        return {}

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def get_competitors(
        self, domain: str, limit: int = 10, location_code: int = 2840
    ) -> list[dict[str, Any]]:
        """Discover SEO competitors based on keyword overlap."""
        domain = self._clean_domain(domain)
        self.logger.info("Finding SEO competitors for: %s", domain)

        resp = await self._client.post(
            "/dataforseo_labs/google/competitors_domain/live",
            json=[{
                "target": domain,
                "location_code": location_code,
                "language_code": "en",
                "limit": limit,
                "order_by": ["avg_position,asc"],
            }],
        )
        resp.raise_for_status()
        data = resp.json()

        competitors: list[dict[str, Any]] = []
        tasks = data.get("tasks", [])
        if tasks and tasks[0].get("result"):
            for item in tasks[0]["result"][0].get("items", []):
                competitors.append({
                    "domain": item.get("domain", ""),
                    "avg_position": item.get("avg_position", 0),
                    "intersections": item.get("intersections", 0),
                    "organic_traffic": item.get("metrics", {}).get("organic", {}).get("etv", 0),
                    "organic_keywords": item.get("metrics", {}).get("organic", {}).get("count", 0),
                })

        self.logger.info("Found %d competitors", len(competitors))
        return competitors

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def get_keyword_suggestions(
        self, seed_keywords: list[str], limit: int = 50, location_code: int = 2840
    ) -> list[dict[str, Any]]:
        """Get keyword suggestions based on seed keywords."""
        self.logger.info("Getting keyword suggestions for: %s", seed_keywords)

        resp = await self._client.post(
            "/dataforseo_labs/google/keyword_suggestions/live",
            json=[{
                "keywords": seed_keywords,
                "location_code": location_code,
                "language_code": "en",
                "limit": limit,
                "order_by": ["keyword_info.search_volume,desc"],
            }],
        )
        resp.raise_for_status()
        data = resp.json()

        suggestions: list[dict[str, Any]] = []
        tasks = data.get("tasks", [])
        if tasks and tasks[0].get("result"):
            for item in tasks[0]["result"][0].get("items", []):
                info = item.get("keyword_info", {})
                suggestions.append({
                    "keyword": item.get("keyword", ""),
                    "search_volume": info.get("search_volume", 0),
                    "cpc": info.get("cpc", 0.0),
                    "competition": info.get("competition_level", ""),
                })

        return suggestions

    @retry_async(max_attempts=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    async def get_domain_technologies(self, domain: str) -> list[str]:
        """Detect technologies used on a domain."""
        domain = self._clean_domain(domain)
        self.logger.info("Detecting technologies for: %s", domain)

        resp = await self._client.post(
            "/domain_analytics/technologies/domain_technologies/live",
            json=[{"target": domain}],
        )
        resp.raise_for_status()
        data = resp.json()

        technologies: list[str] = []
        tasks = data.get("tasks", [])
        if tasks and tasks[0].get("result"):
            for item in tasks[0]["result"][0].get("items", []):
                for tech in item.get("technologies", []):
                    technologies.append(tech.get("name", ""))

        self.logger.info("Detected %d technologies", len(technologies))
        return technologies

    async def get_full_seo_profile(self, domain: str) -> SEOMetrics:
        """Aggregate a complete SEO profile for a domain."""
        import asyncio

        self.logger.info("Building full SEO profile for: %s", domain)

        overview, keywords, backlinks, technologies = await asyncio.gather(
            self.get_domain_overview(domain),
            self.get_organic_keywords(domain),
            self.get_backlink_summary(domain),
            self.get_domain_technologies(domain),
            return_exceptions=True,
        )

        metrics = overview if isinstance(overview, SEOMetrics) else SEOMetrics(domain=self._clean_domain(domain))

        if isinstance(keywords, list):
            metrics.top_keywords = keywords

        if isinstance(backlinks, dict):
            metrics.backlink_profile = backlinks
            metrics.backlinks_total = metrics.backlinks_total or backlinks.get("backlinks", 0)
            metrics.referring_domains = metrics.referring_domains or backlinks.get("referring_domains", 0)

        if isinstance(technologies, list):
            metrics.tech_stack = technologies

        return metrics
