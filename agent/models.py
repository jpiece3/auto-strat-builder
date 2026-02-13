"""Shared data models and schemas used across agents and skills."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ReportSection(str, Enum):
    BRAND_OVERVIEW = "brand_overview"
    WEBSITE_ANALYSIS = "website_analysis"
    SEO_PROFILE = "seo_profile"
    COMPETITOR_LANDSCAPE = "competitor_landscape"
    CONTENT_STRATEGY = "content_strategy"
    SOCIAL_PRESENCE = "social_presence"
    MARKET_POSITIONING = "market_positioning"
    RECOMMENDATIONS = "recommendations"


# ---------------------------------------------------------------------------
# Input Models
# ---------------------------------------------------------------------------

@dataclass
class BrandQuery:
    """Input specification for a brand intelligence run."""

    brand_name: str
    website_url: str
    industry: str = ""
    known_competitors: list[str] = field(default_factory=list)
    target_keywords: list[str] = field(default_factory=list)
    target_markets: list[str] = field(default_factory=lambda: ["us"])
    social_profiles: dict[str, str] = field(default_factory=dict)
    depth: str = "comprehensive"  # "quick" | "standard" | "comprehensive"


# ---------------------------------------------------------------------------
# Intermediate Data Models
# ---------------------------------------------------------------------------

@dataclass
class WebPage:
    url: str
    title: str = ""
    content: str = ""
    meta_description: str = ""
    headings: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    status_code: int = 200
    crawled_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    content: str = ""
    score: float = 0.0
    source: str = ""


@dataclass
class SEOMetrics:
    domain: str
    domain_rank: int = 0
    organic_traffic: int = 0
    organic_keywords: int = 0
    backlinks_total: int = 0
    referring_domains: int = 0
    domain_authority: float = 0.0
    top_keywords: list[dict[str, Any]] = field(default_factory=list)
    top_pages: list[dict[str, Any]] = field(default_factory=list)
    backlink_profile: dict[str, Any] = field(default_factory=dict)
    tech_stack: list[str] = field(default_factory=list)


@dataclass
class CompetitorProfile:
    name: str
    domain: str
    description: str = ""
    similarity_score: float = 0.0
    seo_metrics: SEOMetrics | None = None
    key_differentiators: list[str] = field(default_factory=list)
    shared_keywords: list[str] = field(default_factory=list)
    content_themes: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)


@dataclass
class SocialPresence:
    platform: str
    url: str = ""
    followers: int = 0
    engagement_rate: float = 0.0
    post_frequency: str = ""
    top_content_themes: list[str] = field(default_factory=list)
    sentiment: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class BrandColor:
    """A single color from the brand's palette."""
    hex: str
    name: str = ""
    role: str = ""  # "primary", "secondary", "accent"


@dataclass
class BrandLogo:
    """A logo variant from the brand."""
    url: str
    mode: str = ""    # "light", "dark"
    type: str = ""    # "icon", "logo"
    width: int = 0
    height: int = 0


@dataclass
class BrandTypography:
    """Brand typography settings."""
    heading_font: str = ""
    body_font: str = ""
    heading_weight: str = "700"
    body_weight: str = "400"


@dataclass
class BrandVisualIdentity:
    """Visual identity data fetched from brand.dev or fallback."""
    colors: list[BrandColor] = field(default_factory=list)
    logos: list[BrandLogo] = field(default_factory=list)
    typography: BrandTypography = field(default_factory=BrandTypography)
    slogan: str = ""
    source: str = ""  # "brand_dev" or "fallback"


@dataclass
class ContentAnalysis:
    total_pages: int = 0
    blog_posts: int = 0
    content_themes: list[str] = field(default_factory=list)
    avg_word_count: int = 0
    publishing_frequency: str = ""
    content_types: list[str] = field(default_factory=list)
    top_performing: list[dict[str, Any]] = field(default_factory=list)
    content_gaps: list[str] = field(default_factory=list)


@dataclass
class BrandProfile:
    """Aggregated brand intelligence data."""

    brand_name: str
    domain: str
    tagline: str = ""
    description: str = ""
    value_propositions: list[str] = field(default_factory=list)
    target_audience: list[str] = field(default_factory=list)
    brand_voice: str = ""
    key_messages: list[str] = field(default_factory=list)
    pages: list[WebPage] = field(default_factory=list)
    seo: SEOMetrics | None = None
    content: ContentAnalysis | None = None
    social: list[SocialPresence] = field(default_factory=list)
    competitors: list[CompetitorProfile] = field(default_factory=list)
    visual_identity: BrandVisualIdentity | None = None
    market_trends: list[str] = field(default_factory=list)
    swot: dict[str, list[str]] = field(default_factory=lambda: {
        "strengths": [],
        "weaknesses": [],
        "opportunities": [],
        "threats": [],
    })


# ---------------------------------------------------------------------------
# Workflow State
# ---------------------------------------------------------------------------

@dataclass
class TaskResult:
    task_name: str
    status: TaskStatus
    data: Any = None
    error: str = ""
    duration_seconds: float = 0.0
    started_at: str = ""
    completed_at: str = ""


@dataclass
class WorkflowState:
    """Mutable state passed through the workflow pipeline."""

    query: BrandQuery
    brand: BrandProfile | None = None
    task_results: list[TaskResult] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str = ""
    report_path: str = ""
    html_report_path: str = ""
    competitive_intel_path: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)

    def record_task(self, result: TaskResult) -> None:
        self.task_results.append(result)
        if result.status == TaskStatus.FAILED:
            self.errors.append(f"{result.task_name}: {result.error}")
