"""Centralized configuration management for all agent services and skills."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class FirecrawlConfig:
    api_key: str = field(default_factory=lambda: os.getenv("FIRECRAWL_API_KEY", ""))
    base_url: str = "https://api.firecrawl.dev/v1"
    max_pages_per_crawl: int = 50
    timeout: int = 120


@dataclass(frozen=True)
class TavilyConfig:
    api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    max_results: int = 10
    search_depth: str = "advanced"
    include_raw_content: bool = True


@dataclass(frozen=True)
class PlaywrightConfig:
    headless: bool = True
    timeout: int = 30_000
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )


@dataclass(frozen=True)
class DataForSEOConfig:
    login: str = field(default_factory=lambda: os.getenv("DATAFORSEO_LOGIN", ""))
    password: str = field(default_factory=lambda: os.getenv("DATAFORSEO_PASSWORD", ""))
    base_url: str = "https://api.dataforseo.com/v3"
    timeout: int = 60


@dataclass(frozen=True)
class BrandDevConfig:
    api_key: str = field(default_factory=lambda: os.getenv("BRAND_DEV_API_KEY", ""))


@dataclass(frozen=True)
class LLMConfig:
    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "anthropic"))
    api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", os.getenv("OPENAI_API_KEY", "")))
    model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "claude-sonnet-4-20250514"))
    max_tokens: int = 4096
    temperature: float = 0.2


@dataclass(frozen=True)
class AgentConfig:
    """Top-level configuration aggregating all service configs."""

    firecrawl: FirecrawlConfig = field(default_factory=FirecrawlConfig)
    tavily: TavilyConfig = field(default_factory=TavilyConfig)
    playwright: PlaywrightConfig = field(default_factory=PlaywrightConfig)
    dataforseo: DataForSEOConfig = field(default_factory=DataForSEOConfig)
    branddev: BrandDevConfig = field(default_factory=BrandDevConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)

    output_dir: Path = field(
        default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "./reports"))
    )
    max_concurrent_tasks: int = 5
    retry_attempts: int = 3
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    def validate(self) -> list[str]:
        """Return a list of configuration warnings (missing keys, etc.)."""
        warnings: list[str] = []
        if not self.firecrawl.api_key:
            warnings.append("FIRECRAWL_API_KEY is not set")
        if not self.tavily.api_key:
            warnings.append("TAVILY_API_KEY is not set")
        if not self.dataforseo.login or not self.dataforseo.password:
            warnings.append("DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD not set")
        if not self.branddev.api_key:
            warnings.append("BRAND_DEV_API_KEY is not set — brand theming will use fallback")
        if not self.llm.api_key:
            warnings.append("LLM API key (ANTHROPIC_API_KEY or OPENAI_API_KEY) not set")
        return warnings
