import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export const InventoryAnalyticsDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [invValue, setInvValue] = useState(0.0);

  const fetchInvData = async () => {
    try {
      const res = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'INVENTORY_VALUE' })
      });
      if (res.ok) {
        const d = await res.json();
        setInvValue(d.value);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (accessToken) fetchInvData();
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">Inventory Turnover & Valuation</h1>
        <p className="text-sm text-muted-foreground mt-1.5">Track warehouse utilization ratios, slow-moving items, and stock value metrics.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Valuation Total</span>
          <span className="text-3xl font-bold text-white block mt-2">₹{invValue.toLocaleString()}</span>
        </div>
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Turnover Ratio</span>
          <span className="text-3xl font-bold text-white block mt-2">5.4x</span>
        </div>
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/40">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Reorder Risk Counts</span>
          <span className="text-3xl font-bold text-white block mt-2">0</span>
        </div>
      </div>
    </div>
  );
};
