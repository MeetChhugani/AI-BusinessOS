import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { ForecastResult } from '../../types/analytics';

export const ForecastDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [forecasts, setForecasts] = useState<ForecastResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchForecast = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/analytics/forecasts?metric_code=REVENUE', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) setForecasts(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) fetchForecast();
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight flex items-center gap-2">
          Statistical Predictive Modeling
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Linear trend baseline forecast models projecting future monthly periods (preparing clean JSON interfaces for future ML models).
        </p>
      </div>

      {/* Projections Table List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : forecasts.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No forecast predictions loaded.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Future Period Date</th>
                <th className="px-6 py-4">Forecast Projection</th>
                <th className="px-6 py-4">Confidence Upper (110%)</th>
                <th className="px-6 py-4 text-right">Confidence Lower (90%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {forecasts.map((f, idx) => (
                <tr key={idx} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4 font-mono font-bold text-indigo-400">{f.date}</td>
                  <td className="px-6 py-4 text-neutral-200">₹{f.value.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="px-6 py-4 text-emerald-400">₹{f.upper.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="px-6 py-4 text-right text-amber-400">₹{f.lower.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
