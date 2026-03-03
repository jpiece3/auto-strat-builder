import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Check, Mail, FileText, Target, Zap, TrendingUp, Loader2, Search, Globe, BarChart3, Users } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface JobStatus {
  job_id: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  report_path: string | null;
  errors: string[];
  tasks_completed: number;
  tasks_total: number;
}

const AGENT_STEPS = [
  { label: 'Brand Discovery', icon: Search, description: 'Crawling website and analyzing brand identity' },
  { label: 'Competitor Intelligence', icon: Users, description: 'Identifying and profiling competitors' },
  { label: 'SEO Analysis', icon: BarChart3, description: 'Analyzing keywords, backlinks, and rankings' },
  { label: 'Web Presence', icon: Globe, description: 'Scanning social profiles and online reputation' },
  { label: 'Report Generation', icon: FileText, description: 'Compiling comprehensive intelligence report' },
];

const ThankYou: React.FC = () => {
  const location = useLocation();
  const jobId = (location.state as { jobId?: string })?.jobId;
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [polling, setPolling] = useState(!!jobId);

  useEffect(() => {
    if (!jobId) return;

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status/${jobId}`);
        if (res.ok) {
          const data: JobStatus = await res.json();
          setJobStatus(data);
          if (data.status === 'completed' || data.status === 'failed') {
            setPolling(false);
          }
        }
      } catch {
        // Backend may not be running, that's fine
      }
    };

    poll();
    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, [jobId]);

  const tasksCompleted = jobStatus?.tasks_completed ?? 0;
  const isRunning = polling && jobStatus?.status === 'running';
  const isComplete = jobStatus?.status === 'completed';

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto text-center">
          {/* Success Header */}
          <div className="mb-12 animate-fade-in">
            <div className="w-20 h-20 bg-success rounded-full flex items-center justify-center mx-auto mb-6 animate-scale-in">
              {isRunning ? (
                <Loader2 className="w-10 h-10 text-success-foreground animate-spin" />
              ) : (
                <Check className="w-10 h-10 text-success-foreground" />
              )}
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              {isRunning
                ? 'Analyzing Your Brand...'
                : isComplete
                  ? 'Your Intelligence Report is Ready!'
                  : 'Your Custom Automation Strategy Report is on its way!'}
            </h1>
            <p className="text-xl text-muted-foreground mb-8">
              {isRunning
                ? 'Our AI agents are gathering comprehensive intelligence'
                : 'Check your email in the next 5 minutes'}
            </p>
          </div>

          {/* Live Agent Progress */}
          {jobId && (
            <Card className="p-8 shadow-medium gradient-card animate-slide-up mb-8">
              <h2 className="text-2xl font-bold text-foreground mb-8">
                Agent Pipeline Progress
              </h2>
              <div className="space-y-4">
                {AGENT_STEPS.map((step, idx) => {
                  const StepIcon = step.icon;
                  const isDone = idx < tasksCompleted;
                  const isCurrent = idx === tasksCompleted && isRunning;
                  return (
                    <div
                      key={step.label}
                      className={`flex items-center gap-4 p-4 rounded-lg transition-smooth ${
                        isDone
                          ? 'bg-success/10 border border-success/20'
                          : isCurrent
                            ? 'bg-primary/10 border border-primary/30'
                            : 'bg-accent/20'
                      }`}
                    >
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                          isDone
                            ? 'bg-success'
                            : isCurrent
                              ? 'bg-primary'
                              : 'bg-muted'
                        }`}
                      >
                        {isDone ? (
                          <Check className="w-5 h-5 text-success-foreground" />
                        ) : isCurrent ? (
                          <Loader2 className="w-5 h-5 text-primary-foreground animate-spin" />
                        ) : (
                          <StepIcon className="w-5 h-5 text-muted-foreground" />
                        )}
                      </div>
                      <div className="text-left flex-1">
                        <div className="font-semibold text-foreground">{step.label}</div>
                        <div className="text-sm text-muted-foreground">{step.description}</div>
                      </div>
                      {isDone && (
                        <span className="text-xs font-medium text-success">Complete</span>
                      )}
                      {isCurrent && (
                        <span className="text-xs font-medium text-primary">Running...</span>
                      )}
                    </div>
                  );
                })}
              </div>
              {isComplete && jobStatus?.report_path && (
                <div className="mt-6 p-4 rounded-lg bg-success/10 border border-success/20 text-success font-medium">
                  Report generated successfully
                </div>
              )}
              {jobStatus?.status === 'failed' && (
                <div className="mt-6 p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive font-medium">
                  Some steps encountered errors. A partial report may still be available.
                </div>
              )}
            </Card>
          )}

          {/* What's Included */}
          <Card className="p-8 shadow-medium gradient-card animate-slide-up mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-8">
              Here's what's included in your personalized report:
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="flex items-start gap-4 p-6 rounded-lg bg-accent/30 hover:bg-accent/50 transition-smooth">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                  <Zap className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-foreground mb-2">Brand Intelligence</h3>
                  <p className="text-muted-foreground text-sm">
                    Complete brand profile including messaging, positioning, value propositions, and SWOT analysis
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-6 rounded-lg bg-accent/30 hover:bg-accent/50 transition-smooth">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-foreground mb-2">SEO & Traffic Analysis</h3>
                  <p className="text-muted-foreground text-sm">
                    Keyword rankings, backlink profile, organic traffic metrics, and content gap analysis
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-6 rounded-lg bg-accent/30 hover:bg-accent/50 transition-smooth">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-foreground mb-2">Competitive Landscape</h3>
                  <p className="text-muted-foreground text-sm">
                    Detailed competitor profiles, market positioning map, and competitive benchmarking
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-6 rounded-lg bg-accent/30 hover:bg-accent/50 transition-smooth">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-foreground mb-2">Strategic Recommendations</h3>
                  <p className="text-muted-foreground text-sm">
                    Prioritized action items, quick wins, and long-term strategy roadmap
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8 p-6 rounded-lg bg-success/10 border border-success/20">
              <div className="flex items-center justify-center gap-3 mb-3">
                <TrendingUp className="w-6 h-6 text-success" />
                <h3 className="text-lg font-semibold text-success">Powered by AI Agents</h3>
              </div>
              <p className="text-success font-medium">
                Our autonomous agents use Firecrawl, Tavily, Playwright, and DataForSEO
                to build a comprehensive intelligence dossier on your brand and competitors
              </p>
            </div>
          </Card>

          {/* Next Steps */}
          <Card className="p-8 shadow-soft animate-slide-up">
            <div className="flex items-center justify-center gap-3 mb-6">
              <Mail className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">What happens next?</h2>
            </div>

            <div className="space-y-4 text-left max-w-2xl mx-auto">
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-primary font-semibold text-sm">1</span>
                </div>
                <p className="text-muted-foreground">
                  <strong className="text-foreground">Check your email</strong> - Your personalized report will arrive within 5 minutes
                </p>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-primary font-semibold text-sm">2</span>
                </div>
                <p className="text-muted-foreground">
                  <strong className="text-foreground">Review your quick wins</strong> - Start with the 3 immediate actions we've identified
                </p>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-primary font-semibold text-sm">3</span>
                </div>
                <p className="text-muted-foreground">
                  <strong className="text-foreground">Optional: Book a strategy call</strong> - We'll include a link to discuss implementation with our team
                </p>
              </div>
            </div>
          </Card>

          {/* CTA */}
          <div className="mt-12 text-center animate-fade-in">
            <Button
              onClick={() => window.location.href = '/'}
              className="gradient-hero hover:opacity-90 text-lg px-8 py-3"
            >
              Create Another Report
            </Button>
            <p className="text-sm text-muted-foreground mt-4">
              Want to help a colleague? Share this assessment with your team!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThankYou;
