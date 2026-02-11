"""SEO Analyst Agent - deep SEO analysis and keyword intelligence."""

from __future__ import annotations

import asyncio
from typing import Any

from agent.agents.base import BaseAgent
from agent.models import WorkflowState
from agent.utils.logging import log_agent_step

SEO_ANALYST_SYSTEM = """You are a senior SEO strategist and analyst. Analyze domain metrics,
keyword data, and backlink profiles to provide actionable SEO intelligence. Be specific with
numbers and always tie insights to business impact."""


class SEOAnalystAgent(BaseAgent):
    """Deep SEO analysis combining DataForSEO metrics with content insights.

    Pipeline:
    1. Fetch full SEO profile (domain metrics, keywords, backlinks, tech stack)
    2. Analyze keyword gaps and opportunities
    3. Compare SEO performance against competitors
    4. Generate keyword strategy recommendations
    """

    name = "seo_analyst"
    description = "Deep SEO analysis including keywords, backlinks, and competitive benchmarking"

    async def run(self, state: WorkflowState) -> WorkflowState:
        query = state.query
        brand = state.brand
        if not brand:
            self.logger.warning("No brand profile available, skipping SEO analysis")
            return state

        dataforseo = self.skills.get("dataforseo")
        if not dataforseo:
            self.logger.warning("DataForSEO skill not available, skipping")
            return state

        # Phase 1: Get full SEO profile for brand
        log_agent_step(self.logger, self.name, "PROFILE", f"Fetching SEO profile for {query.website_url}")

        try:
            seo_profile = await dataforseo.get_full_seo_profile(query.website_url)
            brand.seo = seo_profile
            log_agent_step(
                self.logger, self.name, "METRICS",
                f"Traffic: {seo_profile.organic_traffic}, "
                f"Keywords: {seo_profile.organic_keywords}, "
                f"Backlinks: {seo_profile.backlinks_total}",
            )
        except Exception as exc:
            self.logger.warning("Full SEO profile failed: %s", exc)
            return state

        # Phase 2: Keyword expansion and suggestions
        log_agent_step(self.logger, self.name, "KEYWORDS", "Expanding keyword universe")

        seed_keywords = query.target_keywords.copy()
        if not seed_keywords and seo_profile.top_keywords:
            seed_keywords = [kw["keyword"] for kw in seo_profile.top_keywords[:5]]
        if not seed_keywords:
            seed_keywords = [query.brand_name, query.industry]

        try:
            suggestions = await dataforseo.get_keyword_suggestions(seed_keywords, limit=50)
            log_agent_step(self.logger, self.name, "SUGGESTIONS", f"Found {len(suggestions)} keyword suggestions")
        except Exception as exc:
            self.logger.warning("Keyword suggestions failed: %s", exc)
            suggestions = []

        # Phase 3: Competitor SEO comparison
        log_agent_step(self.logger, self.name, "BENCHMARK", "Comparing against competitors")

        competitor_seo_data: list[dict[str, Any]] = []
        if brand.competitors:
            semaphore = asyncio.Semaphore(3)

            async def _get_comp_seo(domain: str) -> dict[str, Any] | None:
                async with semaphore:
                    try:
                        metrics = await dataforseo.get_domain_overview(domain)
                        return {
                            "domain": domain,
                            "organic_traffic": metrics.organic_traffic,
                            "organic_keywords": metrics.organic_keywords,
                            "backlinks": metrics.backlinks_total,
                            "domain_rank": metrics.domain_rank,
                        }
                    except Exception as exc:
                        self.logger.warning("Competitor SEO fetch failed for %s: %s", domain, exc)
                        return None

            comp_tasks = [_get_comp_seo(c.domain) for c in brand.competitors[:5]]
            comp_results = await asyncio.gather(*comp_tasks)
            competitor_seo_data = [r for r in comp_results if r is not None]

        # Phase 4: LLM synthesis - SEO strategy recommendations
        log_agent_step(self.logger, self.name, "SYNTHESIZE", "Generating SEO insights")

        brand_seo_summary = (
            f"Domain: {seo_profile.domain}\n"
            f"Domain Rank: {seo_profile.domain_rank}\n"
            f"Organic Traffic: {seo_profile.organic_traffic}\n"
            f"Organic Keywords: {seo_profile.organic_keywords}\n"
            f"Backlinks: {seo_profile.backlinks_total}\n"
            f"Referring Domains: {seo_profile.referring_domains}\n"
            f"Tech Stack: {', '.join(seo_profile.tech_stack[:10])}\n"
            f"\nTop Keywords:\n"
            + "\n".join(
                f"  - {kw['keyword']} (pos: {kw.get('position')}, vol: {kw.get('search_volume')})"
                for kw in seo_profile.top_keywords[:20]
            )
        )

        comp_summary = "\n".join(
            f"  - {c['domain']}: traffic={c['organic_traffic']}, "
            f"keywords={c['organic_keywords']}, backlinks={c['backlinks']}"
            for c in competitor_seo_data
        )

        suggestions_text = "\n".join(
            f"  - {s['keyword']} (vol: {s.get('search_volume', 0)}, cpc: ${s.get('cpc', 0):.2f})"
            for s in suggestions[:30]
        )

        seo_analysis = await self.extract_structured(
            SEO_ANALYST_SYSTEM,
            f"""BRAND SEO PROFILE:\n{brand_seo_summary}\n\n
COMPETITOR SEO:\n{comp_summary}\n\n
KEYWORD OPPORTUNITIES:\n{suggestions_text}""",
            """Provide a comprehensive SEO analysis as JSON:
{
    "seo_health_score": 75,
    "key_findings": ["3-5 most important SEO findings"],
    "keyword_gaps": ["keywords competitors rank for but brand doesn't"],
    "content_opportunities": ["content topics with high search volume and low competition"],
    "technical_recommendations": ["technical SEO improvements"],
    "link_building_opportunities": ["backlink strategy recommendations"],
    "quick_wins": ["3-5 actions that could improve SEO quickly"],
    "long_term_strategy": ["3-5 strategic SEO initiatives"]
}""",
        )

        # Store SEO analysis in content analysis
        if brand.content and isinstance(seo_analysis, dict):
            brand.content.content_gaps = seo_analysis.get("content_opportunities", [])

        state.brand = brand
        log_agent_step(self.logger, self.name, "DONE", "SEO analysis complete")
        return state
