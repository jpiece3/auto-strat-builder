"""Brand Discovery Agent - researches and profiles the target brand."""

from __future__ import annotations

import asyncio
from typing import Any

from agent.agents.base import BaseAgent
from agent.models import BrandProfile, ContentAnalysis, WebPage, WorkflowState
from agent.utils.logging import log_agent_step

BRAND_ANALYST_SYSTEM = """You are a senior brand strategist and market analyst. Your job is to
analyze website content, search results, and public information to build a comprehensive
brand profile. Be specific, data-driven, and objective. Identify both strengths and weaknesses."""


class BrandDiscoveryAgent(BaseAgent):
    """Discovers and profiles the target brand using website crawling and search.

    Pipeline:
    1. Crawl the brand's website to extract content, structure, and messaging
    2. Search for brand mentions, reviews, and press coverage
    3. Use LLM to synthesize a complete brand profile
    """

    name = "brand_discovery"
    description = "Research and profile the target brand from web presence and public data"

    async def run(self, state: WorkflowState) -> WorkflowState:
        query = state.query
        firecrawl = self.skills.get("firecrawl")
        tavily = self.skills.get("tavily")

        # Initialize brand profile
        brand = BrandProfile(
            brand_name=query.brand_name,
            domain=query.website_url,
        )

        # Phase 1: Crawl the brand's website
        log_agent_step(self.logger, self.name, "CRAWL", f"Crawling {query.website_url}")
        pages: list[WebPage] = []
        if firecrawl:
            try:
                # Scrape key pages first (fast)
                homepage = await firecrawl.scrape_page(query.website_url)
                pages.append(homepage)

                # Discover sitemap to find important pages
                sitemap_urls = await firecrawl.discover_sitemap(query.website_url)
                priority_paths = [
                    u for u in sitemap_urls
                    if any(kw in u.lower() for kw in [
                        "about", "product", "service", "pricing", "blog",
                        "case-stud", "testimonial", "team", "mission", "feature",
                    ])
                ][:15]

                if priority_paths:
                    crawled = await firecrawl.crawl_site(
                        query.website_url,
                        max_pages=min(len(priority_paths), 20),
                        include_paths=[p.replace(query.website_url, "") for p in priority_paths],
                    )
                    pages.extend(crawled)
                elif query.depth == "comprehensive":
                    crawled = await firecrawl.crawl_site(query.website_url, max_pages=30)
                    pages.extend(crawled)

            except Exception as exc:
                self.logger.warning("Firecrawl error, falling back to Playwright: %s", exc)
                playwright = self.skills.get("playwright")
                if playwright:
                    homepage = await playwright.render_page(query.website_url)
                    pages.append(homepage)

        brand.pages = pages

        # Phase 2: Extract structured brand info from homepage
        log_agent_step(self.logger, self.name, "EXTRACT", "Extracting brand identity from website")
        if firecrawl:
            try:
                extracted = await firecrawl.extract_structured(
                    query.website_url,
                    schema={
                        "type": "object",
                        "properties": {
                            "tagline": {"type": "string"},
                            "description": {"type": "string"},
                            "value_propositions": {"type": "array", "items": {"type": "string"}},
                            "target_audience": {"type": "array", "items": {"type": "string"}},
                            "key_messages": {"type": "array", "items": {"type": "string"}},
                            "products_services": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    prompt="Extract the brand's core identity, value propositions, target audience, and key messaging.",
                )
                brand.tagline = extracted.get("tagline", "")
                brand.description = extracted.get("description", "")
                brand.value_propositions = extracted.get("value_propositions", [])
                brand.target_audience = extracted.get("target_audience", [])
                brand.key_messages = extracted.get("key_messages", [])
            except Exception as exc:
                self.logger.warning("Structured extraction failed: %s", exc)

        # Phase 3: Search for brand mentions and sentiment
        log_agent_step(self.logger, self.name, "RESEARCH", "Searching brand mentions and press")
        mentions = []
        if tavily:
            try:
                mentions = await tavily.find_brand_mentions(query.brand_name, query.website_url)
            except Exception as exc:
                self.logger.warning("Brand mention search failed: %s", exc)

        # Phase 4: LLM synthesis - build complete brand profile
        log_agent_step(self.logger, self.name, "SYNTHESIZE", "Building brand profile via LLM")

        page_content = "\n\n---\n\n".join(
            f"URL: {p.url}\nTitle: {p.title}\n{p.content[:2000]}" for p in pages[:10]
        )
        mentions_text = "\n".join(
            f"- {m.title}: {m.snippet}" for m in mentions[:15]
        )

        profile_data = await self.extract_structured(
            BRAND_ANALYST_SYSTEM,
            f"""WEBSITE CONTENT:\n{page_content}\n\nBRAND MENTIONS & REVIEWS:\n{mentions_text}""",
            """Analyze this brand and return a JSON object with:
{
    "tagline": "the brand's primary tagline or slogan",
    "description": "2-3 sentence brand description",
    "value_propositions": ["list of 3-5 core value props"],
    "target_audience": ["list of target audience segments"],
    "brand_voice": "description of brand tone/voice",
    "key_messages": ["list of 3-5 key marketing messages"],
    "content_themes": ["list of main content topics/themes"],
    "content_types": ["list of content formats used (blog, video, etc.)"],
    "market_trends": ["3-5 relevant market/industry trends"],
    "strengths": ["3-5 brand strengths"],
    "weaknesses": ["3-5 brand weaknesses or gaps"]
}""",
        )

        # Merge LLM insights with extracted data
        if isinstance(profile_data, dict):
            brand.tagline = brand.tagline or profile_data.get("tagline", "")
            brand.description = brand.description or profile_data.get("description", "")
            brand.value_propositions = brand.value_propositions or profile_data.get("value_propositions", [])
            brand.target_audience = brand.target_audience or profile_data.get("target_audience", [])
            brand.brand_voice = profile_data.get("brand_voice", "")
            brand.key_messages = brand.key_messages or profile_data.get("key_messages", [])
            brand.market_trends = profile_data.get("market_trends", [])
            brand.content = ContentAnalysis(
                total_pages=len(pages),
                content_themes=profile_data.get("content_themes", []),
                content_types=profile_data.get("content_types", []),
            )
            brand.swot["strengths"] = profile_data.get("strengths", [])
            brand.swot["weaknesses"] = profile_data.get("weaknesses", [])

        state.brand = brand
        log_agent_step(self.logger, self.name, "DONE", f"Profiled {brand.brand_name} ({len(pages)} pages)")
        return state
