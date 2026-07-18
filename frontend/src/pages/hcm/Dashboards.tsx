import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Employee, LeaveRequest } from '../../types/hcm';
import { Link } from 'react-router-dom';
import { 
  Users, Calendar, TrendingUp, ArrowUpRight, Smile 
} from 'lucide-react';

export const HCMDashboard: React.FC = () => {
  const { user: currentUser, accessToken } = useAuth();
  
  // Dashboard state aggregates
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [pendingLeaves, setPendingLeaves] = useState<LeaveRequest[]>([]);
  const [clockStatus, setClockStatus] = useState({ clocked_in: false, status: 'OUT' });
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const empRes = await fetch('/api/v1/employees?limit=100', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const leaveRes = await fetch('/api/v1/leaves/requests?status=PENDING_MANAGER', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const clockRes = await fetch('/api/v1/attendance/status', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      if (empRes.ok) setEmployees(await empRes.ok ? await empRes.json() : []);
      if (leaveRes.ok) setPendingLeaves(await leaveRes.ok ? await leaveRes.json() : []);
      if (clockRes.ok) setClockStatus(await clockRes.json());
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

  const handleClockToggle = async () => {
    const endpoint = clockStatus.clocked_in ? '/api/v1/attendance/clock-out' : '/api/v1/attendance/clock-in';
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    if (res.ok) {
      fetchDashboardData();
    }
  };

  if (isLoading) {
    return <div className="h-64 animate-pulse bg-neutral-800/40 rounded-2xl" />;
  }

  // --- 1. HR / ADMIN DASHBOARD VIEW ---
  if (currentUser?.role === 'SUPER_ADMIN' || currentUser?.role === 'ADMIN' || currentUser?.role === 'HR') {
    const totalCount = employees.length;
    const onboardCount = employees.filter(e => e.onboarding_status !== 'ONBOARDING_COMPLETE').length;
    const activeCount = employees.filter(e => e.status === 'ACTIVE').length;

    return (
      <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in duration-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">HR Core Hub</h1>
          <p className="text-sm text-muted-foreground mt-1.5">Overview of employee statuses, recruiting onboardings, and organization metrics.</p>
        </div>

        {/* Aggregates Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Total Headcount</span>
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20 text-blue-400">
                <Users size={16} />
              </div>
            </div>
            <div>
              <span className="text-3xl font-bold text-white block">{totalCount}</span>
              <span className="text-[10px] text-muted-foreground">Active profiles logged</span>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Onboarding Pipeline</span>
              <div className="w-8 h-8 rounded-lg bg-yellow-500/10 flex items-center justify-center border border-yellow-500/20 text-yellow-400">
                <Smile size={16} />
              </div>
            </div>
            <div>
              <span className="text-3xl font-bold text-white block">{onboardCount}</span>
              <span className="text-[10px] text-muted-foreground">Candidates in progress</span>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Active Staff</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 text-emerald-400">
                <TrendingUp size={16} />
              </div>
            </div>
            <div>
              <span className="text-3xl font-bold text-white block">{activeCount}</span>
              <span className="text-[10px] text-muted-foreground">Excluding deactivations</span>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Pending Approvals</span>
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400">
                <Calendar size={16} />
              </div>
            </div>
            <div>
              <span className="text-3xl font-bold text-white block">{pendingLeaves.length}</span>
              <span className="text-[10px] text-muted-foreground">Leaves pending HR check</span>
            </div>
          </div>
        </div>

        {/* Charts & Details */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Department Distributions */}
          <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-neutral-800 space-y-6">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Department Distribution</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1.5"><span className="text-neutral-300">Engineering</span><span className="text-white font-semibold">60%</span></div>
                <div className="w-full bg-secondary h-2 rounded-full overflow-hidden"><div className="bg-blue-500 h-full" style={{ width: '60%' }} /></div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1.5"><span className="text-neutral-300">Human Resources</span><span className="text-white font-semibold">20%</span></div>
                <div className="w-full bg-secondary h-2 rounded-full overflow-hidden"><div className="bg-purple-500 h-full" style={{ width: '20%' }} /></div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1.5"><span className="text-neutral-300">Sales</span><span className="text-white font-semibold">20%</span></div>
                <div className="w-full bg-secondary h-2 rounded-full overflow-hidden"><div className="bg-yellow-500 h-full" style={{ width: '20%' }} /></div>
              </div>
            </div>
          </div>

          {/* Quick Shortcuts */}
          <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4 flex flex-col justify-between">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">HR Direct Access</h3>
            <div className="space-y-3">
              <Link to="/dashboard/hcm/org" className="w-full flex items-center justify-between p-3 bg-secondary/60 hover:bg-secondary rounded-xl text-xs text-white border border-border/40 transition">
                <span>Interactive Org Chart</span>
                <ArrowUpRight size={14} className="text-muted-foreground" />
              </Link>
              <Link to="/dashboard/hcm/pipeline" className="w-full flex items-center justify-between p-3 bg-secondary/60 hover:bg-secondary rounded-xl text-xs text-white border border-border/40 transition">
                <span>Onboarding Pipeline Board</span>
                <ArrowUpRight size={14} className="text-muted-foreground" />
              </Link>
              <Link to="/dashboard/hcm" className="w-full flex items-center justify-between p-3 bg-secondary/60 hover:bg-secondary rounded-xl text-xs text-white border border-border/40 transition">
                <span>Manage Employees Directory</span>
                <ArrowUpRight size={14} className="text-muted-foreground" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --- 2. MANAGER DASHBOARD VIEW ---
  if (currentUser?.role === 'MANAGER') {
    return (
      <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in duration-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">Team Overview</h1>
          <p className="text-sm text-muted-foreground mt-1.5">Manage direct reports, approve team leaves, and assess performances.</p>
        </div>

        {/* Manager widgets list */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Direct reports list */}
          <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">My Direct Reports</h3>
            {employees.length === 0 ? (
              <p className="text-xs text-muted-foreground">No reports currently assigned.</p>
            ) : (
              <div className="space-y-3">
                {employees.slice(0, 4).map(e => (
                  <div key={e.id} className="flex items-center justify-between p-3 bg-secondary/40 border border-border/40 rounded-xl">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-full bg-secondary border border-border flex items-center justify-center font-display text-white text-xs">
                        {e.first_name[0]}{e.last_name[0]}
                      </div>
                      <div>
                        <span className="font-semibold text-white block text-xs">{e.first_name} {e.last_name}</span>
                        <span className="text-[10px] text-muted-foreground font-mono">{e.employee_id || 'DRAFT'}</span>
                      </div>
                    </div>
                    <Link to={`/dashboard/hcm/profile/${e.id}`} className="text-xs text-blue-400 hover:underline">Manage Profile</Link>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Pending Direct Reports leaves list */}
          <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Pending Leaves approvals</h3>
              {pendingLeaves.length === 0 ? (
                <p className="text-xs text-muted-foreground">No pending leaves to approve.</p>
              ) : (
                <div className="space-y-3">
                  {pendingLeaves.map(r => (
                    <div key={r.id} className="text-xs border-b border-border/40 pb-2.5 last:border-0 last:pb-0">
                      <p className="text-white font-semibold">{r.employee?.first_name} {r.employee?.last_name}</p>
                      <p className="text-muted-foreground text-[10px] mt-0.5">{r.start_date} to {r.end_date}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <Link to="/dashboard/hcm/leaves" className="w-full text-center py-2.5 bg-secondary hover:bg-neutral-800 text-white border border-border/40 rounded-xl text-xs transition mt-6 block">
              Manage Leaves Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // --- 3. EMPLOYEE DASHBOARD VIEW ---
  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in duration-200">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">Employee Portal</h1>
        <p className="text-sm text-muted-foreground mt-1.5">Track your workday attendance, request leave days, and submit documents.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Clock session widget */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between min-h-[220px]">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Attendance Clock</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Workday Status: <span className="font-semibold text-white">{clockStatus.status}</span>
            </p>
          </div>
          
          <button
            onClick={handleClockToggle}
            className={`w-full py-3 rounded-lg text-sm font-semibold transition ${
              clockStatus.clocked_in 
                ? 'bg-red-500 text-white hover:bg-red-650' 
                : 'bg-emerald-500 text-white hover:bg-emerald-660'
            }`}
          >
            {clockStatus.clocked_in ? 'Clock Out Workday' : 'Clock In Workday'}
          </button>
        </div>

        {/* Shortcuts cards */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between min-h-[220px]">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Quick Tasks</h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Use the employee profile options to apply for leaves, upload certs/contracts, or view your appraisal review cycles.
            </p>
          </div>

          <Link
            to={`/dashboard/hcm/profile/${currentUser?.id}`}
            className="w-full text-center py-3 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition block"
          >
            Access My Profile Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};
