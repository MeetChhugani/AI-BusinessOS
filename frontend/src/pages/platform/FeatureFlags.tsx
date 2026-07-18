import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { FeatureFlag } from '../../types/platform';
import { ToggleLeft, ToggleRight } from 'lucide-react';

export const FeatureFlags: React.FC = () => {
  const { accessToken } = useAuth();
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchFlags = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/features', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setFlags(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchFlags();
    }
  }, [accessToken]);

  const toggleFlag = async (id: string, currentVal: boolean) => {
    try {
      const res = await fetch(`/api/v1/features/${id}/toggle?enabled=${!currentVal}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        fetchFlags();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Beta Feature Toggles
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Enable or disable modules, experimental dashboards, and API channels in real-time.
        </p>
      </div>

      {/* Feature Flags Grid List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : flags.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No feature flags configured.
        </div>
      ) : (
        <div className="space-y-3.5 text-xs">
          {flags.map(flag => (
            <div key={flag.id} className="p-5 bg-card border border-neutral-800 rounded-2xl flex justify-between items-center hover:bg-secondary/10 transition">
              <div className="space-y-1">
                <span className="font-mono font-bold text-white block">{flag.name}</span>
                <span className="text-[10px] text-muted-foreground block">{flag.description}</span>
              </div>
              <div>
                <button
                  onClick={() => toggleFlag(flag.id, flag.enabled)}
                  className={`flex items-center gap-1.5 p-1 rounded-lg border transition ${
                    flag.enabled 
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25' 
                      : 'bg-neutral-800 text-neutral-500 border-neutral-700'
                  }`}
                >
                  {flag.enabled ? (
                    <>
                      <ToggleRight size={22} />
                      <span className="text-[10px] font-bold pr-2">ENABLED</span>
                    </>
                  ) : (
                    <>
                      <ToggleLeft size={22} />
                      <span className="text-[10px] font-bold pr-2">DISABLED</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
