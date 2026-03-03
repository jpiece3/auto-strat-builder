import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBrandTheme } from '@/lib/theme-context';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Search,
  Globe,
  BarChart3,
  Users,
  FileText,
  ArrowRight,
  Loader2,
  Zap,
  Target,
  TrendingUp,
  Shield,
} from 'lucide-react';
import { toast } from '@/hooks/use-toast';

const API_BASE = import.meta.env.VITE_API_URL || '';

const PIPELINE_STEPS = [
  { icon: Search, label: 'Brand Discovery', desc: 'Crawl & profile your brand identity via Firecrawl' },
  { icon: Users, label: 'Competitor Intel', desc: 'Identify & analyze competitors via Tavily + DataForSEO' },
  { icon: BarChart3, label: 'SEO Analysis', desc: 'Keywords, backlinks & traffic via DataForSEO' },
  { icon: Globe, label: 'Web Presence', desc: 'Social profiles & reputation via Playwright' },
  { icon: FileText, label: 'Report', desc: 'Comprehensive intelligence report via LLM synthesis' },
];

const Index = () => {
  const navigate = useNavigate();
  const { resetTheme } = useBrandTheme();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset theme to defaults on home page
  useEffect(() => {
    resetTheme();
  }, [resetTheme]);
  const [form, setForm] = useState({
    brand_name: '',
    website_url: '',
    email: '',
    industry: '',
    competitors: '',
    keywords: '',
    social_linkedin: '',
    social_twitter: '',
    depth: 'comprehensive',
  });

  const canSubmit = form.brand_name.trim() && form.website_url.trim() && form.email.trim();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setIsSubmitting(true);

    const payload = {
      brand_name: form.brand_name.trim(),
      website_url: form.website_url.trim(),
      email: form.email.trim(),
      industry: form.industry.trim(),
      known_competitors: form.competitors
        ? form.competitors.split(',').map((c) => c.trim()).filter(Boolean)
        : [],
      target_keywords: form.keywords
        ? form.keywords.split(',').map((k) => k.trim()).filter(Boolean)
        : [],
      social_profiles: {
        ...(form.social_linkedin && { linkedin: form.social_linkedin.trim() }),
        ...(form.social_twitter && { twitter: form.social_twitter.trim() }),
      },
      depth: form.depth,
    };

    try {
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      navigate(`/analysis/${data.job_id}`);
    } catch {
      toast({
        title: 'Could not reach the agent server',
        description: 'Make sure the backend is running on ' + API_BASE,
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  return (
    <div className="min-h-screen bg-background">
      {/* Nav - Sharp UI Header */}
      <nav className="header-sharp sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="Brothers Automate" className="h-9" />
            <span className="font-bold text-lg uppercase tracking-wide">
              Intelligence
            </span>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-sharp-secondary text-xs py-2 px-4"
          >
            Past Analyses
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-12 animate-fade-in">
            <div className="badge-sharp-accent inline-flex items-center mb-6">
              <Shield className="w-3.5 h-3.5 mr-2" />
              Done-For-You Intelligence
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-4 leading-tight text-foreground">
              KNOW YOUR MARKET.{' '}
              <span className="text-brand-accent">OWN YOUR POSITION.</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              AI agents crawl, research, and analyze your brand and competitors—delivering
              a complete intelligence report while you sleep. <strong>No manual work. No guesswork.</strong>
            </p>
          </div>

          {/* Pipeline visual */}
          <div className="flex flex-wrap justify-center gap-3 mb-12 animate-slide-up">
            {PIPELINE_STEPS.map((step, i) => {
              const Icon = step.icon;
              return (
                <React.Fragment key={step.label}>
                  <div className="flex items-center gap-2 bg-card border border-border px-4 py-2 text-sm" style={{borderRadius: '2px'}}>
                    <Icon className="w-4 h-4 text-brand-accent" />
                    <span className="font-semibold uppercase text-xs tracking-wide">{step.label}</span>
                  </div>
                  {i < PIPELINE_STEPS.length - 1 && (
                    <ArrowRight className="w-5 h-5 text-brand-accent self-center hidden md:block" />
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {/* Form - Sharp UI Card */}
          <div className="max-w-2xl mx-auto card-sharp bg-card p-8 animate-slide-up">
            <form onSubmit={handleSubmit} className="space-y-6">
              <h2 className="text-xl font-bold text-foreground uppercase tracking-wide">
                Start Intelligence Analysis
              </h2>

              {/* Required fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="brand_name" className="label-sharp block mb-2">
                    Brand Name <span className="text-destructive">*</span>
                  </label>
                  <input
                    id="brand_name"
                    value={form.brand_name}
                    onChange={set('brand_name')}
                    placeholder="Acme Corp"
                    className="input-sharp w-full"
                  />
                </div>
                <div>
                  <label htmlFor="website_url" className="label-sharp block mb-2">
                    Website URL <span className="text-destructive">*</span>
                  </label>
                  <input
                    id="website_url"
                    value={form.website_url}
                    onChange={set('website_url')}
                    placeholder="https://acme.com"
                    type="url"
                    className="input-sharp w-full"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="email" className="label-sharp block mb-2">
                  Email Address <span className="text-destructive">*</span>
                </label>
                <input
                  id="email"
                  value={form.email}
                  onChange={set('email')}
                  placeholder="you@company.com"
                  type="email"
                  className="input-sharp w-full"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  We'll send your report links here when the analysis is complete.
                </p>
              </div>

              <div>
                <label htmlFor="industry" className="label-sharp block mb-2">Industry / Vertical</label>
                <input
                  id="industry"
                  value={form.industry}
                  onChange={set('industry')}
                  placeholder="e.g. SaaS, E-commerce, FinTech"
                  className="input-sharp w-full"
                />
              </div>

              {/* Optional extras */}
              <div>
                <label htmlFor="competitors" className="label-sharp block mb-2">Known Competitors (comma-separated domains)</label>
                <input
                  id="competitors"
                  value={form.competitors}
                  onChange={set('competitors')}
                  placeholder="competitor1.com, competitor2.com"
                  className="input-sharp w-full"
                />
              </div>

              <div>
                <label htmlFor="keywords" className="label-sharp block mb-2">Target Keywords (comma-separated)</label>
                <input
                  id="keywords"
                  value={form.keywords}
                  onChange={set('keywords')}
                  placeholder="brand monitoring, competitor analysis"
                  className="input-sharp w-full"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="social_linkedin" className="label-sharp block mb-2">LinkedIn URL</label>
                  <input
                    id="social_linkedin"
                    value={form.social_linkedin}
                    onChange={set('social_linkedin')}
                    placeholder="https://linkedin.com/company/acme"
                    className="input-sharp w-full"
                  />
                </div>
                <div>
                  <label htmlFor="social_twitter" className="label-sharp block mb-2">Twitter / X URL</label>
                  <input
                    id="social_twitter"
                    value={form.social_twitter}
                    onChange={set('social_twitter')}
                    placeholder="https://x.com/acme"
                    className="input-sharp w-full"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="depth" className="label-sharp block mb-2">Analysis Depth</label>
                <select
                  id="depth"
                  value={form.depth}
                  onChange={set('depth')}
                  className="input-sharp w-full"
                >
                  <option value="quick">Quick (~2 min)</option>
                  <option value="standard">Standard (~5 min)</option>
                  <option value="comprehensive">Comprehensive (~10 min)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={!canSubmit || isSubmitting}
                className="w-full btn-sharp-primary py-4 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Launching Agents...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5 mr-2" />
                    Run Brand Intelligence
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 bg-secondary/20">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-3xl font-bold text-center mb-12 text-foreground uppercase tracking-wide">
            What We Discover For You
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Search, title: 'Brand Profile', desc: 'Messaging, positioning, value props, target audience, SWOT analysis' },
              { icon: Users, title: 'Competitor Map', desc: 'Identify up to 8 competitors with full profiles and differentiation' },
              { icon: BarChart3, title: 'SEO Intel', desc: 'Organic traffic, keyword rankings, backlinks, content gaps' },
              { icon: Target, title: 'Strategy', desc: 'Prioritized recommendations, quick wins, and long-term roadmap' },
            ].map((feat) => {
              const Icon = feat.icon;
              return (
                <div key={feat.title} className="card-sharp bg-card p-6">
                  <div className="w-12 h-12 bg-primary flex items-center justify-center mb-4" style={{borderRadius: '4px'}}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-bold mb-2 text-foreground uppercase text-sm tracking-wide">
                    {feat.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">{feat.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Tool logos */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-3xl text-center">
          <p className="label-sharp mb-6">Powered by</p>
          <div className="flex flex-wrap justify-center gap-4">
            {['Firecrawl', 'Tavily', 'Playwright', 'DataForSEO', 'Claude / GPT'].map((tool) => (
              <span key={tool} className="badge-sharp">
                {tool}
              </span>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
