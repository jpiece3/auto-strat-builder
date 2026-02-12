import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [form, setForm] = useState({
    brand_name: '',
    website_url: '',
    industry: '',
    competitors: '',
    keywords: '',
    social_linkedin: '',
    social_twitter: '',
    depth: 'comprehensive',
  });

  const canSubmit = form.brand_name.trim() && form.website_url.trim();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setIsSubmitting(true);

    const payload = {
      brand_name: form.brand_name.trim(),
      website_url: form.website_url.trim(),
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
    <div className="min-h-screen gradient-bg">
      {/* Nav */}
      <nav className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="Brothers Automate" className="h-10" />
            <span className="font-bold text-lg text-foreground">
              Intelligence
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
            Past Analyses
          </Button>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-12 animate-fade-in">
            <Badge variant="secondary" className="mb-4 px-4 py-1.5 text-sm shadow-soft">
              <Shield className="w-3.5 h-3.5 mr-1.5" />
              Done-For-You Intelligence
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight text-foreground">
              Know Your Market.{' '}
              <span className="gradient-cta bg-clip-text text-transparent">Own Your Position.</span>
            </h1>
            <p className="text-lg text-muted max-w-2xl mx-auto">
              Our AI agents crawl, research, and analyze your brand and competitors—delivering
              a complete intelligence report while you sleep. No manual work. No guesswork.
            </p>
          </div>

          {/* Pipeline visual */}
          <div className="flex flex-wrap justify-center gap-3 mb-12 animate-slide-up">
            {PIPELINE_STEPS.map((step, i) => {
              const Icon = step.icon;
              return (
                <React.Fragment key={step.label}>
                  <div className="flex items-center gap-2 bg-background border rounded-full px-4 py-2 shadow-soft text-sm">
                    <Icon className="w-4 h-4 text-primary" />
                    <span className="font-medium">{step.label}</span>
                  </div>
                  {i < PIPELINE_STEPS.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-muted-foreground self-center hidden md:block" />
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {/* Form */}
          <Card className="max-w-2xl mx-auto p-8 shadow-medium gradient-card animate-scale-in">
            <form onSubmit={handleSubmit} className="space-y-6">
              <h2 className="text-xl font-semibold text-foreground">
                Start Intelligence Analysis
              </h2>

              {/* Required fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="brand_name">
                    Brand Name <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="brand_name"
                    value={form.brand_name}
                    onChange={set('brand_name')}
                    placeholder="Acme Corp"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="website_url">
                    Website URL <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="website_url"
                    value={form.website_url}
                    onChange={set('website_url')}
                    placeholder="https://acme.com"
                    type="url"
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="industry">Industry / Vertical</Label>
                <Input
                  id="industry"
                  value={form.industry}
                  onChange={set('industry')}
                  placeholder="e.g. SaaS, E-commerce, FinTech"
                  className="mt-1"
                />
              </div>

              {/* Optional extras */}
              <div>
                <Label htmlFor="competitors">Known Competitors (comma-separated domains)</Label>
                <Input
                  id="competitors"
                  value={form.competitors}
                  onChange={set('competitors')}
                  placeholder="competitor1.com, competitor2.com"
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="keywords">Target Keywords (comma-separated)</Label>
                <Input
                  id="keywords"
                  value={form.keywords}
                  onChange={set('keywords')}
                  placeholder="brand monitoring, competitor analysis"
                  className="mt-1"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="social_linkedin">LinkedIn URL</Label>
                  <Input
                    id="social_linkedin"
                    value={form.social_linkedin}
                    onChange={set('social_linkedin')}
                    placeholder="https://linkedin.com/company/acme"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="social_twitter">Twitter / X URL</Label>
                  <Input
                    id="social_twitter"
                    value={form.social_twitter}
                    onChange={set('social_twitter')}
                    placeholder="https://x.com/acme"
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="depth">Analysis Depth</Label>
                <select
                  id="depth"
                  value={form.depth}
                  onChange={set('depth')}
                  className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="quick">Quick (~2 min)</option>
                  <option value="standard">Standard (~5 min)</option>
                  <option value="comprehensive">Comprehensive (~10 min)</option>
                </select>
              </div>

              <Button
                type="submit"
                disabled={!canSubmit || isSubmitting}
                className="w-full gradient-cta hover:opacity-90 text-base py-3"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Launching Agents...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    Run Brand Intelligence
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </form>
          </Card>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 bg-primary/5">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-3xl font-bold text-center mb-12 text-foreground">
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
                <Card key={feat.title} className="p-6 shadow-soft hover-lift gradient-card transition-spring">
                  <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-primary-foreground" />
                  </div>
                  <h3 className="font-semibold mb-2 text-foreground">
                    {feat.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">{feat.desc}</p>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Tool logos */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-3xl text-center">
          <p className="text-sm text-muted-foreground mb-6">Powered by</p>
          <div className="flex flex-wrap justify-center gap-6">
            {['Firecrawl', 'Tavily', 'Playwright', 'DataForSEO', 'Claude / GPT'].map((tool) => (
              <Badge key={tool} variant="outline" className="px-4 py-2 text-sm font-medium">
                {tool}
              </Badge>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
