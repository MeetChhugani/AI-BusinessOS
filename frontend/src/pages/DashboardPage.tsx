import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { TrendingUp, Users, Package, ShoppingCart, BarChart2 } from 'lucide-react';

const Skeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={`animate-pulse bg-neutral-800/60 light:bg-neutral-200 rounded-lg ${className}`} />
);

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  const metrics = [
    { title: 'Gross Revenue', icon: TrendingUp, color: 'text-emerald-400 bg-emerald-500/10' },
    { title: 'Active Employees', icon: Users, color: 'text-blue-400 bg-blue-500/10' },
    { title: 'Stock & Inventory', icon: Package, color: 'text-indigo-400 bg-indigo-500/10' },
    { title: 'Closed Sales', icon: ShoppingCart, color: 'text-purple-400 bg-purple-500/10' },
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
            
            {/* Skeletal loaders */}
            <div className="space-y-3">
              <Skeleton className="h-7 w-2/3" />
              <Skeleton className="h-3 w-1/2" />
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
            <Skeleton className="h-6 w-20" />
          </div>

          <div className="flex-1 flex flex-col justify-between space-y-4">
            {/* Pulsing bars mimicking chart */}
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
            <div className="flex justify-between px-2">
              <Skeleton className="h-2 w-8" />
              <Skeleton className="h-2 w-8" />
              <Skeleton className="h-2 w-8" />
              <Skeleton className="h-2 w-8" />
              <Skeleton className="h-2 w-8" />
            </div>
          </div>
        </div>

        {/* Audit Log / Session list Skeleton Panel */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 min-h-[350px] flex flex-col">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-6">Foundational Events</h3>
          
          <div className="flex-1 space-y-4">
            {[1, 2, 3, 4].map((idx) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b border-neutral-800/40 last:border-0">
                <div className="flex items-center space-x-3 w-full">
                  <Skeleton className="w-7 h-7 rounded-full shrink-0" />
                  <div className="space-y-1.5 w-full">
                    <Skeleton className="h-3.5 w-2/3" />
                    <Skeleton className="h-2.5 w-1/3" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
