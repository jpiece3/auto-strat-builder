"""Brand Intelligence Workflow - orchestrates the full autonomous pipeline."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any

from agent.agents.brand_discovery import BrandDiscoveryAgent
from agent.agents.competitor_intel import CompetitorIntelAgent
from agent.agents.report_compiler import ReportCompilerAgent
from agent.agents.seo_analyst import SEOAnalystAgent
from agent.agents.web_presence import WebPresenceAgent
from agent.config import AgentConfig
from agent.models import BrandQuery, TaskStatus, WorkflowState
from agent.skills.branddev_skill import BrandDevSkill
from agent.skills.dataforseo_skill import DataForSEOSkill
from agent.skills.firecrawl_skill import FirecrawlSkill
from agent.skills.playwright_skill import PlaywrightSkill
from agent.skills.tavily_skill import TavilySkill
from agent.utils.logging import get_logger

logger = get_logger("workflow.brand_intelligence")


class BrandIntelligenceWorkflow:
    """Autonomous workflow that orchestrates the full brand intelligence pipeline.

    Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    Brand Intelligence Workflow               │
    │                                                             │
    │  ┌─────────────┐                                            │
    │  │   Brand      │── Phase 1: Research the target brand      │
    │  │  Discovery   │                                           │
    │  └──────┬───────┘                                           │
    │         │                                                   │
    │  ┌──────┴───────┐  ┌─────────────┐  ┌─────────────┐        │
    │  │  Competitor   │  │    SEO       │  │    Web       │       │
    │  │    Intel      │  │   Analyst    │  │  Presence    │       │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
    │         │                 │                  │  Phase 2:     │
    │         │                 │                  │  Parallel     │
    │         └─────────────────┴─────────────────┘  Analysis     │
    │                           │                                 │
    │                    ┌──────┴───────┐                          │
    │                    │   Report      │── Phase 3: Synthesis    │
    │                    │  Compiler     │                         │
    │                    └──────────────┘                          │
    └─────────────────────────────────────────────────────────────┘

    Skills used:
    - Firecrawl: Website crawling and content extraction
    - Tavily: AI-powered search and research
    - Playwright: Browser automation for dynamic content
    - DataForSEO: SEO analytics and competitive data
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self._skills: dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> list[str]:
        """Initialize all skills and return any warnings."""
        warnings = self.config.validate()

        # Initialize skills (gracefully handle missing API keys)
        if self.config.firecrawl.api_key:
            self._skills["firecrawl"] = FirecrawlSkill(self.config.firecrawl)
        else:
            logger.warning("Firecrawl skill disabled: no API key")

        if self.config.tavily.api_key:
            self._skills["tavily"] = TavilySkill(self.config.tavily)
        else:
            logger.warning("Tavily skill disabled: no API key")

        if self.config.dataforseo.login:
            self._skills["dataforseo"] = DataForSEOSkill(self.config.dataforseo)
        else:
            logger.warning("DataForSEO skill disabled: no credentials")

        if self.config.branddev.api_key:
            self._skills["branddev"] = BrandDevSkill(self.config.branddev)
        else:
            logger.warning("brand.dev skill disabled: no API key — reports will use fallback theme")

        # Playwright doesn't need an API key
        self._skills["playwright"] = PlaywrightSkill(self.config.playwright)

        self._initialized = True
        logger.info(
            "Workflow initialized with %d skills: %s",
            len(self._skills),
            list(self._skills.keys()),
        )
        return warnings

    async def run(self, query: BrandQuery) -> WorkflowState:
        """Execute the full brand intelligence pipeline autonomously."""
        if not self._initialized:
            await self.initialize()

        state = WorkflowState(query=query)
        state.status = TaskStatus.RUNNING
        start_time = time.monotonic()

        logger.info(
            "Starting brand intelligence workflow for: %s (%s)",
            query.brand_name,
            query.website_url,
        )
        logger.info("Depth: %s | Industry: %s", query.depth, query.industry)
        logger.info("Known competitors: %s", query.known_competitors)
        logger.info("Active skills: %s", list(self._skills.keys()))

        try:
            # ── Phase 1: Brand Discovery (sequential - other agents depend on it) ──
            logger.info("═══ Phase 1: Brand Discovery ═══")
            brand_agent = BrandDiscoveryAgent(self.config, self._skills)
            state = await brand_agent.execute(state)

            if not state.brand:
                logger.error("Brand discovery failed, aborting workflow")
                state.status = TaskStatus.FAILED
                return state

            # ── Phase 2: Parallel Analysis ──────────────────────────────────────
            logger.info("═══ Phase 2: Parallel Analysis (Competitor + SEO + Web Presence) ═══")

            parallel_agents = []

            competitor_agent = CompetitorIntelAgent(self.config, self._skills)
            parallel_agents.append(("competitor_intel", competitor_agent))

            if "dataforseo" in self._skills:
                seo_agent = SEOAnalystAgent(self.config, self._skills)
                parallel_agents.append(("seo_analyst", seo_agent))

            web_agent = WebPresenceAgent(self.config, self._skills)
            parallel_agents.append(("web_presence", web_agent))

            # Run parallel agents - each operates on a copy of state then merges
            async def _run_agent(name: str, agent: Any, s: WorkflowState) -> WorkflowState:
                logger.info("Starting parallel agent: %s", name)
                return await agent.execute(s)

            # We run them on the same state object; agents write to different
            # sections of brand profile so there's no conflict
            parallel_tasks = [
                _run_agent(name, agent, state)
                for name, agent in parallel_agents
            ]
            results = await asyncio.gather(*parallel_tasks, return_exceptions=True)

            # Merge results back - take the latest state and merge task results
            for result in results:
                if isinstance(result, WorkflowState):
                    # Merge task results
                    for tr in result.task_results:
                        if tr not in state.task_results:
                            state.task_results.append(tr)
                    # Merge brand data (each agent writes to different fields)
                    if result.brand and state.brand:
                        if result.brand.competitors:
                            state.brand.competitors = result.brand.competitors
                        if result.brand.seo:
                            state.brand.seo = result.brand.seo
                        if result.brand.social:
                            state.brand.social = result.brand.social
                        if result.brand.content and result.brand.content.content_gaps:
                            if state.brand.content:
                                state.brand.content.content_gaps = result.brand.content.content_gaps
                        # Merge SWOT
                        for key in ("opportunities", "threats"):
                            if result.brand.swot.get(key):
                                state.brand.swot[key] = result.brand.swot[key]
                    state.errors.extend(result.errors)
                elif isinstance(result, Exception):
                    logger.error("Parallel agent failed: %s", result)
                    state.errors.append(str(result))

            # ── Phase 3: Report Compilation ─────────────────────────────────────
            logger.info("═══ Phase 3: Report Compilation ═══")
            report_agent = ReportCompilerAgent(self.config, self._skills)
            state = await report_agent.execute(state)

            # ── Finalize ────────────────────────────────────────────────────────
            duration = time.monotonic() - start_time
            state.status = TaskStatus.COMPLETED
            state.completed_at = datetime.utcnow().isoformat()

            logger.info("═══ Workflow Complete ═══")
            logger.info("Duration: %.1fs", duration)
            logger.info("Report: %s", state.report_path)
            logger.info("Tasks: %d completed, %d failed",
                sum(1 for t in state.task_results if t.status == TaskStatus.COMPLETED),
                sum(1 for t in state.task_results if t.status == TaskStatus.FAILED),
            )
            if state.errors:
                logger.warning("Errors encountered: %s", state.errors)

        except Exception as exc:
            state.status = TaskStatus.FAILED
            state.completed_at = datetime.utcnow().isoformat()
            state.errors.append(f"Workflow error: {exc}")
            logger.error("Workflow failed: %s", exc, exc_info=True)

        finally:
            await self.cleanup()

        return state

    async def cleanup(self) -> None:
        """Release all skill resources."""
        for name, skill in self._skills.items():
            try:
                await skill.close()
            except Exception as exc:
                logger.warning("Error closing skill %s: %s", name, exc)
