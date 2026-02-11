"""Competitor Intelligence Agent - identifies and profiles competitors."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlparse

from agent.agents.base import BaseAgent
from agent.models import CompetitorProfile, WorkflowState
from agent.utils.logging import log_agent_step

COMPETITOR_ANALYST_SYSTEM = """You are a competitive intelligence analyst. Your job is to identify
real competitors, analyze their positioning, and provide actionable insights about the competitive
landscape. Be specific and data-driven. Focus on direct competitors first, then indirect ones."""


class CompetitorIntelAgent(BaseAgent):
    """Identifies competitors and builds detailed competitive profiles.

    Pipeline:
    1. Use DataForSEO to find SEO competitors (keyword overlap)
    2. Use Tavily to search for competitor mentions and comparisons
    3. Crawl top competitor websites for positioning and messaging
    4. LLM synthesis for competitive landscape analysis
    """

    name = "competitor_intel"
    description = "Identify and profile brand competitors with detailed analysis"

    async def run(self, state: WorkflowState) -> WorkflowState:
        query = state.query
        brand = state.brand
        if not brand:
            self.logger.warning("No brand profile available, skipping competitor analysis")
            return state

        dataforseo = self.skills.get("dataforseo")
        tavily = self.skills.get("tavily")
        firecrawl = self.skills.get("firecrawl")

        # Phase 1: Identify competitors from multiple sources
        log_agent_step(self.logger, self.name, "DISCOVER", "Identifying competitors")

        competitor_domains: dict[str, float] = {}

        # Source 1: User-provided competitors
        for comp in query.known_competitors:
            competitor_domains[comp] = 1.0

        # Source 2: DataForSEO SEO competitors
        if dataforseo:
            try:
                seo_competitors = await dataforseo.get_competitors(query.website_url, limit=15)
                for comp in seo_competitors:
                    domain = comp.get("domain", "")
                    if domain and domain != brand.domain:
                        score = min(comp.get("intersections", 0) / 100, 1.0)
                        competitor_domains[domain] = max(competitor_domains.get(domain, 0), score)
            except Exception as exc:
                self.logger.warning("DataForSEO competitor discovery failed: %s", exc)

        # Source 3: Tavily search for competitors
        if tavily:
            try:
                search_results = await tavily.find_competitors(
                    query.brand_name, query.industry, query.website_url
                )
                # Use LLM to extract competitor domains from search results
                search_text = "\n".join(
                    f"- {r.title}: {r.snippet} ({r.url})" for r in search_results[:20]
                )
                extracted = await self.extract_structured(
                    COMPETITOR_ANALYST_SYSTEM,
                    f"Brand: {query.brand_name}\nIndustry: {query.industry}\n\nSearch results:\n{search_text}",
                    """From these search results, extract competitor company domains.
Return JSON: {"competitors": [{"domain": "example.com", "name": "Company Name", "relevance": 0.8}]}
Only include direct competitors, not review sites, news outlets, or directories.""",
                )
                if isinstance(extracted, dict):
                    for comp in extracted.get("competitors", []):
                        domain = comp.get("domain", "")
                        if domain and domain != brand.domain:
                            competitor_domains[domain] = max(
                                competitor_domains.get(domain, 0),
                                comp.get("relevance", 0.5),
                            )
            except Exception as exc:
                self.logger.warning("Tavily competitor search failed: %s", exc)

        # Sort by relevance and take top competitors
        sorted_competitors = sorted(competitor_domains.items(), key=lambda x: x[1], reverse=True)
        top_domains = [domain for domain, _ in sorted_competitors[:8]]
        log_agent_step(self.logger, self.name, "FOUND", f"{len(top_domains)} competitors: {top_domains}")

        # Phase 2: Profile each competitor
        log_agent_step(self.logger, self.name, "PROFILE", "Building competitor profiles")

        async def _profile_competitor(domain: str, relevance: float) -> CompetitorProfile | None:
            profile = CompetitorProfile(
                name=domain,
                domain=domain,
                similarity_score=relevance,
            )

            tasks: list[Any] = []

            # Get SEO metrics
            if dataforseo:
                tasks.append(("seo", dataforseo.get_full_seo_profile(domain)))

            # Scrape competitor homepage
            if firecrawl:
                url = f"https://{domain}" if not domain.startswith("http") else domain
                tasks.append(("page", firecrawl.scrape_page(url)))

            results: dict[str, Any] = {}
            for label, coro in tasks:
                try:
                    results[label] = await coro
                except Exception as exc:
                    self.logger.warning("Failed %s for %s: %s", label, domain, exc)

            if "seo" in results:
                profile.seo_metrics = results["seo"]

            # Use LLM to analyze competitor positioning
            page_content = ""
            if "page" in results:
                page_content = f"Website content:\n{results['page'].content[:3000]}"

            seo_summary = ""
            if profile.seo_metrics:
                seo_summary = (
                    f"Organic traffic: {profile.seo_metrics.organic_traffic}, "
                    f"Keywords: {profile.seo_metrics.organic_keywords}, "
                    f"Backlinks: {profile.seo_metrics.backlinks_total}"
                )

            try:
                analysis = await self.extract_structured(
                    COMPETITOR_ANALYST_SYSTEM,
                    f"Competitor: {domain}\n{page_content}\nSEO: {seo_summary}",
                    """Analyze this competitor and return JSON:
{
    "name": "Company Name",
    "description": "2 sentence description",
    "key_differentiators": ["what makes them unique"],
    "content_themes": ["main topics they cover"],
    "strengths": ["competitive strengths"],
    "weaknesses": ["competitive weaknesses"]
}""",
                )
                if isinstance(analysis, dict):
                    profile.name = analysis.get("name", domain)
                    profile.description = analysis.get("description", "")
                    profile.key_differentiators = analysis.get("key_differentiators", [])
                    profile.content_themes = analysis.get("content_themes", [])
                    profile.strengths = analysis.get("strengths", [])
                    profile.weaknesses = analysis.get("weaknesses", [])
            except Exception as exc:
                self.logger.warning("LLM analysis failed for %s: %s", domain, exc)

            return profile

        # Run competitor profiling with concurrency limit
        semaphore = asyncio.Semaphore(3)

        async def _limited_profile(domain: str, relevance: float) -> CompetitorProfile | None:
            async with semaphore:
                return await _profile_competitor(domain, relevance)

        profile_tasks = [
            _limited_profile(domain, competitor_domains.get(domain, 0.5))
            for domain in top_domains
        ]
        profiles = await asyncio.gather(*profile_tasks, return_exceptions=True)

        for p in profiles:
            if isinstance(p, CompetitorProfile):
                brand.competitors.append(p)
            elif isinstance(p, Exception):
                self.logger.warning("Competitor profiling error: %s", p)

        # Phase 3: LLM synthesis - competitive landscape
        log_agent_step(self.logger, self.name, "SYNTHESIZE", "Analyzing competitive landscape")

        if brand.competitors:
            landscape_data = "\n\n".join(
                f"**{c.name}** ({c.domain}): {c.description}\n"
                f"Differentiators: {', '.join(c.key_differentiators)}\n"
                f"Strengths: {', '.join(c.strengths)}"
                for c in brand.competitors
            )

            swot_update = await self.extract_structured(
                COMPETITOR_ANALYST_SYSTEM,
                f"Brand: {brand.brand_name}\nCompetitors:\n{landscape_data}",
                """Based on the competitive landscape, identify:
{
    "opportunities": ["3-5 market opportunities for the brand"],
    "threats": ["3-5 competitive threats to watch"]
}""",
            )
            if isinstance(swot_update, dict):
                brand.swot["opportunities"] = swot_update.get("opportunities", [])
                brand.swot["threats"] = swot_update.get("threats", [])

        state.brand = brand
        log_agent_step(
            self.logger, self.name, "DONE",
            f"Profiled {len(brand.competitors)} competitors",
        )
        return state
