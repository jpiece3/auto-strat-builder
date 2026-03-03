"""Web Presence Agent - social media and online presence analysis."""

from __future__ import annotations

import asyncio
from typing import Any

from agent.agents.base import BaseAgent
from agent.models import SocialPresence, WorkflowState
from agent.utils.logging import log_agent_step

SOCIAL_ANALYST_SYSTEM = """You are a social media and digital presence analyst. Analyze social
profiles, online reviews, and brand mentions to assess a brand's digital footprint. Provide
specific, actionable insights about engagement, reach, and reputation."""


class WebPresenceAgent(BaseAgent):
    """Analyzes social media profiles and broader web presence.

    Pipeline:
    1. Discover social media profiles via search
    2. Scrape social profiles for metrics (followers, engagement)
    3. Search for reviews and reputation signals
    4. LLM synthesis for web presence assessment
    """

    name = "web_presence"
    description = "Analyze social media profiles and broader digital presence"

    async def run(self, state: WorkflowState) -> WorkflowState:
        query = state.query
        brand = state.brand
        if not brand:
            self.logger.warning("No brand profile, skipping web presence analysis")
            return state

        tavily = self.skills.get("tavily")
        playwright = self.skills.get("playwright")

        # Phase 1: Discover social profiles
        log_agent_step(self.logger, self.name, "DISCOVER", "Finding social media profiles")

        known_profiles = query.social_profiles.copy()
        if tavily and len(known_profiles) < 4:
            try:
                social_results = await tavily.search(
                    f"{query.brand_name} official social media profiles",
                    max_results=10,
                )
                discovered = await self.extract_structured(
                    SOCIAL_ANALYST_SYSTEM,
                    "\n".join(f"- {r.title}: {r.url}" for r in social_results),
                    f"""Find official social media profile URLs for "{query.brand_name}".
Return JSON: {{"profiles": {{"linkedin": "url", "twitter": "url", "facebook": "url", "instagram": "url", "youtube": "url"}}}}
Only include URLs that appear to be the brand's official profiles. Use empty string for unknown.""",
                )
                if isinstance(discovered, dict):
                    for platform, url in discovered.get("profiles", {}).items():
                        if url and platform not in known_profiles:
                            known_profiles[platform] = url
            except Exception as exc:
                self.logger.warning("Social profile discovery failed: %s", exc)

        log_agent_step(self.logger, self.name, "PROFILES", f"Found {len(known_profiles)} social profiles")

        # Phase 2: Scrape social profiles
        social_data: list[SocialPresence] = []
        if playwright and known_profiles:
            log_agent_step(self.logger, self.name, "SCRAPE", "Scraping social profiles")

            async def _scrape_profile(platform: str, url: str) -> SocialPresence | None:
                try:
                    return await playwright.scrape_social_profile(platform, url)
                except Exception as exc:
                    self.logger.warning("Failed to scrape %s: %s", platform, exc)
                    return SocialPresence(platform=platform, url=url)

            tasks = [_scrape_profile(p, u) for p, u in known_profiles.items() if u]
            results = await asyncio.gather(*tasks)
            social_data = [r for r in results if r is not None]

        # Phase 3: Search for reviews and reputation
        log_agent_step(self.logger, self.name, "REPUTATION", "Analyzing online reputation")

        review_data: list[dict[str, str]] = []
        if tavily:
            try:
                review_queries = [
                    f'"{query.brand_name}" reviews',
                    f"{query.brand_name} customer experience",
                    f"{query.brand_name} trustpilot OR g2 OR capterra",
                ]
                for q in review_queries:
                    results = await tavily.search(q, max_results=5)
                    for r in results:
                        review_data.append({
                            "title": r.title,
                            "url": r.url,
                            "snippet": r.snippet,
                        })
            except Exception as exc:
                self.logger.warning("Review search failed: %s", exc)

        # Phase 4: Search for recent news
        news_data: list[dict[str, str]] = []
        if tavily:
            try:
                news = await tavily.search_news(f"{query.brand_name}", max_results=10)
                news_data = [{"title": n.title, "url": n.url, "snippet": n.snippet} for n in news]
            except Exception as exc:
                self.logger.warning("News search failed: %s", exc)

        # Phase 5: LLM synthesis
        log_agent_step(self.logger, self.name, "SYNTHESIZE", "Building web presence assessment")

        social_summary = "\n".join(
            f"- {s.platform}: {s.url} ({s.followers} followers)" for s in social_data
        )
        review_summary = "\n".join(
            f"- {r['title']}: {r['snippet'][:200]}" for r in review_data[:10]
        )
        news_summary = "\n".join(
            f"- {n['title']}: {n['snippet'][:200]}" for n in news_data[:10]
        )

        presence_analysis = await self.extract_structured(
            SOCIAL_ANALYST_SYSTEM,
            f"""Brand: {query.brand_name}

SOCIAL PROFILES:
{social_summary}

REVIEWS & REPUTATION:
{review_summary}

RECENT NEWS:
{news_summary}""",
            """Analyze the brand's digital presence and return JSON:
{
    "presence_score": 75,
    "social_assessment": "overall social media presence assessment",
    "reputation_sentiment": "positive|neutral|mixed|negative",
    "reputation_summary": "2-3 sentence summary of online reputation",
    "top_platforms": ["ranked list of strongest social platforms"],
    "platform_recommendations": ["platforms they should focus on or improve"],
    "content_recommendations": ["social content strategy suggestions"],
    "reputation_risks": ["potential reputation concerns"],
    "news_sentiment": "positive|neutral|mixed|negative",
    "key_narratives": ["dominant themes in news/press coverage"]
}""",
        )

        # Update brand profile
        brand.social = social_data

        if isinstance(presence_analysis, dict):
            # Enrich social presence objects with analysis
            for sp in brand.social:
                sp.sentiment = presence_analysis.get("reputation_sentiment", "")

        state.brand = brand
        log_agent_step(self.logger, self.name, "DONE", "Web presence analysis complete")
        return state
