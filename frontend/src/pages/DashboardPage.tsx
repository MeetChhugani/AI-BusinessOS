import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { TrendingUp, Users, Package, ShoppingCart, BarChart2 } from 'lucide-react';

const Skeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={`animate-pulse bg-neutral-800/60 light:bg-neutral-200 rounded-lg ${className}`} />
);

export const DashboardPage: React.FC = () => {
  const { accessToken, user } = useAuth();
  const [revenue, setRevenue] = useState<number | null>(null);
  const [headcount, setHeadcount] = useState<number | null>(null);
  const [inventoryValue, setInventoryValue] = useState<number | null>(null);
  const [conversionRate, setConversionRate] = useState<number | null>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [forecasts, setForecasts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboardData = async () => {
    setIsLoading(true);
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

      const invRes = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'INVENTORY_VALUE' })
      });
      if (invRes.ok) {
        const d = await invRes.json();
        setInventoryValue(d.value);
      }

      const convRes = await fetch('/api/v1/analytics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
        body: JSON.stringify({ metric_code: 'LEAD_CONVERSION_RATE' })
      });
      if (convRes.ok) {
        const d = await convRes.json();
        setConversionRate(d.value);
      }

      // 2. Fetch insights (Foundational Events)
      const insRes = await fetch('/api/v1/analytics/insights', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (insRes.ok) {
        const d = await insRes.json();
        setInsights(d);
      }

      // 3. Fetch forecasts (Analytics & Trends)
      const foreRes = await fetch('/api/v1/analytics/forecasts?metric_code=REVENUE', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (foreRes.ok) {
        const d = await foreRes.json();
        setForecasts(d);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchDashboardData();
    }
  }, [accessToken]);

  const getMonthName = (dateStr: string) => {
    try {
      const dateObj = new Date(dateStr);
      return dateObj.toLocaleString('default', { month: 'short' });
    } catch {
      return dateStr;
    }
  };

  const metrics = [
    { 
      title: 'Gross Revenue', 
      icon: TrendingUp, 
      color: 'text-emerald-400 bg-emerald-500/10',
      value: revenue !== null ? `₹${revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : '0',
      sub: 'Dynamic revenue tracking'
    },
    { 
      title: 'Active Employees', 
      icon: Users, 
      color: 'text-blue-400 bg-blue-500/10',
      value: headcount !== null ? `${headcount} FTE` : '0 FTE',
      sub: 'Active personnel size'
    },
    { 
      title: 'Stock & Inventory', 
      icon: Package, 
      color: 'text-indigo-400 bg-indigo-500/10',
      value: inventoryValue !== null ? `₹${inventoryValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : '₹0',
      sub: 'Total inventory valuation'
    },
    { 
      title: 'Closed Sales', 
      icon: ShoppingCart, 
      color: 'text-purple-400 bg-purple-500/10',
      value: conversionRate !== null ? `${conversionRate.toFixed(1)}%` : '0.0%',
      sub: 'Lead conversion rate'
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Welcome Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Workspace Overview
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Welcome back, {user?.full_name}. Active enterprise shell in development env.
          </p>
        </div>
        
        {/* Timestamp / Access Status */}
        <div className="flex items-center space-x-2 bg-secondary/40 border border-border px-3.5 py-1.5 rounded-lg text-xs font-semibold text-muted-foreground w-fit">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Session: Active (Role: {user?.role})</span>
        </div>
      </div>

      {/* Metrics Card Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((m, i) => (
          <div key={i} className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-40 hover:border-neutral-700 transition">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{m.title}</span>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center border border-white/5 ${m.color}`}>
                <m.icon size={16} />
              </div>
            </div>
            
            <div className="space-y-1.5">
              {isLoading ? (
                <>
                  <Skeleton className="h-7 w-2/3" />
                  <Skeleton className="h-3 w-1/2" />
                </>
              ) : (
                <>
                  <span className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight block">
                    {m.value}
                  </span>
                  <span className="text-[10px] text-muted-foreground font-semibold">
                    {m.sub}
                  </span>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Large Analytics Skeleton Graph & Table Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Large Analytics Card */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col min-h-[350px]">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                <BarChart2 size={14} />
              </div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Analytics & Trends</h3>
            </div>
            {!isLoading && <span className="text-[9px] font-bold text-emerald-400 border border-emerald-500/20 bg-emerald-500/5 px-2 py-0.5 rounded-lg">FORECAST ACTIVATED</span>}
          </div>

          <div className="flex-1 flex flex-col justify-between space-y-4">
            {isLoading ? (
              <div className="flex items-end justify-between h-48 px-4 border-b border-neutral-800 pb-2">
                <Skeleton className="w-[8%] h-[30%]" />
                <Skeleton className="w-[8%] h-[45%]" />
                <Skeleton className="w-[8%] h-[60%]" />
                <Skeleton className="w-[8%] h-[40%]" />
                <Skeleton className="w-[8%] h-[75%]" />
                <Skeleton className="w-[8%] h-[90%]" />
                <Skeleton className="w-[8%] h-[55%]" />
                <Skeleton className="w-[8%] h-[70%]" />
                <Skeleton className="w-[8%] h-[80%]" />
                <Skeleton className="w-[8%] h-[65%]" />
              </div>
            ) : forecasts.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-muted-foreground text-xs">
                No forecasting trends data available
              </div>
            ) : (
              <div className="flex items-end justify-around h-48 px-4 border-b border-neutral-800 pb-2">
                {forecasts.map((f, idx) => {
                  const maxVal = Math.max(...forecasts.map(x => x.value), 1);
                  const heightPct = `${(f.value / maxVal) * 80}%`;
                  return (
                    <div key={idx} className="group relative flex flex-col items-center w-[12%]">
                      {/* Custom styled Tooltip popup on hover */}
                      <div className="absolute bottom-full mb-2 hidden group-hover:flex flex-col items-center bg-neutral-900 border border-neutral-800 p-2.5 rounded-xl shadow-xl text-[9px] text-neutral-200 z-10 w-36 text-center pointer-events-none">
                        <span className="font-bold text-indigo-400">{f.date}</span>
                        <span className="mt-1 font-semibold">Projected Rev:</span>
                        <span className="font-bold text-white">₹{f.value.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                      </div>
                      {/* Color gradient dynamic bar elements */}
                      <div 
                        style={{ height: heightPct }} 
                        className="w-full bg-gradient-to-t from-indigo-600/35 to-indigo-500/80 hover:to-indigo-400 rounded-md border border-indigo-500/25 transition-all duration-300 cursor-pointer"
                      />
                    </div>
                  );
                })}
              </div>
            )}
            
            {isLoading ? (
              <div className="flex justify-between px-2">
                <Skeleton className="h-2 w-8" />
                <Skeleton className="h-2 w-8" />
                <Skeleton className="h-2 w-8" />
                <Skeleton className="h-2 w-8" />
                <Skeleton className="h-2 w-8" />
              </div>
            ) : (
              <div className="flex justify-around px-2 text-[10px] font-bold text-muted-foreground">
                {forecasts.map((f, idx) => (
                  <span key={idx} className="w-[12%] text-center">{getMonthName(f.date)}</span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Foundational Events / System alerts panel */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 min-h-[350px] flex flex-col bg-card/40">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-6">Foundational Events</h3>
          
          <div className="flex-1 space-y-4">
            {isLoading ? (
              [1, 2, 3, 4].map((idx) => (
                <div key={idx} className="flex items-center justify-between py-2 border-b border-neutral-800/40 last:border-0">
                  <div className="flex items-center space-x-3 w-full">
                    <Skeleton className="w-7 h-7 rounded-full shrink-0" />
                    <div className="space-y-1.5 w-full">
                      <Skeleton className="h-3.5 w-2/3" />
                      <Skeleton className="h-2.5 w-1/3" />
                    </div>
                  </div>
                </div>
              ))
            ) : insights.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-muted-foreground text-xs">
                No recent corporate alerts active
              </div>
            ) : (
              <div className="space-y-4 overflow-y-auto max-h-[260px] pr-1">
                {insights.map((ins, idx) => {
                  const severity = ins.severity || 'INFO';
                  return (
                    <div key={idx} className="flex items-center justify-between py-2.5 border-b border-neutral-800/40 last:border-0">
                      <div className="flex items-center space-x-3 w-full">
                        <div className={`w-7 h-7 rounded-full shrink-0 flex items-center justify-center text-[10px] font-black ${
                          severity === 'ERROR' || severity === 'WARNING' 
                            ? 'bg-rose-500/10 border border-rose-500/20 text-rose-400' 
                            : 'bg-indigo-500/10 border border-indigo-500/20 text-indigo-400'
                        }`}>
                          {severity[0]}
                        </div>
                        <div className="space-y-0.5 w-full">
                          <p className="text-[11px] font-semibold text-neutral-200 line-clamp-2">{ins.message}</p>
                          <p className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">{severity} Alert</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

