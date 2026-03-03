"""Brand.dev skill - fetch brand visual identity (logos, colors, fonts)."""

from __future__ import annotations

from typing import Any

from agent.config import BrandDevConfig
from agent.models import BrandColor, BrandLogo, BrandTypography, BrandVisualIdentity
from agent.skills.base import BaseSkill


class BrandDevSkill(BaseSkill):
    """Fetch brand visual identity from brand.dev API.

    Returns logos, colors, and typography for any domain. Used to dynamically
    theme reports and dashboards in the analyzed brand's style.
    """

    name = "branddev"
    description = "Fetch brand visual identity (logos, colors, fonts) from brand.dev"

    def __init__(self, config: BrandDevConfig) -> None:
        super().__init__()
        self.config = config
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            from brand_dev import BrandDev
            self._client = BrandDev(api_key=self.config.api_key)
        return self._client

    async def health_check(self) -> bool:
        """Check brand.dev API connectivity."""
        try:
            client = self._get_client()
            result = client.brand.retrieve(domain="google.com")
            return result is not None
        except Exception:
            return False

    async def close(self) -> None:
        self._client = None

    async def fetch_brand(self, domain: str) -> BrandVisualIdentity | None:
        """Fetch visual identity for a domain from brand.dev.

        Returns BrandVisualIdentity with colors, logos, typography, or None on failure.
        """
        try:
            client = self._get_client()
            self.logger.info("Fetching brand data from brand.dev for: %s", domain)

            # brand.dev SDK client.brand.retrieve() is synchronous
            import asyncio
            result = await asyncio.to_thread(client.brand.retrieve, domain=domain)

            if not result:
                self.logger.warning("brand.dev returned no data for %s", domain)
                return None

            return self._parse_brand_response(result, domain)

        except Exception as exc:
            self.logger.warning("brand.dev fetch failed for %s: %s", domain, exc)
            return None

    def _parse_brand_response(self, result: Any, domain: str) -> BrandVisualIdentity:
        """Parse brand.dev API response into BrandVisualIdentity."""
        colors = self._extract_colors(result)
        logos = self._extract_logos(result)
        typography = self._extract_typography(result)
        slogan = ""

        # Try to get slogan from response
        if hasattr(result, "slogan") and result.slogan:
            slogan = result.slogan
        elif hasattr(result, "description") and result.description:
            slogan = result.description[:80]

        self.logger.info(
            "brand.dev: %s → %d colors, %d logos, fonts=%s/%s",
            domain, len(colors), len(logos),
            typography.heading_font or "none",
            typography.body_font or "none",
        )

        return BrandVisualIdentity(
            colors=colors,
            logos=logos,
            typography=typography,
            slogan=slogan,
            source="brand_dev",
        )

    def _extract_colors(self, result: Any) -> list[BrandColor]:
        """Extract and assign roles to brand colors."""
        colors: list[BrandColor] = []
        raw_colors = getattr(result, "colors", None) or []

        role_order = ["primary", "secondary", "accent"]
        for i, color in enumerate(raw_colors):
            hex_val = ""
            name = ""

            if isinstance(color, dict):
                hex_val = color.get("hex", "")
                name = color.get("name", "")
            elif hasattr(color, "hex"):
                hex_val = color.hex or ""
                name = getattr(color, "name", "") or ""

            if hex_val:
                if not hex_val.startswith("#"):
                    hex_val = f"#{hex_val}"
                role = role_order[i] if i < len(role_order) else ""
                colors.append(BrandColor(hex=hex_val, name=name, role=role))

        return colors

    def _extract_logos(self, result: Any) -> list[BrandLogo]:
        """Extract logo variants, preferring full logos over icons."""
        logos: list[BrandLogo] = []
        raw_logos = getattr(result, "logos", None) or []

        for logo in raw_logos:
            url = ""
            mode = ""
            logo_type = ""
            width = 0
            height = 0

            if isinstance(logo, dict):
                url = logo.get("url", "")
                mode = logo.get("mode", "")
                logo_type = logo.get("type", "")
                res = logo.get("resolution", {})
                if isinstance(res, dict):
                    width = res.get("width", 0)
                    height = res.get("height", 0)
            elif hasattr(logo, "url"):
                url = logo.url or ""
                mode = getattr(logo, "mode", "") or ""
                logo_type = getattr(logo, "type", "") or ""
                res = getattr(logo, "resolution", None)
                if res:
                    width = getattr(res, "width", 0) or 0
                    height = getattr(res, "height", 0) or 0

            if url:
                logos.append(BrandLogo(
                    url=url, mode=mode, type=logo_type,
                    width=width, height=height,
                ))

        return logos

    def _extract_typography(self, result: Any) -> BrandTypography:
        """Extract typography from brand.dev styleguide data."""
        heading_font = ""
        body_font = ""

        # brand.dev may include styleguide/typography in the brand response
        styleguide = getattr(result, "styleguide", None)
        if styleguide:
            typography = getattr(styleguide, "typography", None) or {}
            if isinstance(typography, dict):
                h1 = typography.get("h1", {})
                p = typography.get("p", {})
                if isinstance(h1, dict):
                    heading_font = h1.get("fontFamily", "")
                if isinstance(p, dict):
                    body_font = p.get("fontFamily", "")
            elif hasattr(typography, "h1"):
                h1 = typography.h1
                if hasattr(h1, "fontFamily"):
                    heading_font = h1.fontFamily or ""
                p = getattr(typography, "p", None)
                if p and hasattr(p, "fontFamily"):
                    body_font = p.fontFamily or ""

        # Clean up font names (remove quotes, fallback stacks)
        heading_font = self._clean_font_name(heading_font)
        body_font = self._clean_font_name(body_font)

        return BrandTypography(
            heading_font=heading_font,
            body_font=body_font,
        )

    @staticmethod
    def _clean_font_name(font: str) -> str:
        """Extract the primary font name from a CSS font-family string."""
        if not font:
            return ""
        # Take the first font in a comma-separated list
        primary = font.split(",")[0].strip()
        # Remove quotes
        primary = primary.strip("'\"")
        return primary
