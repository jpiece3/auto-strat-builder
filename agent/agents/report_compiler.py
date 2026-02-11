"""Report Compiler Agent - synthesizes all data into a comprehensive intelligence report."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from agent.agents.base import BaseAgent
from agent.models import WorkflowState
from agent.utils.logging import log_agent_step

REPORT_SYSTEM = """You are a senior strategy consultant preparing a comprehensive brand
intelligence report for a C-level executive audience. The report should be data-driven,
visually structured with markdown, and conclude with clear strategic recommendations.
Use specific numbers and evidence from the data provided."""


class ReportCompilerAgent(BaseAgent):
    """Compiles all gathered intelligence into a polished markdown report.

    Pipeline:
    1. Aggregate all data from previous agents
    2. Use LLM to synthesize executive summary
    3. Generate section-by-section analysis
    4. Produce strategic recommendations
    5. Output final report in markdown and JSON formats
    """

    name = "report_compiler"
    description = "Compile all intelligence into a comprehensive brand strategy report"

    async def run(self, state: WorkflowState) -> WorkflowState:
        brand = state.brand
        if not brand:
            self.logger.warning("No brand data to compile")
            return state

        log_agent_step(self.logger, self.name, "COMPILE", "Generating intelligence report")

        # Build the comprehensive data bundle for LLM
        data_bundle = self._build_data_bundle(state)

        # Generate executive summary
        log_agent_step(self.logger, self.name, "EXECUTIVE_SUMMARY", "Writing executive summary")
        exec_summary = await self.llm.complete(
            REPORT_SYSTEM,
            f"""Based on this brand intelligence data, write a concise executive summary
(3-4 paragraphs) covering the brand's position, competitive landscape, and key opportunities.

{data_bundle}""",
        )

        # Generate strategic recommendations
        log_agent_step(self.logger, self.name, "RECOMMENDATIONS", "Generating strategic recommendations")
        recommendations = await self.llm.complete(
            REPORT_SYSTEM,
            f"""Based on this brand intelligence data, provide 8-10 specific, actionable
strategic recommendations organized by priority (immediate, short-term, long-term).
Each recommendation should include: the action, expected impact, and implementation notes.

{data_bundle}""",
        )

        # Generate competitive positioning analysis
        log_agent_step(self.logger, self.name, "POSITIONING", "Analyzing competitive positioning")
        positioning = await self.llm.complete(
            REPORT_SYSTEM,
            f"""Based on this brand intelligence data, write a competitive positioning analysis
that includes: market position map, key differentiators, vulnerability assessment,
and positioning opportunities.

{data_bundle}""",
        )

        # Assemble full report
        log_agent_step(self.logger, self.name, "ASSEMBLE", "Assembling final report")
        report_md = self._assemble_report(
            state=state,
            exec_summary=exec_summary,
            recommendations=recommendations,
            positioning=positioning,
        )

        # Write report files
        output_dir = self.config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = brand.brand_name.lower().replace(" ", "_")

        # Markdown report
        md_path = output_dir / f"{safe_name}_intelligence_{timestamp}.md"
        md_path.write_text(report_md, encoding="utf-8")
        self.logger.info("Report written to: %s", md_path)

        # JSON data export
        json_path = output_dir / f"{safe_name}_data_{timestamp}.json"
        json_data = self._export_json(state)
        json_path.write_text(json.dumps(json_data, indent=2, default=str), encoding="utf-8")
        self.logger.info("Data export written to: %s", json_path)

        state.report_path = str(md_path)
        log_agent_step(self.logger, self.name, "DONE", f"Report saved: {md_path}")
        return state

    def _build_data_bundle(self, state: WorkflowState) -> str:
        """Compile all workflow data into a text summary for LLM consumption."""
        brand = state.brand
        if not brand:
            return ""

        sections: list[str] = []

        # Brand overview
        sections.append(f"""## BRAND OVERVIEW
- Name: {brand.brand_name}
- Domain: {brand.domain}
- Tagline: {brand.tagline}
- Description: {brand.description}
- Value Propositions: {', '.join(brand.value_propositions)}
- Target Audience: {', '.join(brand.target_audience)}
- Brand Voice: {brand.brand_voice}
- Key Messages: {', '.join(brand.key_messages)}""")

        # SEO data
        if brand.seo:
            seo = brand.seo
            kw_text = "\n".join(
                f"  - {kw['keyword']} (pos: {kw.get('position')}, vol: {kw.get('search_volume')})"
                for kw in seo.top_keywords[:15]
            )
            sections.append(f"""## SEO PROFILE
- Domain Rank: {seo.domain_rank}
- Organic Traffic: {seo.organic_traffic:,}
- Organic Keywords: {seo.organic_keywords:,}
- Backlinks: {seo.backlinks_total:,}
- Referring Domains: {seo.referring_domains:,}
- Tech Stack: {', '.join(seo.tech_stack[:10])}
- Top Keywords:
{kw_text}""")

        # Content analysis
        if brand.content:
            sections.append(f"""## CONTENT ANALYSIS
- Total Pages Analyzed: {brand.content.total_pages}
- Content Themes: {', '.join(brand.content.content_themes)}
- Content Types: {', '.join(brand.content.content_types)}
- Content Gaps: {', '.join(brand.content.content_gaps)}""")

        # Competitors
        if brand.competitors:
            comp_entries: list[str] = []
            for c in brand.competitors:
                entry = f"""### {c.name} ({c.domain})
- Description: {c.description}
- Similarity Score: {c.similarity_score:.2f}
- Differentiators: {', '.join(c.key_differentiators)}
- Strengths: {', '.join(c.strengths)}
- Weaknesses: {', '.join(c.weaknesses)}"""
                if c.seo_metrics:
                    entry += f"""
- Organic Traffic: {c.seo_metrics.organic_traffic:,}
- Organic Keywords: {c.seo_metrics.organic_keywords:,}
- Backlinks: {c.seo_metrics.backlinks_total:,}"""
                comp_entries.append(entry)
            sections.append("## COMPETITORS\n" + "\n\n".join(comp_entries))

        # Social presence
        if brand.social:
            social_entries = "\n".join(
                f"- {s.platform}: {s.url} | {s.followers:,} followers | Sentiment: {s.sentiment}"
                for s in brand.social
            )
            sections.append(f"## SOCIAL PRESENCE\n{social_entries}")

        # SWOT
        sections.append(f"""## SWOT ANALYSIS
- Strengths: {', '.join(brand.swot.get('strengths', []))}
- Weaknesses: {', '.join(brand.swot.get('weaknesses', []))}
- Opportunities: {', '.join(brand.swot.get('opportunities', []))}
- Threats: {', '.join(brand.swot.get('threats', []))}""")

        # Market trends
        if brand.market_trends:
            sections.append(f"## MARKET TRENDS\n" + "\n".join(f"- {t}" for t in brand.market_trends))

        return "\n\n".join(sections)

    def _assemble_report(
        self,
        state: WorkflowState,
        exec_summary: str,
        recommendations: str,
        positioning: str,
    ) -> str:
        """Assemble the final markdown report."""
        brand = state.brand
        if not brand:
            return ""

        now = datetime.utcnow().strftime("%B %d, %Y")
        data_bundle = self._build_data_bundle(state)

        task_summary = "\n".join(
            f"| {t.task_name} | {t.status.value} | {t.duration_seconds}s |"
            for t in state.task_results
        )

        report = f"""# Brand Intelligence Report: {brand.brand_name}

**Generated:** {now}
**Domain:** {brand.domain}
**Industry:** {state.query.industry}
**Analysis Depth:** {state.query.depth}

---

## Executive Summary

{exec_summary}

---

{data_bundle}

---

## Competitive Positioning Analysis

{positioning}

---

## Strategic Recommendations

{recommendations}

---

## Workflow Summary

| Agent | Status | Duration |
|-------|--------|----------|
{task_summary}

---

*Report generated by Brand Intelligence Agent v0.1.0*
"""
        return report

    def _export_json(self, state: WorkflowState) -> dict[str, Any]:
        """Export all data as a JSON-serializable dictionary."""
        brand = state.brand
        if not brand:
            return {}

        def _serialize(obj: Any) -> Any:
            if hasattr(obj, "__dataclass_fields__"):
                return {k: _serialize(v) for k, v in obj.__dict__.items()}
            if isinstance(obj, list):
                return [_serialize(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _serialize(v) for k, v in obj.items()}
            return obj

        return {
            "query": _serialize(state.query),
            "brand": _serialize(brand),
            "workflow": {
                "status": state.status.value,
                "started_at": state.started_at,
                "completed_at": state.completed_at,
                "task_results": [_serialize(t) for t in state.task_results],
                "errors": state.errors,
            },
        }
