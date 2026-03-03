import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

export interface BrandTheme {
  primary: string;
  primary_light: string;
  accent: string;
  accent_dark: string;
  background: string;
  card_bg: string;
  text_primary: string;
  text_secondary: string;
  text_muted: string;
  border: string;
  success: string;
  blue: string;
  font_heading: string;
  font_body: string;
  logo_url: string;
  tagline: string;
  footer_text: string;
  header_text_color: string;
  source: string;
  brand_name: string;
}

export const DEFAULT_THEME: BrandTheme = {
  primary: '#1a365d',
  primary_light: '#2c5282',
  accent: '#ed8936',
  accent_dark: '#dd6b20',
  background: '#fdfcfa',
  card_bg: '#ffffff',
  text_primary: '#1a365d',
  text_secondary: '#64748b',
  text_muted: '#94a3b8',
  border: '#e8e6e1',
  success: '#16a34a',
  blue: '#3182ce',
  font_heading: 'Plus Jakarta Sans',
  font_body: 'Plus Jakarta Sans',
  logo_url: '',
  tagline: 'Simple AI. Smart Results.',
  footer_text: 'Brothers Automate Intelligence Agent v0.1.0',
  header_text_color: '#ffffff',
  source: 'fallback',
  brand_name: '',
};

/** Convert hex color (#1a365d) to HSL components string ("210 55% 24%") */
function hexToHSL(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return '';

  const r = parseInt(result[1], 16) / 255;
  const g = parseInt(result[2], 16) / 255;
  const b = parseInt(result[3], 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  const l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }

  return `${Math.round(h * 360)} ${Math.round(s * 100)}% ${Math.round(l * 100)}%`;
}

/** Create a light tint: keep hue, soften saturation, set lightness to 90% */
function lightTintHSL(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return '';

  const r = parseInt(result[1], 16) / 255;
  const g = parseInt(result[2], 16) / 255;
  const b = parseInt(result[3], 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;

  if (max !== min) {
    const d = max - min;
    const l = (max + min) / 2;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }

  return `${Math.round(h * 360)} ${Math.round(s * 50)}% 90%`;
}

interface ThemeContextValue {
  theme: BrandTheme;
  setTheme: (theme: BrandTheme) => void;
  resetTheme: () => void;
  isCustomTheme: boolean;
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: DEFAULT_THEME,
  setTheme: () => {},
  resetTheme: () => {},
  isCustomTheme: false,
});

const MANAGED_VARS = [
  '--primary', '--primary-foreground', '--primary-hover',
  '--foreground', '--card-foreground', '--popover-foreground',
  '--background', '--card', '--popover',
  '--muted-foreground',
  '--border', '--input',
  '--success', '--success-foreground',
  '--brand-accent',
  '--accent', '--accent-foreground', '--cta', '--cta-foreground',
  '--border-accent', '--ring',
  '--secondary', '--secondary-foreground',
];

function applyThemeToDOM(theme: BrandTheme) {
  const root = document.documentElement;

  const setVar = (name: string, hex: string) => {
    const hsl = hexToHSL(hex);
    if (hsl) root.style.setProperty(name, hsl);
  };

  // Primary brand color
  setVar('--primary', theme.primary);
  setVar('--primary-foreground', theme.header_text_color);
  setVar('--primary-hover', theme.primary_light);
  setVar('--foreground', theme.text_primary);
  setVar('--card-foreground', theme.text_primary);
  setVar('--popover-foreground', theme.text_primary);

  // Background & surfaces
  setVar('--background', theme.background);
  setVar('--card', theme.card_bg);
  setVar('--popover', theme.card_bg);

  // Text
  setVar('--muted-foreground', theme.text_secondary);

  // Borders
  setVar('--border', theme.border);
  setVar('--input', theme.border);

  // Success
  setVar('--success', theme.success);

  // Brand accent (bright highlight - icons, links, bullets)
  setVar('--brand-accent', theme.accent);

  // Accent / CTA (light tint of the brand accent for badges, card corners, etc.)
  const accentTint = lightTintHSL(theme.accent);
  if (accentTint) {
    root.style.setProperty('--accent', accentTint);
    root.style.setProperty('--cta', accentTint);
    root.style.setProperty('--border-accent', accentTint);
    root.style.setProperty('--ring', accentTint);
    setVar('--accent-foreground', theme.text_primary);
    setVar('--cta-foreground', theme.text_primary);
  }

  // Secondary (light tint of primary)
  const secondaryTint = lightTintHSL(theme.primary);
  if (secondaryTint) {
    root.style.setProperty('--secondary', secondaryTint);
    setVar('--secondary-foreground', theme.text_primary);
  }

  // Load custom fonts
  const loadFont = (fontName: string) => {
    if (!fontName || fontName === 'Plus Jakarta Sans') return;
    const fontUrl = `https://fonts.googleapis.com/css2?family=${fontName.replace(/ /g, '+')}:wght@400;500;600;700&display=swap`;
    if (!document.querySelector(`link[href="${fontUrl}"]`)) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = fontUrl;
      document.head.appendChild(link);
    }
  };

  loadFont(theme.font_heading);
  if (theme.font_body !== theme.font_heading) {
    loadFont(theme.font_body);
  }

  // Apply font to body
  if (theme.font_body) {
    document.body.style.fontFamily = `'${theme.font_body}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`;
  }
}

function clearThemeFromDOM() {
  const root = document.documentElement;
  for (const v of MANAGED_VARS) {
    root.style.removeProperty(v);
  }
  document.body.style.fontFamily = '';
}

export const BrandThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<BrandTheme>(DEFAULT_THEME);
  const [isCustomTheme, setIsCustomTheme] = useState(false);

  const setTheme = useCallback((newTheme: BrandTheme) => {
    setThemeState(newTheme);
    const isCustom = newTheme.source === 'brand_dev';
    setIsCustomTheme(isCustom);
    if (isCustom) {
      applyThemeToDOM(newTheme);
    } else {
      clearThemeFromDOM();
    }
  }, []);

  const resetTheme = useCallback(() => {
    setThemeState(DEFAULT_THEME);
    setIsCustomTheme(false);
    clearThemeFromDOM();
  }, []);

  useEffect(() => {
    return () => clearThemeFromDOM();
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resetTheme, isCustomTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useBrandTheme = () => useContext(ThemeContext);
