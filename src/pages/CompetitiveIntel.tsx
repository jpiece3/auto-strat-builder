import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBrandTheme } from '@/lib/theme-context';
import { useAuth } from '@/lib/auth-context';
import {
  ArrowLeft,
  TrendingUp,
  Target,
  DollarSign,
  Users,
  BarChart3,
  Lightbulb,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Loader2,
  LogOut,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const API_BASE = import.meta.env.VITE_API_URL || '';

const CHART_COLORS = {
  primary: '#1a365d',
  accent: '#ed8936',
  success: '#16a34a',
  muted: '#64748b',
  destructive: '#ef4444',
  amber: '#f59e0b',
};

const intensityToNumber = (intensity: string): number => {
  switch (intensity.toLowerCase()) {
    case 'very high': return 4;
    case 'high': return 3;
    case 'medium-high': return 2.5;
    case 'medium': return 2;
    case 'low': return 1;
    case 'very low': return 0.5;
    default: return 1;
  }
};

const saturationToNumber = (saturation: string): number => {
  switch (saturation.toLowerCase()) {
    case 'high': return 3;
    case 'medium-high': return 2.5;
    case 'medium': return 2;
    case 'low': return 1;
    case 'very low': return 0.5;
    default: return 1;
  }
};

const opportunityToNumber = (size: string): number => {
  switch (size.toLowerCase()) {
    case 'high': return 3;
    case 'medium-high': return 2.5;
    case 'medium': return 2;
    case 'low': return 1;
    default: return 1;
  }
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="bg-card border border-border p-3 shadow-md" style={{ borderRadius: '4px' }}>
      <p className="stat-label-sharp mb-1">{label}</p>
      {payload.map((entry: any, idx: number) => (
        <p key={idx} className="text-xs text-muted-foreground">
          <span style={{ color: entry.color }}>&#9679;</span> {entry.name}: {entry.value}%
        </p>
      ))}
    </div>
  );
};

const CustomTooltipSimple = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="bg-card border border-border p-3 shadow-md" style={{ borderRadius: '4px' }}>
      <p className="stat-label-sharp mb-1">{label}</p>
      {payload.map((entry: any, idx: number) => (
        <p key={idx} className="text-xs text-muted-foreground">
          <span style={{ color: entry.color }}>&#9679;</span> {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  );
};

// Sample data structure - used as fallback
const sampleData = {
  "analysis_metadata": {
    "client_company": "Psycho Bunny",
    "client_domain": "https://www.psychobunny.ca/",
    "client_industry": "Designer Fashion",
    "analysis_date": "2026-02-13",
    "date_range_days": 180,
    "region": "Canada"
  },
  "competitors": [
    {
      "name": "Ralph Lauren",
      "domain": "https://www.ralphlauren.ca/",
      "value_proposition": {
        "primary_claim": "Defining modern luxury and timeless style since 1967",
        "headline": "Heritage icons, quality craftsmanship, and unique style",
        "target_audience": "Multi-segment: men, women, kids; focus on heritage-conscious, premium consumers",
        "key_differentiators": [
          "60+ year heritage and legacy (founded 1967)",
          "Iconic Polo Pony logo and brand heritage",
          "Quality craftsmanship and premium materials"
        ],
        "proof_points": [
          "Museum of Modern Art (MoMA) permanent collection inclusion",
          "Official Team USA Olympic outfitter"
        ]
      },
      "positioning_dimensions": {
        "price_tier": "high",
        "target_segment": "multi_segment",
        "messaging_style": "business_value",
        "brand_personality": "authoritative",
        "funnel_focus": "full_funnel",
        "geographic_focus": "global"
      },
      "keyword_strategy": {
        "analysis": "Ralph Lauren dominates branded search with 110K searches for 'ralph lauren' (14.86% of traffic), indicating massive brand equity.",
        "intent_distribution": {
          "navigational_percent": 50,
          "informational_percent": 35,
          "transactional_percent": 15,
          "top_themes": ["polo shirts", "designer fashion", "heritage clothing"]
        }
      },
      "ad_strategy": {
        "primary_platforms": ["Facebook", "Instagram"],
        "estimated_platform_allocation": {
          "facebook_instagram": 60,
          "google": 25,
          "other": 15
        },
        "creative_velocity": "High - continuous seasonal campaigns",
        "dominant_format": "Video and carousel ads",
        "visual_style": "Premium, lifestyle-focused, heritage-centric",
        "core_messaging_angles": [
          "Timeless American style",
          "Heritage and craftsmanship",
          "Seasonal collections"
        ],
        "brand_personality": "Professional, aspirational, authoritative"
      },
      "competitive_strengths": [
        "Unmatched brand heritage and recognition",
        "Diverse product portfolio across price points",
        "Strong emotional brand connection"
      ],
      "competitive_weaknesses": [
        "Price point may limit mass-market appeal",
        "Legacy brand perception (may feel dated to younger audiences)"
      ]
    }
  ],
  "landscape": {
    "market_segments_served": [
      {
        "segment": "Multi-segment (men, women, kids)",
        "competitors_targeting": ["Ralph Lauren", "Calvin Klein", "Polo"],
        "saturation": "High",
        "key_players": "All three major competitors"
      }
    ],
    "pricing_distribution": [
      {
        "tier": "Mid ($40-80 CAD per item)",
        "examples": "Calvin Klein basics, Psycho Bunny polos",
        "competitors": ["Psycho Bunny", "Calvin Klein (basics)"],
        "positioning": "Value-conscious quality seekers"
      }
    ],
    "messaging_clusters": [
      {
        "cluster": "Heritage & Timeless Style",
        "core_message": "Decades of craftsmanship, American icon status",
        "competitors_using": ["Ralph Lauren", "Polo"],
        "intensity": "Very High",
        "effectiveness_signal": "High - dominates branded search"
      }
    ]
  },
  "white_space": {
    "underserved_segments": [
      {
        "segment": "Gen Z casual contemporary (non-heritage-focused)",
        "evidence": "Ralph Lauren/Polo emphasize heritage; Calvin Klein is minimalist but underwear-heavy",
        "saturation": "Low",
        "opportunity_size": "Medium",
        "why_underserved": "No competitor addresses irreverent, culturally-aware contemporary casual"
      }
    ],
    "positioning_recommendation": {
      "recommended_position": "Position as the 'authentically playful, contemporary Canadian designer casual brand'",
      "key_differentiators_to_emphasize": [
        "Canadian heritage and identity",
        "Playful irreverence via iconic bunny logo",
        "Vibrant, bold color palette"
      ],
      "messaging_angle_to_adopt": "Authentically Unconventional",
      "target_segment_to_prioritize": "Primary: 18-35 year old Canadians (Gen Z and millennial)",
      "rationale": "Ralph Lauren dominates heritage; Calvin Klein dominates minimalist design"
    }
  }
};

const CompetitiveIntel: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { theme, setTheme } = useBrandTheme();
  const { logout } = useAuth();
  const [data, setData] = useState<typeof sampleData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCompetitor, setSelectedCompetitor] = useState(0);
  const [expandedSections, setExpandedSections] = useState<{[key: string]: boolean}>({
    valueProp: true,
    positioning: false,
    keywords: false,
    ads: false,
    strengths: false
  });

  // Fetch competitive intelligence data and brand theme
  useEffect(() => {
    if (!jobId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch data and theme in parallel
        const [dataRes, themeRes] = await Promise.all([
          fetch(`${API_BASE}/api/reports/${jobId}/competitive-intel`),
          fetch(`${API_BASE}/api/theme/${jobId}`).catch(() => null),
        ]);

        if (!dataRes.ok) {
          throw new Error(`Failed to fetch competitive intelligence: ${dataRes.statusText}`);
        }

        const intelData = await dataRes.json();
        setData(intelData);

        // Apply brand theme if available
        if (themeRes?.ok) {
          const themeData = await themeRes.json();
          setTheme(themeData);
        }
      } catch (err) {
        console.error('Error fetching competitive intelligence:', err);
        setError(err instanceof Error ? err.message : 'Failed to load competitive intelligence');
        setData(sampleData);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [jobId, setTheme]);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <nav className="header-sharp sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
              {theme.logo_url ? (
              <img src={theme.logo_url} alt={theme.brand_name || 'Brand'} className="h-9" />
            ) : (
              <img src="/logo.png" alt="Brothers Automate" className="h-9" />
            )}
              <span className="font-bold text-lg uppercase tracking-wide">
                Intelligence
              </span>
            </div>
            <button onClick={() => navigate('/dashboard')} className="btn-sharp-secondary text-xs py-2 px-4">
              <ArrowLeft className="w-4 h-4 mr-1" /> Dashboard
            </button>
          </div>
        </nav>
        <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center">
          <Loader2 className="w-12 h-12 text-brand-accent animate-spin mb-4" />
          <p className="stat-label-sharp">Loading competitive intelligence...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !data) {
    return (
      <div className="min-h-screen bg-background">
        <nav className="header-sharp sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
              {theme.logo_url ? (
              <img src={theme.logo_url} alt={theme.brand_name || 'Brand'} className="h-9" />
            ) : (
              <img src="/logo.png" alt="Brothers Automate" className="h-9" />
            )}
              <span className="font-bold text-lg uppercase tracking-wide">
                Intelligence
              </span>
            </div>
            <button onClick={() => navigate('/dashboard')} className="btn-sharp-secondary text-xs py-2 px-4">
              <ArrowLeft className="w-4 h-4 mr-1" /> Dashboard
            </button>
          </div>
        </nav>
        <div className="container mx-auto px-4 py-20">
          <div className="card-sharp p-6 border-destructive bg-destructive/5 max-w-2xl mx-auto">
            <h2 className="text-xl font-bold text-destructive mb-3 uppercase tracking-wide">Error Loading Data</h2>
            <p className="text-muted-foreground mb-4">{error}</p>
            <button onClick={() => navigate('/dashboard')} className="btn-sharp-primary py-2 px-4 text-xs">
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Use fetched data or fallback to sample data
  const intelData = data || sampleData;
  const competitor = intelData.competitors[selectedCompetitor];

  const getSaturationColor = (saturation: string) => {
    switch (saturation.toLowerCase()) {
      case 'high': return 'bg-destructive text-destructive-foreground';
      case 'medium': case 'medium-high': return 'bg-amber-500 text-white';
      case 'low': case 'very low': return 'bg-success text-white';
      default: return 'bg-secondary text-foreground';
    }
  };

  const getOpportunityColor = (size: string) => {
    switch (size.toLowerCase()) {
      case 'high': case 'medium-high': return 'bg-success text-white';
      case 'medium': return 'bg-amber-500 text-white';
      case 'low': return 'bg-secondary text-foreground';
      default: return 'bg-secondary text-foreground';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <nav className="header-sharp sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            {theme.logo_url ? (
              <img src={theme.logo_url} alt={theme.brand_name || 'Brand'} className="h-9" />
            ) : (
              <img src="/logo.png" alt="Brothers Automate" className="h-9" />
            )}
            <span className="font-bold text-lg uppercase tracking-wide">
              Intelligence
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => navigate('/dashboard')} className="btn-sharp-secondary text-xs py-2 px-4">
              <ArrowLeft className="w-4 h-4 mr-1" /> Dashboard
            </button>
            <button onClick={() => { logout(); navigate('/login'); }} className="btn-sharp-secondary text-xs py-2 px-4">
              <LogOut className="w-4 h-4 mr-1" /> Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-10 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-foreground uppercase tracking-wide mb-2">
                Competitive Intelligence
              </h1>
              <p className="stat-label-sharp">
                {intelData.analysis_metadata.client_company} · {intelData.analysis_metadata.client_industry} · {intelData.analysis_metadata.analysis_date}
              </p>
            </div>
            <span className="badge-sharp-accent">
              {intelData.analysis_metadata.date_range_days} Day Analysis
            </span>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card-sharp bg-card p-4">
              <div className="stat-label-sharp mb-2">Competitors Analyzed</div>
              <div className="text-2xl font-bold text-foreground">{intelData.competitors.length}</div>
            </div>
            <div className="card-sharp bg-card p-4">
              <div className="stat-label-sharp mb-2">Market Segments</div>
              <div className="text-2xl font-bold text-foreground">{intelData.landscape.market_segments_served.length}</div>
            </div>
            <div className="card-sharp bg-card p-4">
              <div className="stat-label-sharp mb-2">White Space Opportunities</div>
              <div className="text-2xl font-bold text-foreground">{intelData.white_space.underserved_segments.length}</div>
            </div>
            <div className="card-sharp bg-card p-4">
              <div className="stat-label-sharp mb-2">Messaging Clusters</div>
              <div className="text-2xl font-bold text-foreground">{intelData.landscape.messaging_clusters.length}</div>
            </div>
          </div>
        </div>

        {/* Landscape Overview Charts */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-foreground uppercase tracking-wide mb-6 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-brand-accent" />
            Landscape Overview
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Messaging Cluster Intensity */}
            <div className="card-sharp bg-card p-6">
              <div className="stat-label-sharp mb-4">Messaging Cluster Intensity</div>
              <ResponsiveContainer width="100%" height={Math.max(160, intelData.landscape.messaging_clusters.length * 45)}>
                <BarChart
                  layout="vertical"
                  data={intelData.landscape.messaging_clusters.map((c) => ({
                    name: c.cluster.length > 25 ? c.cluster.slice(0, 25) + '...' : c.cluster,
                    Intensity: intensityToNumber(c.intensity),
                    fullName: c.cluster,
                  }))}
                  margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(210, 20%, 90%)" />
                  <XAxis type="number" domain={[0, 4]} tick={{ fontSize: 11 }} ticks={[1, 2, 3, 4]} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={130} />
                  <Tooltip content={<CustomTooltipSimple />} />
                  <Bar dataKey="Intensity" fill={CHART_COLORS.accent} radius={[0, 2, 2, 0]}>
                    {intelData.landscape.messaging_clusters.map((c, idx) => (
                      <Cell
                        key={idx}
                        fill={intensityToNumber(c.intensity) >= 3 ? CHART_COLORS.accent : intensityToNumber(c.intensity) >= 2 ? CHART_COLORS.amber : CHART_COLORS.muted}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Market Segment Saturation */}
            <div className="card-sharp bg-card p-6">
              <div className="stat-label-sharp mb-4">Market Segment Saturation</div>
              <ResponsiveContainer width="100%" height={Math.max(160, intelData.landscape.market_segments_served.length * 45)}>
                <BarChart
                  layout="vertical"
                  data={intelData.landscape.market_segments_served.map((s) => ({
                    name: s.segment.length > 25 ? s.segment.slice(0, 25) + '...' : s.segment,
                    Saturation: saturationToNumber(s.saturation),
                    fullName: s.segment,
                  }))}
                  margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(210, 20%, 90%)" />
                  <XAxis type="number" domain={[0, 3]} tick={{ fontSize: 11 }} ticks={[1, 2, 3]} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={130} />
                  <Tooltip content={<CustomTooltipSimple />} />
                  <Bar dataKey="Saturation" fill={CHART_COLORS.destructive} radius={[0, 2, 2, 0]}>
                    {intelData.landscape.market_segments_served.map((s, idx) => (
                      <Cell
                        key={idx}
                        fill={saturationToNumber(s.saturation) >= 3 ? CHART_COLORS.destructive : saturationToNumber(s.saturation) >= 2 ? CHART_COLORS.amber : CHART_COLORS.success}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* Competitor Analysis */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-foreground uppercase tracking-wide mb-6 flex items-center gap-2">
            <Users className="w-6 h-6 text-brand-accent" />
            Competitor Profiles
          </h2>

          {/* Competitor Selector */}
          <div className="flex gap-3 mb-6 overflow-x-auto pb-2">
            {intelData.competitors.map((comp, idx) => (
              <button
                key={comp.name}
                onClick={() => setSelectedCompetitor(idx)}
                className={`px-6 py-3 text-sm font-semibold uppercase tracking-wide transition-all whitespace-nowrap ${
                  selectedCompetitor === idx
                    ? 'btn-sharp-primary'
                    : 'btn-sharp-secondary'
                }`}
              >
                {comp.name}
              </button>
            ))}
          </div>

          {/* Competitor Detail */}
          <div className="card-sharp bg-card p-6 space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between pb-4 border-b border-border">
              <div>
                <h3 className="text-xl font-bold text-foreground mb-2">{competitor.name}</h3>
                <a href={competitor.domain} target="_blank" rel="noopener noreferrer" className="text-brand-accent text-sm flex items-center gap-1 hover:underline">
                  {competitor.domain} <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="flex gap-2">
                <span className={`badge-sharp text-xs ${competitor.positioning_dimensions.price_tier === 'high' ? 'badge-sharp-accent' : ''}`}>
                  {competitor.positioning_dimensions.price_tier.toUpperCase()} PRICE
                </span>
                <span className="badge-sharp text-xs">
                  {competitor.positioning_dimensions.geographic_focus.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Value Proposition */}
            <div>
              <button
                onClick={() => toggleSection('valueProp')}
                className="w-full flex items-center justify-between py-2 font-semibold uppercase text-sm tracking-wide text-foreground hover:text-brand-accent transition-colors"
              >
                <span className="flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Value Proposition
                </span>
                {expandedSections.valueProp ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {expandedSections.valueProp && (
                <div className="mt-4 space-y-4">
                  <div>
                    <div className="stat-label-sharp mb-2">Primary Claim</div>
                    <p className="text-muted-foreground">{competitor.value_proposition.primary_claim}</p>
                  </div>
                  <div>
                    <div className="stat-label-sharp mb-2">Target Audience</div>
                    <p className="text-muted-foreground">{competitor.value_proposition.target_audience}</p>
                  </div>
                  <div>
                    <div className="stat-label-sharp mb-2">Key Differentiators</div>
                    <ul className="space-y-2">
                      {competitor.value_proposition.key_differentiators.map((diff, idx) => (
                        <li key={idx} className="text-muted-foreground flex items-start gap-2">
                          <span className="text-brand-accent mt-1">•</span>
                          {diff}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="stat-label-sharp mb-2">Proof Points</div>
                    <ul className="space-y-2">
                      {competitor.value_proposition.proof_points.map((proof, idx) => (
                        <li key={idx} className="text-muted-foreground flex items-start gap-2">
                          <span className="text-brand-accent mt-1">✓</span>
                          {proof}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>

            {/* Keyword Strategy */}
            <div className="border-t border-border pt-6">
              <button
                onClick={() => toggleSection('keywords')}
                className="w-full flex items-center justify-between py-2 font-semibold uppercase text-sm tracking-wide text-foreground hover:text-brand-accent transition-colors"
              >
                <span className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Keyword Strategy
                </span>
                {expandedSections.keywords ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {expandedSections.keywords && (
                <div className="mt-4 space-y-4">
                  <p className="text-muted-foreground">{competitor.keyword_strategy.analysis}</p>

                  {/* Intent Distribution Chart - All Competitors */}
                  <div className="bg-background p-4" style={{borderRadius: '4px'}}>
                    <div className="stat-label-sharp mb-3">Intent Distribution — All Competitors</div>
                    <ResponsiveContainer width="100%" height={Math.max(180, intelData.competitors.length * 50)}>
                      <BarChart
                        layout="vertical"
                        data={intelData.competitors.map((c) => ({
                          name: c.name,
                          Navigational: c.keyword_strategy.intent_distribution.navigational_percent,
                          Informational: c.keyword_strategy.intent_distribution.informational_percent,
                          Transactional: c.keyword_strategy.intent_distribution.transactional_percent,
                        }))}
                        margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(210, 20%, 90%)" />
                        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
                        <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={100} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }} />
                        <Bar dataKey="Navigational" stackId="a" fill={CHART_COLORS.primary} />
                        <Bar dataKey="Informational" stackId="a" fill={CHART_COLORS.accent} />
                        <Bar dataKey="Transactional" stackId="a" fill={CHART_COLORS.success} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div>
                    <div className="stat-label-sharp mb-2">Top Themes</div>
                    <div className="flex flex-wrap gap-2">
                      {competitor.keyword_strategy.intent_distribution.top_themes.map((theme, idx) => (
                        <span key={idx} className="badge-sharp text-xs">{theme}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Ad Strategy */}
            <div className="border-t border-border pt-6">
              <button
                onClick={() => toggleSection('ads')}
                className="w-full flex items-center justify-between py-2 font-semibold uppercase text-sm tracking-wide text-foreground hover:text-brand-accent transition-colors"
              >
                <span className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Ad Strategy
                </span>
                {expandedSections.ads ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {expandedSections.ads && (
                <div className="mt-4 space-y-4">
                  {/* Ad Platform Allocation Chart - All Competitors */}
                  <div className="bg-background p-4" style={{borderRadius: '4px'}}>
                    <div className="stat-label-sharp mb-3">Platform Allocation — All Competitors</div>
                    <ResponsiveContainer width="100%" height={Math.max(200, intelData.competitors.length * 50)}>
                      <BarChart
                        layout="vertical"
                        data={intelData.competitors.map((c) => ({
                          name: c.name,
                          'FB / IG': c.ad_strategy.estimated_platform_allocation.facebook_instagram,
                          'Google': c.ad_strategy.estimated_platform_allocation.google,
                          'Other': c.ad_strategy.estimated_platform_allocation.other,
                        }))}
                        margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(210, 20%, 90%)" />
                        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
                        <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={100} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }} />
                        <Bar dataKey="FB / IG" stackId="a" fill={CHART_COLORS.primary} />
                        <Bar dataKey="Google" stackId="a" fill={CHART_COLORS.accent} />
                        <Bar dataKey="Other" stackId="a" fill={CHART_COLORS.muted} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="stat-label-sharp mb-2">Primary Platforms</div>
                      <div className="flex gap-2">
                        {competitor.ad_strategy.primary_platforms.map((platform, idx) => (
                          <span key={idx} className="badge-sharp-accent text-xs">{platform}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="stat-label-sharp mb-2">Creative Velocity</div>
                      <p className="text-muted-foreground text-sm">{competitor.ad_strategy.creative_velocity}</p>
                    </div>
                  </div>
                  <div>
                    <div className="stat-label-sharp mb-2">Dominant Format</div>
                    <p className="text-muted-foreground text-sm">{competitor.ad_strategy.dominant_format}</p>
                  </div>
                  <div>
                    <div className="stat-label-sharp mb-2">Visual Style</div>
                    <p className="text-muted-foreground text-sm">{competitor.ad_strategy.visual_style}</p>
                  </div>
                  <div>
                    <div className="stat-label-sharp mb-2">Core Messaging Angles</div>
                    <ul className="space-y-2">
                      {competitor.ad_strategy.core_messaging_angles.map((angle, idx) => (
                        <li key={idx} className="text-muted-foreground flex items-start gap-2 text-sm">
                          <span className="text-brand-accent mt-1">→</span>
                          {angle}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>

            {/* Strengths & Weaknesses */}
            <div className="border-t border-border pt-6">
              <button
                onClick={() => toggleSection('strengths')}
                className="w-full flex items-center justify-between py-2 font-semibold uppercase text-sm tracking-wide text-foreground hover:text-brand-accent transition-colors"
              >
                <span>Competitive Assessment</span>
                {expandedSections.strengths ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {expandedSections.strengths && (
                <div className="mt-4 grid md:grid-cols-2 gap-6">
                  <div>
                    <div className="stat-label-sharp mb-3 text-success">Strengths</div>
                    <ul className="space-y-2">
                      {competitor.competitive_strengths.map((strength, idx) => (
                        <li key={idx} className="text-muted-foreground flex items-start gap-2 text-sm">
                          <span className="text-success mt-1">✓</span>
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="stat-label-sharp mb-3 text-destructive">Weaknesses</div>
                    <ul className="space-y-2">
                      {competitor.competitive_weaknesses.map((weakness, idx) => (
                        <li key={idx} className="text-muted-foreground flex items-start gap-2 text-sm">
                          <span className="text-destructive mt-1">×</span>
                          {weakness}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Market Landscape */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-foreground uppercase tracking-wide mb-6 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-brand-accent" />
            Market Landscape
          </h2>

          {/* Market Segments */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold uppercase text-sm tracking-wide text-foreground mb-4">Market Segments Served</h3>
            <div className="space-y-3">
              {intelData.landscape.market_segments_served.map((segment, idx) => (
                <div key={idx} className="card-sharp bg-card p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="font-semibold text-foreground mb-1">{segment.segment}</div>
                      <p className="text-sm text-muted-foreground">{segment.key_players}</p>
                    </div>
                    <span className={`badge-sharp text-xs ${getSaturationColor(segment.saturation)}`}>
                      {segment.saturation.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {segment.competitors_targeting.map((comp, cIdx) => (
                      <span key={cIdx} className="badge-sharp text-xs">{comp}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pricing Distribution */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold uppercase text-sm tracking-wide text-foreground mb-4">Pricing Distribution</h3>
            <div className="space-y-3">
              {intelData.landscape.pricing_distribution.map((pricing, idx) => (
                <div key={idx} className="card-sharp bg-card p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="font-semibold text-foreground mb-1 flex items-center gap-2">
                        <DollarSign className="w-4 h-4 text-brand-accent" />
                        {pricing.tier}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{pricing.examples}</p>
                      <p className="text-sm text-muted-foreground italic">"{pricing.positioning}"</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {pricing.competitors.map((comp, cIdx) => (
                      <span key={cIdx} className="badge-sharp-accent text-xs">{comp}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Messaging Clusters */}
          <div>
            <h3 className="text-lg font-semibold uppercase text-sm tracking-wide text-foreground mb-4">Messaging Clusters</h3>
            <div className="space-y-3">
              {intelData.landscape.messaging_clusters.map((cluster, idx) => (
                <div key={idx} className="card-sharp bg-card p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="font-semibold text-foreground mb-2">{cluster.cluster}</div>
                      <p className="text-sm text-muted-foreground mb-3">"{cluster.core_message}"</p>
                      <div className="flex items-center gap-4 text-xs">
                        <span className={`badge-sharp ${cluster.intensity === 'Very High' || cluster.intensity === 'High' ? 'badge-sharp-accent' : ''}`}>
                          {cluster.intensity}
                        </span>
                        <span className="text-muted-foreground">{cluster.effectiveness_signal}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {cluster.competitors_using.map((comp, cIdx) => (
                      <span key={cIdx} className="badge-sharp text-xs">{comp}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* White Space Opportunities */}
        <section>
          <h2 className="text-2xl font-bold text-foreground uppercase tracking-wide mb-6 flex items-center gap-2">
            <Lightbulb className="w-6 h-6 text-brand-accent" />
            White Space Opportunities
          </h2>

          {/* Opportunity vs Saturation Chart */}
          {intelData.white_space.underserved_segments.length > 0 && (
            <div className="card-sharp bg-card p-6 mb-8">
              <div className="stat-label-sharp mb-4">Opportunity vs Saturation</div>
              <ResponsiveContainer width="100%" height={Math.max(200, intelData.white_space.underserved_segments.length * 50)}>
                <BarChart
                  layout="vertical"
                  data={intelData.white_space.underserved_segments.map((s) => ({
                    name: s.segment.length > 30 ? s.segment.slice(0, 30) + '...' : s.segment,
                    Opportunity: opportunityToNumber(s.opportunity_size),
                    Saturation: saturationToNumber(s.saturation),
                  }))}
                  margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(210, 20%, 90%)" />
                  <XAxis type="number" domain={[0, 3]} tick={{ fontSize: 11 }} ticks={[1, 2, 3]} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={160} />
                  <Tooltip content={<CustomTooltipSimple />} />
                  <Legend wrapperStyle={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }} />
                  <Bar dataKey="Opportunity" fill={CHART_COLORS.success} radius={[0, 2, 2, 0]} />
                  <Bar dataKey="Saturation" fill={CHART_COLORS.destructive} radius={[0, 2, 2, 0]} />
                </BarChart>
              </ResponsiveContainer>
              <p className="text-xs text-muted-foreground mt-3 text-center">
                Green = higher opportunity, Red = higher saturation. Best targets have high opportunity + low saturation.
              </p>
            </div>
          )}

          {/* Underserved Segments */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold uppercase text-sm tracking-wide text-foreground mb-4">Underserved Segments</h3>
            <div className="space-y-4">
              {intelData.white_space.underserved_segments.map((segment, idx) => (
                <div key={idx} className="card-sharp bg-card p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h4 className="font-bold text-foreground mb-2">{segment.segment}</h4>
                      <p className="text-sm text-muted-foreground mb-3">{segment.why_underserved}</p>
                    </div>
                    <div className="flex gap-2 ml-4">
                      <span className={`badge-sharp text-xs ${getSaturationColor(segment.saturation)}`}>
                        {segment.saturation.toUpperCase()}
                      </span>
                      <span className={`badge-sharp text-xs ${getOpportunityColor(segment.opportunity_size)}`}>
                        {segment.opportunity_size.toUpperCase()} OPP
                      </span>
                    </div>
                  </div>
                  <div className="bg-background p-3" style={{borderRadius: '4px'}}>
                    <div className="stat-label-sharp mb-2">Evidence</div>
                    <p className="text-xs text-muted-foreground">{segment.evidence}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Strategic Positioning Recommendation */}
          <div className="card-sharp bg-brand-accent/5 border-brand-accent p-6">
            <h3 className="text-xl font-bold text-foreground mb-4 uppercase tracking-wide flex items-center gap-2">
              <Target className="w-5 h-5 text-brand-accent" />
              Strategic Positioning Recommendation
            </h3>

            <div className="space-y-6">
              <div>
                <div className="stat-label-sharp mb-2">Recommended Position</div>
                <p className="text-foreground font-medium leading-relaxed">{intelData.white_space.positioning_recommendation.recommended_position}</p>
              </div>

              <div>
                <div className="stat-label-sharp mb-3">Key Differentiators to Emphasize</div>
                <ul className="space-y-2">
                  {intelData.white_space.positioning_recommendation.key_differentiators_to_emphasize.map((diff, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <span className="text-brand-accent font-bold mt-0.5">{idx + 1}.</span>
                      {diff}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <div className="stat-label-sharp mb-2">Messaging Angle</div>
                  <p className="text-sm text-muted-foreground">{intelData.white_space.positioning_recommendation.messaging_angle_to_adopt}</p>
                </div>
                <div>
                  <div className="stat-label-sharp mb-2">Target Segment</div>
                  <p className="text-sm text-muted-foreground">{intelData.white_space.positioning_recommendation.target_segment_to_prioritize}</p>
                </div>
              </div>

              <div className="bg-background p-4" style={{borderRadius: '4px'}}>
                <div className="stat-label-sharp mb-2">Strategic Rationale</div>
                <p className="text-xs text-muted-foreground leading-relaxed">{intelData.white_space.positioning_recommendation.rationale}</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default CompetitiveIntel;
