"""CLI entry point for running brand intelligence workflows."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from agent.config import AgentConfig
from agent.models import BrandQuery
from agent.utils.logging import get_logger
from agent.workflows.brand_intelligence import BrandIntelligenceWorkflow

logger = get_logger("main")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Brand Intelligence Agent - autonomous brand and competitor analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick analysis
  python -m agent.main --brand "Acme Corp" --url "https://acme.com" --industry "SaaS"

  # Comprehensive with competitors
  python -m agent.main \\
    --brand "Acme Corp" \\
    --url "https://acme.com" \\
    --industry "SaaS" \\
    --competitors "competitor1.com,competitor2.com" \\
    --keywords "project management,team collaboration" \\
    --depth comprehensive

  # From JSON config
  python -m agent.main --config query.json
        """,
    )
    parser.add_argument("--brand", type=str, help="Brand name")
    parser.add_argument("--url", type=str, help="Brand website URL")
    parser.add_argument("--industry", type=str, default="", help="Industry/vertical")
    parser.add_argument(
        "--competitors",
        type=str,
        default="",
        help="Comma-separated list of known competitor domains",
    )
    parser.add_argument(
        "--keywords",
        type=str,
        default="",
        help="Comma-separated list of target keywords",
    )
    parser.add_argument(
        "--depth",
        type=str,
        choices=["quick", "standard", "comprehensive"],
        default="comprehensive",
        help="Analysis depth (default: comprehensive)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./reports",
        help="Directory for output reports (default: ./reports)",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON config file with query parameters",
    )
    parser.add_argument(
        "--social",
        type=str,
        default="",
        help='Social profiles as JSON: \'{"linkedin": "url", "twitter": "url"}\'',
    )
    return parser.parse_args()


def build_query(args: argparse.Namespace) -> BrandQuery:
    """Build a BrandQuery from CLI args or config file."""
    if args.config:
        with open(args.config) as f:
            data = json.load(f)
        return BrandQuery(**data)

    if not args.brand or not args.url:
        print("Error: --brand and --url are required (or use --config)")
        sys.exit(1)

    social = {}
    if args.social:
        try:
            social = json.loads(args.social)
        except json.JSONDecodeError:
            print("Warning: Could not parse --social JSON, ignoring")

    return BrandQuery(
        brand_name=args.brand,
        website_url=args.url,
        industry=args.industry,
        known_competitors=[c.strip() for c in args.competitors.split(",") if c.strip()],
        target_keywords=[k.strip() for k in args.keywords.split(",") if k.strip()],
        social_profiles=social,
        depth=args.depth,
    )


async def run_workflow(query: BrandQuery, output_dir: str) -> None:
    """Execute the brand intelligence workflow."""
    from pathlib import Path

    config = AgentConfig(output_dir=Path(output_dir))
    workflow = BrandIntelligenceWorkflow(config)

    warnings = await workflow.initialize()
    if warnings:
        logger.warning("Configuration warnings:")
        for w in warnings:
            logger.warning("  - %s", w)

    print("\n" + "=" * 60)
    print(f"  Brand Intelligence Agent")
    print(f"  Target: {query.brand_name} ({query.website_url})")
    print(f"  Industry: {query.industry or 'Not specified'}")
    print(f"  Depth: {query.depth}")
    print("=" * 60 + "\n")

    state = await workflow.run(query)

    print("\n" + "=" * 60)
    print(f"  Workflow Complete: {state.status.value}")
    if state.report_path:
        print(f"  Report: {state.report_path}")
    if state.errors:
        print(f"  Errors: {len(state.errors)}")
        for err in state.errors:
            print(f"    - {err}")
    print("=" * 60 + "\n")


def main() -> None:
    args = parse_args()
    query = build_query(args)
    asyncio.run(run_workflow(query, args.output_dir))


if __name__ == "__main__":
    main()
