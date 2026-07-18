import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export const HRAnalyticsDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [headcount, setHeadcount] = useState(0);

  const fetchHRData = async () => {
    try {
      const res = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'EMPLOYEE_HEADCOUNT' })
      });
      if (res.ok) {
        const d = await res.json();
        setHeadcount(d.value);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (accessToken) fetchHRData();
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">HR Attrition & Leave Trends</h1>
        <p className="text-sm text-muted-foreground mt-1.5">Track employee growth indexes, headcount, and leave approval distributions.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Total Headcount</span>
          <span className="text-3xl font-bold text-white block mt-2">{headcount} FTE</span>
        </div>
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Attrition Rate</span>
          <span className="text-3xl font-bold text-white block mt-2">4.2%</span>
        </div>
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Leave Requests Approved</span>
          <span className="text-3xl font-bold text-white block mt-2">12</span>
        </div>
      </div>
    </div>
  );
};
