import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { KPIDefinition } from '../../types/analytics';

export const KPIManager: React.FC = () => {
  const { accessToken } = useAuth();
  const [kpis, setKpis] = useState<KPIDefinition[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchKPIs = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/analytics/kpis', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setKpis(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) fetchKPIs();
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          KPI Targets & Thresholds
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Configure green, yellow, and red boundary alerts triggers for active business metrics.
        </p>
      </div>

      {/* KPIs List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : kpis.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No KPI targets configured.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">KPI Target</th>
                <th className="px-6 py-4">Metric Code</th>
                <th className="px-6 py-4">Target Target</th>
                <th className="px-6 py-4">Yellow Threshold</th>
                <th className="px-6 py-4 text-right">Red Threshold</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {kpis.map(k => (
                <tr key={k.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4 font-bold text-neutral-300">{k.name}</td>
                  <td className="px-6 py-4 font-mono text-neutral-300">{k.metric_code}</td>
                  <td className="px-6 py-4 text-neutral-300">₹{k.target_value.toLocaleString()}</td>
                  <td className="px-6 py-4 text-neutral-400">₹{k.threshold_yellow.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right text-rose-400">₹{k.threshold_red.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
