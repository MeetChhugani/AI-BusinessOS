import React, { useState, useEffect } from 'react';
import { LeaveRequest, LeaveBalance, LeaveType } from '../../types/hcm';
import { useAuth } from '../../contexts/AuthContext';
import { AlertCircle, Check, X } from 'lucide-react';

export const LeavesPage: React.FC = () => {
  const { accessToken, user: currentUser } = useAuth();
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<LeaveType[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // New leave request form state
  const [newLeave, setNewLeave] = useState({
    leave_type_id: '',
    start_date: '',
    end_date: '',
    reason: '',
  });
  const [submitError, setSubmitError] = useState<string | null>(null);

  const fetchLeavesData = async () => {
    setIsLoading(true);
    try {
      const typesRes = await fetch('/api/v1/leaves/types', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const balRes = await fetch('/api/v1/leaves/balances', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const reqRes = await fetch('/api/v1/leaves/requests', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (typesRes.ok) setLeaveTypes(await typesRes.json());
      if (balRes.ok) setBalances(await balRes.json());
      if (reqRes.ok) setRequests(await reqRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchLeavesData();
    }
  }, [accessToken]);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    try {
      const res = await fetch('/api/v1/leaves/requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(newLeave),
      });
      const data = await res.json();
      if (res.ok) {
        setNewLeave({ leave_type_id: '', start_date: '', end_date: '', reason: '' });
        fetchLeavesData();
      } else {
        setSubmitError(data.error?.message || 'Failed to submit leave request');
      }
    } catch {
      setSubmitError('Failed to connect to system service');
    }
  };

  const handleApproval = async (reqId: string, approved: boolean) => {
    const res = await fetch(`/api/v1/leaves/requests/${reqId}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ approved, rejection_reason: approved ? undefined : 'Rejected by reviewer' }),
    });
    if (res.ok) {
      fetchLeavesData();
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Leaves & Time Off
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Submit vacation requests, view remaining balances, and check approval cycles.
        </p>
      </div>

      {isLoading ? (
        <div className="h-64 animate-pulse bg-neutral-800/40 rounded-2xl" />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Leaves balances */}
          <div className="lg:col-span-2 space-y-6">
            {/* Balances grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {balances.map(b => (
                <div key={b.id} className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-32">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                    {b.leave_type?.name}
                  </span>
                  <div>
                    <span className="text-2xl font-bold text-white block">
                      {b.entitled - b.used - b.pending} days
                    </span>
                    <span className="text-[9px] text-muted-foreground">
                      (Used: {b.used} / Entitled: {b.entitled})
                    </span>
                  </div>
                </div>
              ))}
              {balances.length === 0 && (
                <div className="col-span-3 text-center py-6 text-xs text-muted-foreground glass-card rounded-2xl border border-border">
                  No active leave balances mapped for this year.
                </div>
              )}
            </div>

            {/* Leave requests table */}
            <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider p-6 bg-secondary/40 border-b border-border">
                Leaves Request History
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-neutral-900 text-muted-foreground border-b border-border font-semibold">
                    <tr>
                      <th className="px-6 py-3">Employee</th>
                      <th className="px-6 py-3">Period</th>
                      <th className="px-6 py-3">Leave Type</th>
                      <th className="px-6 py-3">Reason</th>
                      <th className="px-6 py-3">Status</th>
                      {currentUser?.role !== 'EMPLOYEE' && <th className="px-6 py-3">Actions</th>}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40 text-white font-medium">
                    {requests.map(req => (
                      <tr key={req.id}>
                        <td className="px-6 py-4">
                          {req.employee?.first_name} {req.employee?.last_name}
                        </td>
                        <td className="px-6 py-4">{req.start_date} to {req.end_date}</td>
                        <td className="px-6 py-4">{req.leave_type?.name}</td>
                        <td className="px-6 py-4 text-muted-foreground">{req.reason || 'Not Specified'}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                            req.status === 'APPROVED' 
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                              : req.status.startsWith('PENDING')
                              ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                              : 'bg-red-500/10 text-red-400 border-red-500/20'
                          }`}>
                            {req.status.replace('_', ' ')}
                          </span>
                        </td>
                        {currentUser?.role !== 'EMPLOYEE' && (
                          <td className="px-6 py-4">
                            {req.status.startsWith('PENDING') && (
                              <div className="flex space-x-1.5">
                                <button
                                  onClick={() => handleApproval(req.id, true)}
                                  className="p-1 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 transition"
                                  title="Approve"
                                >
                                  <Check size={12} />
                                </button>
                                <button
                                  onClick={() => handleApproval(req.id, false)}
                                  className="p-1 rounded bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 transition"
                                  title="Reject"
                                >
                                  <X size={12} />
                                </button>
                              </div>
                            )}
                          </td>
                        )}
                      </tr>
                    ))}
                    {requests.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-6 py-10 text-center text-muted-foreground">
                          No leave requests found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Leave Application form */}
          <div className="glass-card rounded-2xl p-6 border border-neutral-800 h-fit space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Apply for Vacation</h3>
            
            {submitError && (
              <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center space-x-2 text-xs text-red-400">
                <AlertCircle size={14} className="shrink-0" />
                <span>{submitError}</span>
              </div>
            )}

            <form onSubmit={handleApply} className="space-y-4 text-xs">
              <div>
                <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-2">Leave Type</label>
                <select
                  required
                  className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                  value={newLeave.leave_type_id}
                  onChange={e => setNewLeave(prev => ({ ...prev, leave_type_id: e.target.value }))}
                >
                  <option value="">Select Type</option>
                  {leaveTypes.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-2">Start Date</label>
                <input 
                  required
                  type="date"
                  className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                  value={newLeave.start_date}
                  onChange={e => setNewLeave(prev => ({ ...prev, start_date: e.target.value }))}
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-2">End Date</label>
                <input 
                  required
                  type="date"
                  className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                  value={newLeave.end_date}
                  onChange={e => setNewLeave(prev => ({ ...prev, end_date: e.target.value }))}
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-2">Reason</label>
                <textarea
                  placeholder="Vacation details..."
                  className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none h-20"
                  value={newLeave.reason}
                  onChange={e => setNewLeave(prev => ({ ...prev, reason: e.target.value }))}
                />
              </div>

              <button type="submit" className="w-full py-3 bg-white text-black hover:bg-neutral-200 rounded-lg font-semibold transition">
                Submit Request
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
