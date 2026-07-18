import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export const FinanceAnalyticsDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [revenue, setRevenue] = useState(0.0);
  const [profit, setProfit] = useState(0.0);

  const fetchFinanceData = async () => {
    try {
      const revRes = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'REVENUE' })
      });
      if (revRes.ok) {
        const d = await revRes.json();
        setRevenue(d.value);
      }

      const gpRes = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'GROSS_PROFIT' })
      });
      if (gpRes.ok) {
        const d = await gpRes.json();
        setProfit(d.value);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (accessToken) fetchFinanceData();
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">Finance Ledger Analytics</h1>
        <p className="text-sm text-muted-foreground mt-1.5">Track dynamic budgets variance, cash position, asset utilization, and P&L balances.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Total Revenue</span>
          <span className="text-3xl font-bold text-white block mt-2">₹{revenue.toLocaleString()}</span>
        </div>
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Gross Profit</span>
          <span className="text-3xl font-bold text-white block mt-2">₹{profit.toLocaleString()}</span>
        </div>
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Budget Variance</span>
          <span className="text-3xl font-bold text-white block mt-2">0.0%</span>
        </div>
      </div>
    </div>
  );
};
