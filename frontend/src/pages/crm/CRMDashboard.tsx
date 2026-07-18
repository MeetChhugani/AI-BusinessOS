import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Briefcase, Target, TrendingUp, Users, Calendar, 
  ArrowUpRight, Award 
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const CRMDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [pipelineVal, setPipelineVal] = useState<number>(0);
  const [activeLeads, setActiveLeads] = useState<number>(0);
  const [meetings, setMeetings] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCRMData = async () => {
    setIsLoading(true);
    try {
      const oppRes = await fetch('/api/v1/opportunities', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const leadRes = await fetch('/api/v1/leads', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const meetRes = await fetch('/api/v1/tasks/meetings', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (oppRes.ok) {
        const opps = await oppRes.json();
        const sum = opps.reduce((acc: number, curr: any) => acc + parseFloat(curr.expected_revenue), 0);
        setPipelineVal(sum);
      }
      if (leadRes.ok) {
        const leads = await leadRes.json();
        setActiveLeads(leads.filter((l: any) => l.status !== 'CONVERTED').length);
      }
      if (meetRes.ok) {
        setMeetings(await meetRes.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchCRMData();
    }
  }, [accessToken]);

  if (isLoading) {
    return <div className="h-64 animate-pulse bg-neutral-800/40 rounded-2xl" />;
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Sales Command Center
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Forecast monthly sales, monitor customer conversions, and plan follow-up tasks.
        </p>
      </div>

      {/* Stats indicators grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Pipeline Value</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400">
              <Briefcase size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">${pipelineVal.toLocaleString()}</span>
            <span className="text-[10px] text-muted-foreground">Adjusted by conversion probability</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Active Leads</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 text-emerald-400">
              <Users size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">{activeLeads}</span>
            <span className="text-[10px] text-muted-foreground">Leads in qualification stage</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Average Deal Size</span>
            <div className="w-8 h-8 rounded-lg bg-yellow-500/10 flex items-center justify-center border border-yellow-500/20 text-yellow-400">
              <TrendingUp size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">$4,500</span>
            <span className="text-[10px] text-muted-foreground">Target deal margin baseline</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Win Rate</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400">
              <Award size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">42%</span>
            <span className="text-[10px] text-muted-foreground">Proposal won percentage ratio</span>
          </div>
        </div>
      </div>

      {/* Core split layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sales funnel details */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-neutral-800 space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Target size={16} className="text-muted-foreground" />
            Conversion Funnel
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center text-xs">
              <span className="text-white font-semibold">1. Leads Capture</span>
              <span className="text-muted-foreground">100% (Baseline)</span>
            </div>
            <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 w-full" />
            </div>

            <div className="flex justify-between items-center text-xs pt-2">
              <span className="text-white font-semibold">2. Qualified Opportunities</span>
              <span className="text-muted-foreground">65% Conversion</span>
            </div>
            <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 w-[65%]" />
            </div>

            <div className="flex justify-between items-center text-xs pt-2">
              <span className="text-white font-semibold">3. Quotations Submitted</span>
              <span className="text-muted-foreground">40% Conversion</span>
            </div>
            <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
              <div className="h-full bg-purple-500 w-[40%]" />
            </div>

            <div className="flex justify-between items-center text-xs pt-2">
              <span className="text-white font-semibold">4. Deals Won (Sales Orders)</span>
              <span className="text-muted-foreground">18% Conversion</span>
            </div>
            <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 w-[18%]" />
            </div>
          </div>
        </div>

        {/* Calendar / Meetings */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between">
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Calendar size={16} className="text-purple-500" />
              Upcoming Meetings
            </h3>
            {meetings.length === 0 ? (
              <p className="text-xs text-muted-foreground">No meetings scheduled for this week.</p>
            ) : (
              <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
                {meetings.map((meet, idx) => (
                  <div key={idx} className="flex justify-between items-center text-xs border-b border-border/40 pb-2.5 last:border-0">
                    <div>
                      <span className="text-white font-semibold block">{meet.title}</span>
                      <span className="text-[9px] text-muted-foreground font-mono">
                        {meet.start_time.slice(11, 16)} | Loc: {meet.location || 'Online'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <Link to="/dashboard/crm/tasks" className="w-full text-center py-2.5 bg-secondary hover:bg-neutral-850 text-white border border-border/40 rounded-xl text-xs transition mt-6 block">
            View Task Calendar →
          </Link>
        </div>
      </div>

      {/* Shortcuts grid */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-6">
        <Link to="/dashboard/crm/directory" className="glass-card rounded-2xl p-6 border border-neutral-800 flex justify-between items-center hover:border-neutral-750 transition text-xs">
          <div>
            <span className="font-semibold text-white block">Customers</span>
            <span className="text-muted-foreground block mt-1">Directory list & segments</span>
          </div>
          <ArrowUpRight size={16} className="text-muted-foreground" />
        </Link>
        <Link to="/dashboard/crm/leads" className="glass-card rounded-2xl p-6 border border-neutral-800 flex justify-between items-center hover:border-neutral-750 transition text-xs">
          <div>
            <span className="font-semibold text-white block">Lead Qualifier</span>
            <span className="text-muted-foreground block mt-1">Automatic lead scoring profiles</span>
          </div>
          <ArrowUpRight size={16} className="text-muted-foreground" />
        </Link>
        <Link to="/dashboard/crm/opportunities" className="glass-card rounded-2xl p-6 border border-neutral-800 flex justify-between items-center hover:border-neutral-750 transition text-xs">
          <div>
            <span className="font-semibold text-white block">Deals Board</span>
            <span className="text-muted-foreground block mt-1">Opportunity pipeline Kanban</span>
          </div>
          <ArrowUpRight size={16} className="text-muted-foreground" />
        </Link>
        <Link to="/dashboard/crm/quotations" className="glass-card rounded-2xl p-6 border border-neutral-800 flex justify-between items-center hover:border-neutral-750 transition text-xs">
          <div>
            <span className="font-semibold text-white block">Quotations & Orders</span>
            <span className="text-muted-foreground block mt-1">Approve SO & reserve inventory</span>
          </div>
          <ArrowUpRight size={16} className="text-muted-foreground" />
        </Link>
      </div>
    </div>
  );
};
