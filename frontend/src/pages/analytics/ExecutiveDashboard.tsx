import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { DeterministicInsight } from '../../types/analytics';
import { 
  Users, DollarSign, Target, Award,
  AlertTriangle, ArrowUpRight, ArrowDownRight, Compass 
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const ExecutiveDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [revenue, setRevenue] = useState(0.0);
  const [headcount, setHeadcount] = useState(0);
  const [conversion, setConversion] = useState(0.0);
  const [insights, setInsights] = useState<DeterministicInsight[]>([]);
  const fetchMetrics = async () => {
    try {
      // 1. Fetch dynamic calculations
      const revRes = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'REVENUE' })
      });
      if (revRes.ok) {
        const d = await revRes.json();
        setRevenue(d.value);
      }

      const hcRes = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'EMPLOYEE_HEADCOUNT' })
      });
      if (hcRes.ok) {
        const d = await hcRes.json();
        setHeadcount(d.value);
      }

      const convRes = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'LEAD_CONVERSION_RATE' })
      });
      if (convRes.ok) {
        const d = await convRes.json();
        setConversion(d.value);
      }

      // 2. Fetch insights
      const insRes = await fetch('/api/v1/analytics/insights', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (insRes.ok) setInsights(await insRes.json());

    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchMetrics();
    }
  }, [accessToken]);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Executive Control Tower
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            C-Suite summarization aggregating real-time revenues, personnel counts, conversion funnels, and alert notifications.
          </p>
        </div>
      </div>

      {/* Dynamic Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Annual Revenue</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 text-emerald-400">
              <DollarSign size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">₹{revenue.toLocaleString()}</span>
            <span className="text-[10px] text-muted-foreground flex items-center gap-1">
              <ArrowUpRight size={10} className="text-emerald-400" />
              +12.4% vs last calendar month
            </span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Personnel Size</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400">
              <Users size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">{headcount} FTE</span>
            <span className="text-[10px] text-muted-foreground flex items-center gap-1">
              <ArrowUpRight size={10} className="text-indigo-400" />
              Organization growth active
            </span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Lead Conversion</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400">
              <Target size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">{conversion.toFixed(1)}%</span>
            <span className="text-[10px] text-muted-foreground flex items-center gap-1">
              <ArrowDownRight size={10} className="text-rose-400" />
              Pipeline conversions target review
            </span>
          </div>
        </div>
      </div>

      {/* Insights and Quick views */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Deterministic Anomalies Warnings list */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle size={16} className="text-amber-400" />
            Anomalies & Insights Engine
          </h3>
          {insights.length === 0 ? (
            <div className="py-10 text-center text-muted-foreground text-xs">
              No anomalies found. Everything matches target ranges.
            </div>
          ) : (
            <div className="space-y-2.5 text-xs">
              {insights.map((ins, idx) => (
                <div key={idx} className="p-4 bg-secondary/35 border border-border/40 rounded-xl flex justify-between items-center hover:bg-secondary/60 transition">
                  <div className="space-y-1">
                    <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${
                      ins.severity === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-neutral-800 text-neutral-500 border-neutral-700'
                    } mr-2 uppercase`}>
                      {ins.severity}
                    </span>
                    <span className="text-white font-medium">{ins.message}</span>
                  </div>
                  {ins.action_url && (
                    <Link to={ins.action_url} className="px-3 py-1 bg-neutral-800 border border-border/60 hover:bg-neutral-700 rounded text-[10px] font-semibold text-white">
                      Inspect
                    </Link>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Analytics Departments Navigation */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Compass size={16} className="text-muted-foreground" />
            Domain BI Panels
          </h3>
          <div className="space-y-2.5 text-xs">
            <Link to="/dashboard/analytics/hr" className="flex justify-between items-center p-2.5 bg-secondary/30 hover:bg-secondary/65 border border-border/40 rounded-xl text-white transition">
              <span>HR Attrition & Leaves</span>
              <Users size={14} className="text-muted-foreground" />
            </Link>
            <Link to="/dashboard/analytics/crm" className="flex justify-between items-center p-2.5 bg-secondary/30 hover:bg-secondary/65 border border-border/40 rounded-xl text-white transition">
              <span>CRM Pipelines & Funnels</span>
              <Target size={14} className="text-muted-foreground" />
            </Link>
            <Link to="/dashboard/analytics/inventory" className="flex justify-between items-center p-2.5 bg-secondary/30 hover:bg-secondary/65 border border-border/40 rounded-xl text-white transition">
              <span>Inventory Turnover & Value</span>
              <Award size={14} className="text-muted-foreground" />
            </Link>
            <Link to="/dashboard/analytics/finance" className="flex justify-between items-center p-2.5 bg-secondary/30 hover:bg-secondary/65 border border-border/40 rounded-xl text-white transition">
              <span>Finance Gross Profits</span>
              <DollarSign size={14} className="text-muted-foreground" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
