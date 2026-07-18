import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export const CRMAnalyticsDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [conversion, setConversion] = useState(0.0);

  const fetchCRMData = async () => {
    try {
      const res = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'LEAD_CONVERSION_RATE' })
      });
      if (res.ok) {
        const d = await res.json();
        setConversion(d.value);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (accessToken) fetchCRMData();
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">CRM Pipeline Funnels</h1>
        <p className="text-sm text-muted-foreground mt-1.5">Track opportunities progress pipelines, win rates, and ranking charts.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Lead Conversion Rate</span>
          <span className="text-3xl font-bold text-white block mt-2">{conversion.toFixed(1)}%</span>
        </div>
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Open Pipeline Value</span>
          <span className="text-3xl font-bold text-white block mt-2">₹1,200,000</span>
        </div>
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Target Conversion</span>
          <span className="text-3xl font-bold text-white block mt-2">30.0%</span>
        </div>
      </div>
    </div>
  );
};
