import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import {
  Check,
  Loader2,
  Search,
  Globe,
  BarChart3,
  Users,
  FileText,
  ArrowLeft,
  AlertTriangle,
  Clock,
  Download,
  ExternalLink,
  type LucideIcon,
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '';

interface JobStatus {
  job_id: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  report_path: string | null;
  html_report_path: string | null;
  errors: string[];
  tasks_completed: number;
  tasks_total: number;
}

interface AgentStep {
  label: string;
  icon: LucideIcon;
  description: string;
  detail: string;
}

const AGENT_STEPS: AgentStep[] = [
  {
    label: 'Brand Discovery',
    icon: Search,
    description: 'Crawling website and analyzing brand identity',
    detail: 'Firecrawl scrapes your website, extracts messaging, value props, and content structure. Tavily searches for brand mentions and press coverage. LLM synthesizes a complete brand profile.',
  },
  {
    label: 'Competitor Intelligence',
    icon: Users,
    description: 'Identifying and profiling competitors',
    detail: 'DataForSEO finds SEO competitors by keyword overlap. Tavily searches for market comparisons. Each competitor gets a full profile with positioning, strengths, and weaknesses.',
  },
  {
    label: 'SEO Analysis',
    icon: BarChart3,
    description: 'Analyzing keywords, backlinks, and rankings',
    detail: 'DataForSEO pulls domain metrics, organic keyword rankings, backlink profiles, and tech stack. Keyword gap analysis compares your coverage against competitors.',
  },
  {
    label: 'Web Presence',
    icon: Globe,
    description: 'Scanning social profiles and online reputation',
    detail: 'Playwright visits social media profiles to collect follower counts and activity. Tavily searches reviews, ratings, and news sentiment across the web.',
  },
  {
    label: 'Report Compilation',
    icon: FileText,
    description: 'Compiling comprehensive intelligence report',
    detail: 'LLM synthesizes all gathered data into an executive summary, competitive positioning analysis, SWOT matrix, and prioritized strategic recommendations.',
  },
];

const Analysis: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [expandedStep, setExpandedStep] = useState<number | null>(null);

  // Poll for job status
  useEffect(() => {
    if (!jobId) return;
    let active = true;

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status/${jobId}`);
        if (res.ok && active) {
          setStatus(await res.json());
        }
      } catch {
        // backend might be down
      }
    };

    poll();
    const interval = setInterval(poll, 2500);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [jobId]);

  // Elapsed timer
  useEffect(() => {
    if (!status || status.status !== 'running') return;
    const t = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(t);
  }, [status?.status]);

  const tasksCompleted = status?.tasks_completed ?? 0;
  const isRunning = status?.status === 'running';
  const isComplete = status?.status === 'completed';
  const isFailed = status?.status === 'failed';
  const progressPct = Math.round((tasksCompleted / AGENT_STEPS.length) * 100);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return m > 0 ? `${m}m ${sec}s` : `${sec}s`;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <nav className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <img src="/logo.png" alt="Brothers Automate" className="h-10" />
            <span className="font-bold text-lg text-foreground">
              Intelligence
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
            <ArrowLeft className="w-4 h-4 mr-1" /> New Analysis
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-10 max-w-3xl">
        {/* Header */}
        <div className="text-center mb-10 animate-fade-in">
          <div
            className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
              isComplete ? 'bg-success' : isFailed ? 'bg-destructive' : 'bg-primary'
            }`}
          >
            {isRunning ? (
              <Loader2 className="w-8 h-8 text-white animate-spin" />
            ) : isComplete ? (
              <Check className="w-8 h-8 text-white" />
            ) : isFailed ? (
              <AlertTriangle className="w-8 h-8 text-white" />
            ) : (
              <Clock className="w-8 h-8 text-white" />
            )}
          </div>

          <h1 className="text-3xl font-bold mb-2 text-foreground">
            {isRunning
              ? 'Agents Working...'
              : isComplete
                ? 'Analysis Complete'
                : isFailed
                  ? 'Analysis Encountered Issues'
                  : 'Waiting for Status...'}
          </h1>

          {isRunning && (
            <div className="flex items-center justify-center gap-4 text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" /> {formatTime(elapsed)}
              </span>
              <span>
                {tasksCompleted} / {AGENT_STEPS.length} agents complete
              </span>
            </div>
          )}

          {isComplete && status?.completed_at && (
            <p className="text-muted-foreground">
              Completed at {new Date(status.completed_at).toLocaleTimeString()}
            </p>
          )}
        </div>

        {/* Progress bar */}
        <div className="mb-8">
          <Progress value={isComplete ? 100 : progressPct} className="h-3" />
          <p className="text-xs text-muted-foreground mt-1 text-right">{isComplete ? 100 : progressPct}%</p>
        </div>

        {/* Agent steps */}
        <div className="space-y-3 mb-10">
          {AGENT_STEPS.map((step, idx) => {
            const StepIcon = step.icon;
            const isDone = idx < tasksCompleted;
            const isCurrent = idx === tasksCompleted && isRunning;
            const isExpanded = expandedStep === idx;

            return (
              <Card
                key={step.label}
                className={`overflow-hidden transition-smooth cursor-pointer ${
                  isDone
                    ? 'border-success/30 bg-success/5'
                    : isCurrent
                      ? 'border-primary/40 bg-primary/5 shadow-medium'
                      : 'border-border bg-background'
                }`}
                onClick={() => setExpandedStep(isExpanded ? null : idx)}
              >
                <div className="flex items-center gap-4 p-4">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-smooth ${
                      isDone
                        ? 'bg-success'
                        : isCurrent
                          ? 'bg-primary'
                          : 'bg-muted'
                    }`}
                  >
                    {isDone ? (
                      <Check className="w-5 h-5 text-white" />
                    ) : isCurrent ? (
                      <Loader2 className="w-5 h-5 text-white animate-spin" />
                    ) : (
                      <StepIcon className="w-5 h-5 text-muted-foreground" />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm">{step.label}</div>
                    <div className="text-xs text-muted-foreground truncate">{step.description}</div>
                  </div>

                  {isDone && <span className="text-xs font-medium text-success flex-shrink-0">Done</span>}
                  {isCurrent && (
                    <span className="text-xs font-medium text-primary flex-shrink-0 animate-pulse">Running</span>
                  )}
                </div>

                {isExpanded && (
                  <div className="px-4 pb-4 pt-0 text-sm text-muted-foreground border-t mx-4 mt-0 pt-3">
                    {step.detail}
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        {/* Errors */}
        {status?.errors && status.errors.length > 0 && (
          <Card className="p-4 mb-8 border-destructive/30 bg-destructive/5">
            <h3 className="font-semibold text-sm mb-2 flex items-center gap-2 text-destructive">
              <AlertTriangle className="w-4 h-4" /> Errors
            </h3>
            <ul className="text-xs text-muted-foreground space-y-1">
              {status.errors.map((err, i) => (
                <li key={i} className="truncate">- {err}</li>
              ))}
            </ul>
          </Card>
        )}

        {/* Completion card */}
        {isComplete && (
          <Card className="p-6 border-success/30 bg-success/5 animate-scale-in">
            <div className="text-center mb-6">
              <Check className="w-10 h-10 text-success mx-auto mb-3" />
              <h2 className="text-lg font-bold mb-1 text-foreground">
                Intelligence Report Generated
              </h2>
              <p className="text-sm text-muted-foreground">
                Your comprehensive brand analysis is ready
              </p>
            </div>

            {/* Download options */}
            <div className="space-y-3 mb-6">
              {status?.html_report_path && (
                <div className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <FileText className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <div className="font-semibold text-sm">HTML Report</div>
                      <div className="text-xs text-muted-foreground">Professional branded report</div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    className="gradient-cta hover:opacity-90"
                    onClick={() => {
                      window.open(`${API_BASE}/api/reports/${jobId}/html`, '_blank');
                    }}
                  >
                    <ExternalLink className="w-4 h-4 mr-1" />
                    View Report
                  </Button>
                </div>
              )}

              {status?.report_path && (
                <div className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                      <FileText className="w-5 h-5 text-accent" />
                    </div>
                    <div>
                      <div className="font-semibold text-sm">Markdown Report</div>
                      <div className="text-xs text-muted-foreground">Plain text format</div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      window.open(`${API_BASE}/api/reports/${jobId}/markdown`, '_blank');
                    }}
                  >
                    <ExternalLink className="w-4 h-4 mr-1" />
                    View Report
                  </Button>
                </div>
              )}
            </div>

            <div className="flex gap-3 justify-center">
              <Button onClick={() => navigate('/')} variant="outline" size="sm">
                New Analysis
              </Button>
              <Button onClick={() => navigate('/dashboard')} size="sm" className="gradient-cta hover:opacity-90">
                <ExternalLink className="w-4 h-4 mr-1" />
                View All Reports
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Analysis;
