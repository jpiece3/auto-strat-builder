import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/hooks/use-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Plus,
  ArrowRight,
  Check,
  Loader2,
  AlertTriangle,
  Clock,
  RefreshCw,
  Trash2,
  Copy,
  FileText,
  ExternalLink,
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '';

interface Job {
  job_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  brand_name?: string;
  website_url?: string;
  report_path?: string;
  html_report_path?: string;
}

const STATUS_CONFIG: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline'; icon: React.ReactNode }> = {
  running: { label: 'Running', variant: 'default', icon: <Loader2 className="w-3 h-3 animate-spin" /> },
  completed: { label: 'Completed', variant: 'secondary', icon: <Check className="w-3 h-3" /> },
  failed: { label: 'Failed', variant: 'destructive', icon: <AlertTriangle className="w-3 h-3" /> },
};

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [serverUp, setServerUp] = useState(true);
  const [deleteJobId, setDeleteJobId] = useState<string | null>(null);

  const fetchJobs = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/jobs`);
      if (res.ok) {
        setJobs(await res.json());
        setServerUp(true);
      }
    } catch {
      setServerUp(false);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (jobId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        toast({
          title: 'Analysis deleted',
          description: 'The analysis has been removed from the dashboard.',
        });
        setJobs((prev) => prev.filter((j) => j.job_id !== jobId));
      } else {
        throw new Error('Delete failed');
      }
    } catch {
      toast({
        title: 'Could not delete analysis',
        description: 'An error occurred while deleting.',
        variant: 'destructive',
      });
    }
    setDeleteJobId(null);
  };

  const handleCopyUrl = (jobId: string) => {
    const url = `${window.location.origin}/analysis/${jobId}`;
    navigator.clipboard.writeText(url);
    toast({
      title: 'URL copied',
      description: 'Analysis URL copied to clipboard.',
    });
  };

  const handleViewReport = (jobId: string) => {
    window.open(`${API_BASE}/api/reports/${jobId}/html`, '_blank');
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

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
          <Button size="sm" onClick={() => navigate('/')} className="gradient-cta hover:opacity-90">
            <Plus className="w-4 h-4 mr-1" /> New Analysis
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-10 max-w-3xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-foreground">
              Past Analyses
            </h1>
            <p className="text-sm text-muted-foreground">All brand intelligence runs</p>
          </div>
          <Button variant="ghost" size="sm" onClick={fetchJobs}>
            <RefreshCw className="w-4 h-4 mr-1" /> Refresh
          </Button>
        </div>

        {!serverUp && (
          <Card className="p-6 mb-6 border-destructive/30 bg-destructive/5 text-center">
            <AlertTriangle className="w-8 h-8 text-destructive mx-auto mb-2" />
            <p className="font-semibold mb-1">Agent server is not reachable</p>
            <p className="text-sm text-muted-foreground mb-3">
              Start the backend with: <code className="bg-muted px-2 py-0.5 rounded text-xs">uvicorn agent.server:app --port 8000</code>
            </p>
          </Card>
        )}

        {loading && (
          <div className="text-center py-20">
            <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-3" />
            <p className="text-muted-foreground">Loading jobs...</p>
          </div>
        )}

        {!loading && jobs.length === 0 && serverUp && (
          <Card className="p-12 text-center gradient-card shadow-soft">
            <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-lg font-semibold mb-2 text-foreground">
              No analyses yet
            </h2>
            <p className="text-muted-foreground mb-6">
              Run your first brand intelligence analysis to see results here.
            </p>
            <Button onClick={() => navigate('/')} className="gradient-cta hover:opacity-90">
              <Plus className="w-4 h-4 mr-1" /> Start Analysis
            </Button>
          </Card>
        )}

        {!loading && jobs.length > 0 && (
          <div className="space-y-3">
            {jobs
              .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
              .map((job) => {
                const cfg = STATUS_CONFIG[job.status] ?? STATUS_CONFIG.running;
                return (
                  <Card
                    key={job.job_id}
                    className="p-4 transition-spring"
                  >
                    <div className="flex items-start gap-4">
                      <div
                        className="flex-1 min-w-0 cursor-pointer"
                        onClick={() => navigate(`/analysis/${job.job_id}`)}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-sm">
                            {job.brand_name || job.job_id}
                          </span>
                          <Badge variant={cfg.variant} className="text-xs flex items-center gap-1">
                            {cfg.icon} {cfg.label}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {job.website_url && <span className="mr-3">{job.website_url}</span>}
                          Started {new Date(job.started_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/analysis/${job.job_id}`)}
                          title="View analysis"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                        {job.status === 'completed' && job.html_report_path && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewReport(job.job_id)}
                            title="View HTML report"
                          >
                            <FileText className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopyUrl(job.job_id)}
                          title="Copy URL"
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteJobId(job.job_id)}
                          className="text-destructive hover:text-destructive"
                          title="Delete analysis"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                );
              })}
          </div>
        )}

        {/* Delete confirmation dialog */}
        <AlertDialog open={!!deleteJobId} onOpenChange={() => setDeleteJobId(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Analysis?</AlertDialogTitle>
              <AlertDialogDescription>
                This will remove the analysis from your dashboard. The report files will remain on disk.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => deleteJobId && handleDelete(deleteJobId)}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
};

export default Dashboard;
