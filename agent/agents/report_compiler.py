"""Report Compiler Agent - synthesizes all data into a comprehensive intelligence report."""

from __future__ import annotations

import base64
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

CRITICAL MARKDOWN FORMATTING RULES:
1. Use markdown numbering (1., 2., 3.) for numbered lists, NOT hashtags (#)
2. For sub-sections within numbered items, use markdown headings (###) or bold text (**text**)
3. For nested lists, use proper indentation with hyphens (-) for bullets
4. Never use # symbols within list items - they create headings, not list numbers

Example format:
1. **Priority 1: Action Name (Timeframe)**
   - **Action:** What to do
   - **Expected Impact:** Results
   - **Implementation:** How to execute

{data_bundle}""",
        )

        # Generate competitive positioning analysis
        log_agent_step(self.logger, self.name, "POSITIONING", "Analyzing competitive positioning")
        positioning = await self.llm.complete(
            REPORT_SYSTEM,
            f"""Based on this brand intelligence data, write a competitive positioning analysis
that includes: market position map, key differentiators, vulnerability assessment,
and positioning opportunities.

CRITICAL MARKDOWN FORMATTING RULES:
1. For tables, ALWAYS include a header separator row with pipes and dashes:
   | Column 1 | Column 2 |
   |----------|----------|
   | Data     | Data     |

2. For numbered lists, use markdown numbering (1., 2., 3.) NOT hashtags (#):
   1. First item
   2. Second item
      - Sub-bullet (use hyphens for bullets)

3. For ASCII art diagrams, use triple backticks with no language specified:
   ```
   ASCII diagram here
   ```

4. Use proper markdown headings (##, ###) only for section titles, never for list items.

5. Bold text uses **double asterisks**, not single.

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

        # HTML report
        html_path = output_dir / f"{safe_name}_intelligence_{timestamp}.html"
        html_content = self._generate_html_report(
            state=state,
            exec_summary=exec_summary,
            recommendations=recommendations,
            positioning=positioning,
        )
        html_path.write_text(html_content, encoding="utf-8")
        self.logger.info("HTML report written to: %s", html_path)

        state.report_path = str(md_path)
        state.html_report_path = str(html_path)  # Store HTML path in state
        log_agent_step(self.logger, self.name, "DONE", f"Reports saved: {md_path}, {html_path}")
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

    def _generate_html_report(
        self,
        state: WorkflowState,
        exec_summary: str,
        recommendations: str,
        positioning: str,
    ) -> str:
        """Generate a professionally styled HTML report with Brothers Automate branding."""
        brand = state.brand
        if not brand:
            return ""

        now = datetime.utcnow().strftime("%B %d, %Y")

        # Read and encode Brothers Automate logo
        logo_base64 = self._encode_logo()

        # Build HTML sections
        brand_overview_html = self._format_brand_overview_html(brand)
        seo_profile_html = self._format_seo_profile_html(brand)
        content_analysis_html = self._format_content_analysis_html(brand)
        competitors_html = self._format_competitors_html(brand)
        social_presence_html = self._format_social_presence_html(brand)
        swot_html = self._format_swot_html(brand)
        market_trends_html = self._format_market_trends_html(brand)
        workflow_summary_html = self._format_workflow_summary_html(state)

        # Convert markdown-style content to HTML paragraphs
        exec_summary_html = self._markdown_to_html(exec_summary)
        recommendations_html = self._markdown_to_html(recommendations)
        positioning_html = self._markdown_to_html(positioning)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brand Intelligence Report - {brand.brand_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --navy: #1a365d;
            --navy-light: #2c5282;
            --orange: #ed8936;
            --orange-dark: #dd6b20;
            --slate: #fdfcfa;
            --white: #ffffff;
            --blue: #3182ce;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --border: #e8e6e1;
            --success: #16a34a;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--navy);
            background: var(--slate);
            padding: 2rem 1rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: var(--white);
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}

        header {{
            background: var(--navy);
            color: var(--white);
            padding: 2.5rem 3rem;
            border-bottom: 4px solid var(--orange);
        }}

        header img {{
            max-width: 200px;
            height: auto;
            margin-bottom: 1rem;
        }}

        .tagline {{
            color: var(--orange);
            font-size: 1.125rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}

        .report-meta {{
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            font-size: 0.875rem;
        }}

        .report-meta-item {{
            display: flex;
            flex-direction: column;
        }}

        .report-meta-label {{
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.75rem;
            margin-bottom: 0.25rem;
        }}

        .report-meta-value {{
            color: var(--white);
            font-weight: 600;
            font-size: 1rem;
        }}

        main {{
            padding: 3rem;
        }}

        h1 {{
            color: var(--navy);
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }}

        h2 {{
            color: var(--navy);
            font-size: 1.875rem;
            font-weight: 700;
            margin: 3rem 0 1.5rem 0;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid var(--orange);
        }}

        h3 {{
            color: var(--navy-light);
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
        }}

        h4 {{
            color: var(--navy);
            font-size: 1.125rem;
            font-weight: 600;
            margin: 1.5rem 0 0.75rem 0;
        }}

        p {{
            color: var(--text-secondary);
            margin-bottom: 1rem;
            line-height: 1.7;
        }}

        ul, ol {{
            margin-left: 1.5rem;
            margin-bottom: 1rem;
            color: var(--text-secondary);
        }}

        li {{
            margin-bottom: 0.5rem;
            line-height: 1.7;
        }}

        .card {{
            background: var(--white);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 1.5rem 0;
        }}

        .stat-card {{
            background: linear-gradient(145deg, #ffffff 0%, #f8f7f4 100%);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1.5rem;
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}

        .stat-value {{
            color: var(--navy);
            font-size: 2rem;
            font-weight: 700;
        }}

        .stat-unit {{
            color: var(--text-muted);
            font-size: 1rem;
            font-weight: 400;
            margin-left: 0.25rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.875rem;
        }}

        th {{
            background: var(--navy);
            color: var(--white);
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.75rem;
        }}

        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
            color: var(--text-secondary);
        }}

        tr:hover {{
            background: rgba(237, 137, 54, 0.05);
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .badge-primary {{
            background: var(--orange);
            color: var(--white);
        }}

        .badge-secondary {{
            background: var(--blue);
            color: var(--white);
        }}

        .badge-success {{
            background: var(--success);
            color: var(--white);
        }}

        .swot-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            margin: 1.5rem 0;
        }}

        .swot-section {{
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1.5rem;
        }}

        .swot-section h4 {{
            margin-top: 0;
            color: var(--orange);
        }}

        .divider {{
            height: 1px;
            background: var(--border);
            margin: 3rem 0;
        }}

        footer {{
            background: #f8f7f4;
            padding: 2rem 3rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
            border-top: 1px solid var(--border);
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}

            h2 {{
                page-break-after: avoid;
            }}

            .card, .stat-card {{
                page-break-inside: avoid;
            }}
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 0;
            }}

            header, main, footer {{
                padding: 1.5rem;
            }}

            h1 {{
                font-size: 2rem;
            }}

            h2 {{
                font-size: 1.5rem;
            }}

            .card-grid, .swot-grid {{
                grid-template-columns: 1fr;
            }}

            .report-meta {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            {f'<img src="data:image/png;base64,{logo_base64}" alt="Brothers Automate">' if logo_base64 else ''}
            <div class="tagline">Simple AI. Smart Results.</div>

            <div class="report-meta">
                <div class="report-meta-item">
                    <span class="report-meta-label">Brand Name</span>
                    <span class="report-meta-value">{brand.brand_name}</span>
                </div>
                <div class="report-meta-item">
                    <span class="report-meta-label">Domain</span>
                    <span class="report-meta-value">{brand.domain}</span>
                </div>
                <div class="report-meta-item">
                    <span class="report-meta-label">Industry</span>
                    <span class="report-meta-value">{state.query.industry}</span>
                </div>
                <div class="report-meta-item">
                    <span class="report-meta-label">Generated</span>
                    <span class="report-meta-value">{now}</span>
                </div>
            </div>
        </header>

        <main>
            <h2>Executive Summary</h2>
            {exec_summary_html}

            <div class="divider"></div>

            <h2>Brand Overview</h2>
            {brand_overview_html}

            <div class="divider"></div>

            <h2>SEO Profile</h2>
            {seo_profile_html}

            <div class="divider"></div>

            <h2>Content Analysis</h2>
            {content_analysis_html}

            <div class="divider"></div>

            <h2>Competitors</h2>
            {competitors_html}

            <div class="divider"></div>

            <h2>Social Presence</h2>
            {social_presence_html}

            <div class="divider"></div>

            <h2>SWOT Analysis</h2>
            {swot_html}

            <div class="divider"></div>

            <h2>Market Trends</h2>
            {market_trends_html}

            <div class="divider"></div>

            <h2>Competitive Positioning Analysis</h2>
            {positioning_html}

            <div class="divider"></div>

            <h2>Strategic Recommendations</h2>
            {recommendations_html}

            <div class="divider"></div>

            <h2>Workflow Summary</h2>
            {workflow_summary_html}
        </main>

        <footer>
            <p>Report generated by <strong>Brothers Automate Intelligence Agent v0.1.0</strong></p>
            <p style="margin-top: 0.5rem;">Confidential - For internal use only</p>
        </footer>
    </div>
</body>
</html>"""
        return html

    def _encode_logo(self) -> str:
        """Read and base64 encode the Brothers Automate logo."""
        # Try multiple possible logo locations
        logo_paths = [
            Path("/Users/jamespinder/brothers-automate/website/public/logo.png"),
            Path.home() / "brothers-automate" / "website" / "public" / "logo.png",
            Path(__file__).parent.parent.parent / "assets" / "logo.png",
        ]

        for logo_path in logo_paths:
            if logo_path.exists():
                try:
                    with open(logo_path, "rb") as f:
                        logo_bytes = f.read()
                    return base64.b64encode(logo_bytes).decode("utf-8")
                except Exception as e:
                    self.logger.warning(f"Failed to encode logo from {logo_path}: {e}")
                    continue

        self.logger.warning("No logo found at any expected location")
        return ""

    def _markdown_to_html(self, text: str) -> str:
        """Convert markdown-style text to HTML paragraphs."""
        if not text:
            return ""

        # Split by double newlines to get paragraphs
        paragraphs = text.strip().split("\n\n")
        html_parts = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if it's a heading
            if para.startswith("###"):
                heading_text = para[3:].strip()
                html_parts.append(f"<h4>{heading_text}</h4>")
            elif para.startswith("##"):
                heading_text = para[2:].strip()
                html_parts.append(f"<h3>{heading_text}</h3>")
            # Check if it's a list
            elif para.startswith("- ") or para.startswith("* ") or para.startswith("1."):
                items = [line.strip() for line in para.split("\n") if line.strip()]
                is_ordered = items[0][0].isdigit()
                list_tag = "ol" if is_ordered else "ul"
                li_items = []
                for item in items:
                    # Remove list markers
                    if item.startswith("- ") or item.startswith("* "):
                        item = item[2:]
                    elif item[0].isdigit() and item[1] in [".", ")"]:
                        item = item[item.index(" ") + 1:]
                    li_items.append(f"<li>{item}</li>")
                html_parts.append(f"<{list_tag}>{''.join(li_items)}</{list_tag}>")
            else:
                # Regular paragraph
                html_parts.append(f"<p>{para}</p>")

        return "\n".join(html_parts)

    def _format_brand_overview_html(self, brand) -> str:
        """Format brand overview section as HTML."""
        return f"""
        <div class="card">
            <h4>Brand Identity</h4>
            <p><strong>Tagline:</strong> {brand.tagline}</p>
            <p><strong>Description:</strong> {brand.description}</p>
        </div>

        <div class="card-grid">
            <div class="stat-card">
                <div class="stat-label">Value Propositions</div>
                <ul>
                    {''.join(f'<li>{vp}</li>' for vp in brand.value_propositions)}
                </ul>
            </div>

            <div class="stat-card">
                <div class="stat-label">Target Audience</div>
                <ul>
                    {''.join(f'<li>{ta}</li>' for ta in brand.target_audience)}
                </ul>
            </div>

            <div class="stat-card">
                <div class="stat-label">Brand Voice</div>
                <p style="margin: 0;">{brand.brand_voice}</p>
            </div>
        </div>

        <div class="card">
            <h4>Key Messages</h4>
            <ul>
                {''.join(f'<li>{msg}</li>' for msg in brand.key_messages)}
            </ul>
        </div>
        """

    def _format_seo_profile_html(self, brand) -> str:
        """Format SEO profile section as HTML."""
        if not brand.seo:
            return "<p>No SEO data available.</p>"

        seo = brand.seo
        return f"""
        <div class="card-grid">
            <div class="stat-card">
                <div class="stat-label">Domain Rank</div>
                <div class="stat-value">{seo.domain_rank:,}</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Organic Traffic</div>
                <div class="stat-value">{seo.organic_traffic:,}</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Organic Keywords</div>
                <div class="stat-value">{seo.organic_keywords:,}</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Backlinks</div>
                <div class="stat-value">{seo.backlinks_total:,}</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Referring Domains</div>
                <div class="stat-value">{seo.referring_domains:,}</div>
            </div>
        </div>

        <div class="card">
            <h4>Top Keywords</h4>
            <table>
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>Position</th>
                        <th>Search Volume</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'''<tr>
                        <td>{kw['keyword']}</td>
                        <td>{kw.get('position', 'N/A')}</td>
                        <td>{kw.get('search_volume', 'N/A'):,}</td>
                    </tr>''' for kw in seo.top_keywords[:15])}
                </tbody>
            </table>
        </div>

        {f'''<div class="card">
            <h4>Technology Stack</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                {''.join(f'<span class="badge badge-secondary">{tech}</span>' for tech in seo.tech_stack[:15])}
            </div>
        </div>''' if seo.tech_stack else ''}
        """

    def _format_content_analysis_html(self, brand) -> str:
        """Format content analysis section as HTML."""
        if not brand.content:
            return "<p>No content analysis data available.</p>"

        content = brand.content
        return f"""
        <div class="card-grid">
            <div class="stat-card">
                <div class="stat-label">Total Pages Analyzed</div>
                <div class="stat-value">{content.total_pages}</div>
            </div>
        </div>

        <div class="card">
            <h4>Content Themes</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                {''.join(f'<span class="badge badge-primary">{theme}</span>' for theme in content.content_themes)}
            </div>
        </div>

        <div class="card">
            <h4>Content Types</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                {''.join(f'<span class="badge badge-secondary">{ct}</span>' for ct in content.content_types)}
            </div>
        </div>

        {f'''<div class="card">
            <h4>Content Gaps</h4>
            <ul>
                {''.join(f'<li>{gap}</li>' for gap in content.content_gaps)}
            </ul>
        </div>''' if content.content_gaps else ''}
        """

    def _format_competitors_html(self, brand) -> str:
        """Format competitors section as HTML."""
        if not brand.competitors:
            return "<p>No competitor data available.</p>"

        comp_cards = []
        for c in brand.competitors:
            seo_metrics_html = ""
            if c.seo_metrics:
                seo_metrics_html = f"""
                <div class="card-grid" style="margin-top: 1rem;">
                    <div class="stat-card">
                        <div class="stat-label">Organic Traffic</div>
                        <div class="stat-value">{c.seo_metrics.organic_traffic:,}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Organic Keywords</div>
                        <div class="stat-value">{c.seo_metrics.organic_keywords:,}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Backlinks</div>
                        <div class="stat-value">{c.seo_metrics.backlinks_total:,}</div>
                    </div>
                </div>
                """

            comp_cards.append(f"""
            <div class="card">
                <h3>{c.name} <span class="badge badge-primary">Similarity: {c.similarity_score:.1%}</span></h3>
                <p><strong>Domain:</strong> <a href="https://{c.domain}" target="_blank">{c.domain}</a></p>
                <p>{c.description}</p>

                <div style="margin-top: 1rem;">
                    <h4>Key Differentiators</h4>
                    <ul>
                        {''.join(f'<li>{diff}</li>' for diff in c.key_differentiators)}
                    </ul>
                </div>

                <div style="margin-top: 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <h4 style="color: var(--success);">Strengths</h4>
                        <ul>
                            {''.join(f'<li>{s}</li>' for s in c.strengths)}
                        </ul>
                    </div>
                    <div>
                        <h4 style="color: var(--orange);">Weaknesses</h4>
                        <ul>
                            {''.join(f'<li>{w}</li>' for w in c.weaknesses)}
                        </ul>
                    </div>
                </div>

                {seo_metrics_html}
            </div>
            """)

        return "\n".join(comp_cards)

    def _format_social_presence_html(self, brand) -> str:
        """Format social presence section as HTML."""
        if not brand.social:
            return "<p>No social presence data available.</p>"

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Platform</th>
                    <th>URL</th>
                    <th>Followers</th>
                    <th>Sentiment</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f'''<tr>
                    <td><span class="badge badge-secondary">{s.platform}</span></td>
                    <td><a href="{s.url}" target="_blank">{s.url}</a></td>
                    <td>{s.followers:,}</td>
                    <td>{s.sentiment}</td>
                </tr>''' for s in brand.social)}
            </tbody>
        </table>
        """

    def _format_swot_html(self, brand) -> str:
        """Format SWOT analysis as HTML."""
        swot = brand.swot
        return f"""
        <div class="swot-grid">
            <div class="swot-section">
                <h4 style="color: var(--success);">Strengths</h4>
                <ul>
                    {''.join(f'<li>{s}</li>' for s in swot.get('strengths', []))}
                </ul>
            </div>

            <div class="swot-section">
                <h4 style="color: var(--orange);">Weaknesses</h4>
                <ul>
                    {''.join(f'<li>{w}</li>' for w in swot.get('weaknesses', []))}
                </ul>
            </div>

            <div class="swot-section">
                <h4 style="color: var(--blue);">Opportunities</h4>
                <ul>
                    {''.join(f'<li>{o}</li>' for o in swot.get('opportunities', []))}
                </ul>
            </div>

            <div class="swot-section">
                <h4 style="color: var(--text-secondary);">Threats</h4>
                <ul>
                    {''.join(f'<li>{t}</li>' for t in swot.get('threats', []))}
                </ul>
            </div>
        </div>
        """

    def _format_market_trends_html(self, brand) -> str:
        """Format market trends section as HTML."""
        if not brand.market_trends:
            return "<p>No market trends data available.</p>"

        return f"""
        <div class="card">
            <ul>
                {''.join(f'<li>{trend}</li>' for trend in brand.market_trends)}
            </ul>
        </div>
        """

    def _format_workflow_summary_html(self, state: WorkflowState) -> str:
        """Format workflow summary as HTML."""
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Agent</th>
                    <th>Status</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f'''<tr>
                    <td>{t.task_name}</td>
                    <td><span class="badge badge-success">{t.status.value}</span></td>
                    <td>{t.duration_seconds}s</td>
                </tr>''' for t in state.task_results)}
            </tbody>
        </table>
        """
