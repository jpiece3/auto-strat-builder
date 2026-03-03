import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth-context';
import { Lock, Loader2, AlertTriangle } from 'lucide-react';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const ok = await login(password);
    setLoading(false);
    if (ok) {
      navigate('/dashboard', { replace: true });
    } else {
      setError('Invalid password');
      setPassword('');
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div
            className="w-14 h-14 bg-primary flex items-center justify-center mx-auto mb-4"
            style={{ borderRadius: '4px' }}
          >
            <Lock className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-foreground uppercase tracking-wide">
            Admin Login
          </h1>
          <p className="text-sm text-muted-foreground mt-2">
            Enter the admin password to view reports
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card-sharp bg-card p-6">
          {error && (
            <div className="flex items-center gap-2 text-destructive text-sm mb-4 p-3 bg-destructive/5 border border-destructive" style={{ borderRadius: '4px' }}>
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <label className="block mb-4">
            <span className="stat-label-sharp mb-2 block">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-background border border-border text-foreground text-sm focus:outline-none focus:border-primary"
              style={{ borderRadius: '4px' }}
              placeholder="Enter admin password"
              autoFocus
              required
            />
          </label>

          <button
            type="submit"
            disabled={loading || !password}
            className="btn-sharp-primary w-full py-3 text-sm disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin mx-auto" />
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <p className="text-center text-xs text-muted-foreground mt-6">
          Brothers Automate Intelligence Agent
        </p>
      </div>
    </div>
  );
};

export default Login;
