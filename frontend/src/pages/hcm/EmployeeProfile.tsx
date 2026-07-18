import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Employee, SalaryHistory, Attendance, LeaveBalance, 
  LeaveRequest, PerformanceReview, EmployeeDocument, EmployeeNote, EmployeeTimeline 
} from '../../types/hcm';
import { 
  User, CreditCard, Calendar, BarChart2, FileText, 
  Clock, Download, Trash2, BookOpen, MessageSquare 
} from 'lucide-react';

export const EmployeeProfile: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { accessToken, user: currentUser } = useAuth();
  const navigate = useNavigate();
  
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);

  // Tab Data states
  const [salaries, setSalaries] = useState<SalaryHistory[]>([]);
  const [attendances, setAttendances] = useState<Attendance[]>([]);
  const [leaveBalances, setLeaveBalances] = useState<LeaveBalance[]>([]);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [reviews, setReviews] = useState<PerformanceReview[]>([]);
  const [documents, setDocuments] = useState<EmployeeDocument[]>([]);
  const [notes, setNotes] = useState<EmployeeNote[]>([]);
  const [timeline, setTimeline] = useState<EmployeeTimeline[]>([]);

  // Clock status for Attendance tab
  const [clockStatus, setClockStatus] = useState({ clocked_in: false, status: 'OUT' });

  // Input states for Adders
  const [newSalary, setNewSalary] = useState({ base_salary: '', bonus: '', allowance: '', deduction: '', reason: '' });
  const [newLeave, setNewLeave] = useState({ leave_type_id: '', start_date: '', end_date: '', reason: '' });
  const [newNote, setNewNote] = useState({ content: '', note_type: 'GENERAL' });
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('Resume');

  const fetchProfile = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/employees/${id}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setEmployee(await res.json());
      } else {
        navigate('/dashboard/hcm');
      }
    } catch {
      navigate('/dashboard/hcm');
    } finally {
      setIsLoading(false);
    }
  };

  const loadTabData = async () => {
    if (!id || !accessToken) return;
    try {
      if (activeTab === 'salary') {
        const res = await fetch(`/api/v1/employees/${id}/salary`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (res.ok) setSalaries(await res.json());
      }
      if (activeTab === 'attendance') {
        const logRes = await fetch(`/api/v1/attendance/logs?start_date=2026-01-01&end_date=2026-12-31`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        const statRes = await fetch(`/api/v1/attendance/status`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (logRes.ok) setAttendances(await logRes.json());
        if (statRes.ok) setClockStatus(await statRes.json());
      }
      if (activeTab === 'leaves') {
        const balRes = await fetch(`/api/v1/leaves/balances`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        const reqRes = await fetch(`/api/v1/leaves/requests`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (balRes.ok) setLeaveBalances(await balRes.json());
        if (reqRes.ok) setLeaveRequests(await reqRes.json());
      }
      if (activeTab === 'performance') {
        const res = await fetch(`/api/v1/performance?employee_id=${id}`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (res.ok) setReviews(await res.json());
      }
      if (activeTab === 'documents') {
        const res = await fetch(`/api/v1/documents/employee/${id}`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (res.ok) setDocuments(await res.json());
      }
      if (activeTab === 'notes') {
        const res = await fetch(`/api/v1/employees/${id}/notes`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (res.ok) setNotes(await res.json());
      }
      if (activeTab === 'timeline') {
        const res = await fetch(`/api/v1/employees/${id}/timeline`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (res.ok) setTimeline(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (id && accessToken) {
      fetchProfile();
    }
  }, [id, accessToken]);

  useEffect(() => {
    loadTabData();
  }, [activeTab]);

  const handleDeactivate = async () => {
    if (!employee) return;
    const method = employee.status === 'TERMINATED' ? 'POST' : 'DELETE';
    const endpoint = employee.status === 'TERMINATED' 
      ? `/api/v1/employees/${employee.id}/restore`
      : `/api/v1/employees/${employee.id}`;
      
    const res = await fetch(endpoint, {
      method,
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    if (res.ok) {
      fetchProfile();
    }
  };

  // Salary actions
  const handleAddSalary = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch(`/api/v1/employees/${id}/salary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({
        effective_date: new Date().toISOString().split('T')[0],
        base_salary: parseFloat(newSalary.base_salary),
        bonus: parseFloat(newSalary.bonus) || 0.0,
        allowance: parseFloat(newSalary.allowance) || 0.0,
        deduction: parseFloat(newSalary.deduction) || 0.0,
        reason: newSalary.reason
      })
    });
    if (res.ok) {
      setNewSalary({ base_salary: '', bonus: '', allowance: '', deduction: '', reason: '' });
      setActiveTab('salary');
      loadTabData();
    }
  };

  // Attendance Clocking Actions
  const handleClockIn = async () => {
    await fetch('/api/v1/attendance/clock-in', { method: 'POST', headers: { 'Authorization': `Bearer ${accessToken}` } });
    loadTabData();
  };
  const handleClockBreak = async () => {
    await fetch('/api/v1/attendance/break', { method: 'POST', headers: { 'Authorization': `Bearer ${accessToken}` } });
    loadTabData();
  };
  const handleClockResume = async () => {
    await fetch('/api/v1/attendance/resume', { method: 'POST', headers: { 'Authorization': `Bearer ${accessToken}` } });
    loadTabData();
  };
  const handleClockOut = async () => {
    await fetch('/api/v1/attendance/clock-out', { method: 'POST', headers: { 'Authorization': `Bearer ${accessToken}` } });
    loadTabData();
  };

  // Leave Actions
  const handleApplyLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/v1/leaves/requests', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(newLeave)
    });
    if (res.ok) {
      setNewLeave({ leave_type_id: '', start_date: '', end_date: '', reason: '' });
      loadTabData();
    }
  };

  // Notes Actions
  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch(`/api/v1/employees/${id}/notes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(newNote)
    });
    if (res.ok) {
      setNewNote({ content: '', note_type: 'GENERAL' });
      loadTabData();
    }
  };

  // Document Uploads
  const handleUploadDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('document_type', docType);

    const res = await fetch(`/api/v1/documents/${id}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${accessToken}` },
      body: formData
    });
    if (res.ok) {
      setUploadFile(null);
      loadTabData();
    }
  };

  const handleDeleteDoc = async (docId: string) => {
    const res = await fetch(`/api/v1/documents/${docId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    if (res.ok) {
      loadTabData();
    }
  };

  if (isLoading) {
    return <div className="h-64 animate-pulse bg-neutral-800/40 rounded-2xl" />;
  }

  if (!employee) return null;

  const tabs = [
    { id: 'overview', name: 'Overview', icon: User },
    { id: 'timeline', name: 'Timeline', icon: BookOpen },
    { id: 'salary', name: 'Compensation', icon: CreditCard },
    { id: 'attendance', name: 'Attendance', icon: Clock },
    { id: 'leaves', name: 'Leaves', icon: Calendar },
    { id: 'performance', name: 'Performance', icon: BarChart2 },
    { id: 'documents', name: 'Documents', icon: FileText },
    { id: 'notes', name: 'Private Notes', icon: MessageSquare, role: ['SUPER_ADMIN', 'ADMIN', 'HR', 'MANAGER'] }
  ].filter(t => !t.role || t.role.includes(currentUser?.role || ''));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
      {/* Profile summary card sidebar */}
      <div className="lg:col-span-1 space-y-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 text-center flex flex-col items-center">
          <div className="w-20 h-20 rounded-full bg-secondary border-2 border-border mb-4 flex items-center justify-center font-display text-white text-3xl font-bold shadow-inner">
            {employee.first_name[0]}{employee.last_name[0]}
          </div>

          <h2 className="text-lg font-bold text-white leading-tight">
            {employee.first_name} {employee.last_name}
          </h2>
          <span className="text-xs text-muted-foreground font-mono block mt-1">{employee.employee_id || 'Draft'}</span>
          
          <div className="mt-4 space-y-1.5 w-full text-xs border-t border-b border-border/40 py-4 my-4">
            <div className="flex justify-between"><span className="text-muted-foreground">Dept:</span><span className="text-white font-medium">{employee.department?.name || 'Unassigned'}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Title:</span><span className="text-white font-medium">{employee.designation?.name || 'Unassigned'}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Type:</span><span className="text-white font-medium capitalize">{employee.employment_type.toLowerCase()}</span></div>
          </div>

          <span className={`w-full text-center px-3 py-1.5 rounded-lg text-xs font-bold border mb-4 uppercase ${
            employee.status === 'ACTIVE' 
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
          }`}>
            Status: {employee.status}
          </span>

          <span className="text-[10px] font-bold px-2 py-1 rounded bg-neutral-900 border border-neutral-850 text-neutral-400 uppercase tracking-wider mb-6 block w-fit">
            Stage: {employee.onboarding_status.replace('_', ' ')}
          </span>

          {currentUser?.role !== 'EMPLOYEE' && (
            <button
              onClick={handleDeactivate}
              className={`w-full py-2 rounded-lg text-xs font-semibold border transition ${
                employee.status === 'TERMINATED'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'
                  : 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20'
              }`}
            >
              {employee.status === 'TERMINATED' ? 'Restore Profile' : 'Terminate Employee'}
            </button>
          )}
        </div>
      </div>

      {/* Tabs panels container */}
      <div className="lg:col-span-3 space-y-6">
        {/* Navigation tabs */}
        <div className="flex items-center space-x-1 overflow-x-auto border-b border-border pb-px text-sm">
          {tabs.map(t => {
            const Icon = t.icon;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium transition whitespace-nowrap ${
                  activeTab === t.id
                    ? 'border-blue-500 text-white'
                    : 'border-transparent text-muted-foreground hover:text-white'
                }`}
              >
                <Icon size={16} />
                <span>{t.name}</span>
              </button>
            );
          })}
        </div>

        {/* Tab content bodies */}
        <div className="min-h-[400px]">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in duration-200">
              {/* Card 1: Basic Info */}
              <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Personal Info</h3>
                <div className="space-y-3 text-xs">
                  <div><span className="text-muted-foreground block mb-0.5">Email Address</span><span className="text-white font-medium">{employee.email}</span></div>
                  <div><span className="text-muted-foreground block mb-0.5">Phone Number</span><span className="text-white font-medium">{employee.phone || 'Not Specified'}</span></div>
                  <div><span className="text-muted-foreground block mb-0.5">Location</span><span className="text-white font-medium">{employee.location || 'Remote'}</span></div>
                  <div><span className="text-muted-foreground block mb-0.5">Joining Date</span><span className="text-white font-medium">{employee.joining_date || 'Pending'}</span></div>
                </div>
              </div>

              {/* Card 2: Emergency Contact */}
              <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Emergency Contacts</h3>
                <div className="space-y-3 text-xs">
                  <div><span className="text-muted-foreground block mb-0.5">Contact Person</span><span className="text-white font-medium">{employee.emergency_contact_name || 'None'}</span></div>
                  <div><span className="text-muted-foreground block mb-0.5">Relationship</span><span className="text-white font-medium">{employee.emergency_contact_relation || 'None'}</span></div>
                  <div><span className="text-muted-foreground block mb-0.5">Phone Number</span><span className="text-white font-medium">{employee.emergency_contact_phone || 'None'}</span></div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'timeline' && (
            <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-6">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Timeline Events</h3>
              {timeline.length === 0 ? (
                <p className="text-xs text-muted-foreground">No events recorded on profile timeline.</p>
              ) : (
                <div className="relative border-l border-neutral-800 pl-4 space-y-6 ml-2">
                  {timeline.map(e => (
                    <div key={e.id} className="relative">
                      <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-blue-500 border-2 border-card" />
                      <span className="text-[10px] text-muted-foreground block">{new Date(e.event_date).toLocaleDateString()}</span>
                      <h4 className="text-xs font-bold text-white mt-0.5">{e.title}</h4>
                      <p className="text-xs text-muted-foreground mt-1">{e.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'salary' && (
            <div className="space-y-6">
              {currentUser && ['SUPER_ADMIN', 'ADMIN', 'HR'].includes(currentUser.role) && (
                <div className="glass-card rounded-2xl p-6 border border-neutral-800">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Adjust Salary details</h3>
                  <form onSubmit={handleAddSalary} className="grid grid-cols-2 sm:grid-cols-4 gap-4 items-end">
                    <div>
                      <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-1.5">Base Salary</label>
                      <input 
                        required
                        type="number"
                        className="w-full px-3 py-2 bg-secondary text-white rounded border border-border text-xs"
                        value={newSalary.base_salary}
                        onChange={e => setNewSalary(prev => ({ ...prev, base_salary: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-1.5">Bonus</label>
                      <input 
                        type="number"
                        className="w-full px-3 py-2 bg-secondary text-white rounded border border-border text-xs"
                        value={newSalary.bonus}
                        onChange={e => setNewSalary(prev => ({ ...prev, bonus: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-1.5">Reason</label>
                      <input 
                        className="w-full px-3 py-2 bg-secondary text-white rounded border border-border text-xs"
                        value={newSalary.reason}
                        onChange={e => setNewSalary(prev => ({ ...prev, reason: e.target.value }))}
                      />
                    </div>
                    <button 
                      type="submit" 
                      className="py-2.5 bg-white text-black hover:bg-neutral-200 rounded font-semibold text-xs transition"
                    >
                      Log Increment
                    </button>
                  </form>
                </div>
              )}

              <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
                <table className="w-full text-left text-xs">
                  <thead className="bg-secondary/40 text-muted-foreground border-b border-border">
                    <tr>
                      <th className="px-6 py-4">Effective Date</th>
                      <th className="px-6 py-4">Base Salary</th>
                      <th className="px-6 py-4">Bonus</th>
                      <th className="px-6 py-4">Allowance</th>
                      <th className="px-6 py-4">Reason</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40 text-white font-medium">
                    {salaries.map(s => (
                      <tr key={s.id}>
                        <td className="px-6 py-4">{s.effective_date}</td>
                        <td className="px-6 py-4">${s.base_salary.toLocaleString()}</td>
                        <td className="px-6 py-4">${s.bonus.toLocaleString()}</td>
                        <td className="px-6 py-4">${s.allowance.toLocaleString()}</td>
                        <td className="px-6 py-4 text-muted-foreground">{s.reason || 'Annual Adjustments'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'attendance' && (
            <div className="space-y-6">
              {/* Daily Session Clock Controller */}
              <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Clock Controller</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    Status: <span className="font-semibold text-white">{clockStatus.status}</span>
                  </p>
                </div>
                
                <div className="flex space-x-3">
                  {!clockStatus.clocked_in ? (
                    <button onClick={handleClockIn} className="px-4 py-2 bg-emerald-500 text-white hover:bg-emerald-600 rounded text-xs font-semibold">Clock In</button>
                  ) : (
                    <>
                      {clockStatus.status === 'IN' ? (
                        <button onClick={handleClockBreak} className="px-4 py-2 bg-yellow-500 text-white hover:bg-yellow-600 rounded text-xs font-semibold">Take Break</button>
                      ) : (
                        <button onClick={handleClockResume} className="px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded text-xs font-semibold">Resume Work</button>
                      )}
                      <button onClick={handleClockOut} className="px-4 py-2 bg-red-500 text-white hover:bg-red-600 rounded text-xs font-semibold">Clock Out</button>
                    </>
                  )}
                </div>
              </div>

              {/* Attendance Log Table */}
              <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
                <table className="w-full text-left text-xs">
                  <thead className="bg-secondary/40 text-muted-foreground border-b border-border">
                    <tr>
                      <th className="px-6 py-4">Date</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4">Total Working Hours</th>
                      <th className="px-6 py-4">Overtime Minutes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40 text-white">
                    {attendances.map(a => (
                      <tr key={a.id}>
                        <td className="px-6 py-4 font-semibold">{a.date}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                            a.status === 'PRESENT' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                          }`}>{a.status}</span>
                        </td>
                        <td className="px-6 py-4 font-mono">{a.total_working_hours} hrs</td>
                        <td className="px-6 py-4 font-mono">{a.overtime_minutes} mins</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'leaves' && (
            <div className="space-y-6">
              {/* Apply Leave form */}
              <div className="glass-card rounded-2xl p-6 border border-neutral-800">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Request Leave Vacation</h3>
                <form onSubmit={handleApplyLeave} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
                  <div>
                    <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-1.5">Leave Type</label>
                    <select
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border text-xs"
                      value={newLeave.leave_type_id}
                      onChange={e => setNewLeave(prev => ({ ...prev, leave_type_id: e.target.value }))}
                    >
                      <option value="">Select Type</option>
                      {leaveBalances.map(b => (
                        <option key={b.id} value={b.leave_type_id}>
                          {b.leave_type?.name} (Bal: {b.entitled - b.used - b.pending})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-1.5">Start Date</label>
                    <input 
                      required
                      type="date"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border text-xs"
                      value={newLeave.start_date}
                      onChange={e => setNewLeave(prev => ({ ...prev, start_date: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-1.5">End Date</label>
                    <input 
                      required
                      type="date"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border text-xs"
                      value={newLeave.end_date}
                      onChange={e => setNewLeave(prev => ({ ...prev, end_date: e.target.value }))}
                    />
                  </div>
                  <button type="submit" className="py-2.5 bg-white text-black hover:bg-neutral-200 rounded font-semibold text-xs transition">Apply Request</button>
                </form>
              </div>

              {/* History Leave Requests */}
              <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
                <table className="w-full text-left text-xs">
                  <thead className="bg-secondary/40 text-muted-foreground border-b border-border">
                    <tr>
                      <th className="px-6 py-4">Period</th>
                      <th className="px-6 py-4">Leave Type</th>
                      <th className="px-6 py-4">Reason</th>
                      <th className="px-6 py-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40 text-white font-medium">
                    {leaveRequests.map(r => (
                      <tr key={r.id}>
                        <td className="px-6 py-4">{r.start_date} to {r.end_date}</td>
                        <td className="px-6 py-4">{r.leave_type?.name}</td>
                        <td className="px-6 py-4 text-muted-foreground">{r.reason || 'None'}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            r.status === 'APPROVED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                          }`}>{r.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div className="space-y-6">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Performance Reviews Cycle</h3>
              {reviews.map(r => (
                <div key={r.id} className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
                  <div className="flex items-center justify-between border-b border-border/40 pb-3">
                    <div>
                      <h4 className="text-sm font-bold text-white">{r.review_cycle}</h4>
                      <span className="text-[10px] text-muted-foreground">Rating: {r.rating} / 5</span>
                    </div>
                    {r.promotion_recommendation && (
                      <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[9px] font-bold uppercase tracking-wider">Recommended for Promotion</span>
                    )}
                  </div>
                  <div className="text-xs space-y-2">
                    <p><span className="text-muted-foreground block mb-0.5">Achievements:</span> {r.achievements || 'Not Filled'}</p>
                    <p><span className="text-muted-foreground block mb-0.5">Goals:</span> {r.goals || 'Not Filled'}</p>
                    <p><span className="text-muted-foreground block mb-0.5">Manager Feedback:</span> {r.manager_feedback || 'Not Filled'}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="space-y-6">
              {/* Document upload form */}
              <div className="glass-card rounded-2xl p-6 border border-neutral-800">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Upload Document Asset</h3>
                <form onSubmit={handleUploadDoc} className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
                  <div>
                    <label className="block text-[10px] font-semibold text-muted-foreground uppercase mb-1.5">Document Type</label>
                    <select
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border text-xs"
                      value={docType}
                      onChange={e => setDocType(e.target.value)}
                    >
                      <option value="Resume">Resume</option>
                      <option value="Offer Letter">Offer Letter</option>
                      <option value="Contract">Contracts</option>
                      <option value="Certificate">Certificate</option>
                    </select>
                  </div>
                  <div>
                    <input 
                      required
                      type="file" 
                      className="w-full text-xs text-white file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-secondary file:text-white hover:file:bg-neutral-800"
                      onChange={e => setUploadFile(e.target.files?.[0] || null)}
                    />
                  </div>
                  <button type="submit" className="py-2.5 bg-white text-black hover:bg-neutral-200 rounded font-semibold text-xs transition">Upload file</button>
                </form>
              </div>

              {/* Document Listing */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {documents.map(d => (
                  <div key={d.id} className="glass-card rounded-xl p-4 border border-neutral-800 flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-white truncate max-w-[200px]">{d.name}</h4>
                      <span className="text-[10px] text-muted-foreground">{d.document_type} (v{d.version})</span>
                    </div>
                    <div className="flex space-x-2">
                      <a 
                        href={`/api/v1/documents/${d.id}/download`} 
                        download
                        className="p-1.5 bg-secondary hover:bg-neutral-850 rounded text-muted-foreground hover:text-white transition"
                        title="Download"
                      >
                        <Download size={14} />
                      </a>
                      <button 
                        onClick={() => handleDeleteDoc(d.id)}
                        className="p-1.5 bg-red-500/10 hover:bg-red-500/20 rounded text-red-400 border border-red-500/20 transition"
                        title="Delete"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="space-y-6">
              {/* Create note card form */}
              <div className="glass-card rounded-2xl p-6 border border-neutral-800">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Add Profile Note</h3>
                <form onSubmit={handleAddNote} className="space-y-4">
                  <textarea
                    required
                    placeholder="Write a private note regarding employee status details..."
                    className="w-full px-4 py-3 bg-secondary text-white border border-border rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-ring h-24"
                    value={newNote.content}
                    onChange={e => setNewNote(prev => ({ ...prev, content: e.target.value }))}
                  />
                  <div className="flex justify-between items-center">
                    <select
                      className="px-3 py-2 bg-secondary text-white rounded border border-border text-xs"
                      value={newNote.note_type}
                      onChange={e => setNewNote(prev => ({ ...prev, note_type: e.target.value }))}
                    >
                      <option value="GENERAL">General Note</option>
                      <option value="MANAGER">Manager Note</option>
                      {currentUser && ['SUPER_ADMIN', 'ADMIN', 'HR'].includes(currentUser.role) && (
                        <option value="PRIVATE_HR">Private HR Note</option>
                      )}
                    </select>
                    <button type="submit" className="px-4 py-2 bg-white text-black hover:bg-neutral-200 rounded text-xs font-semibold transition">Save Note</button>
                  </div>
                </form>
              </div>

              {/* Notes chronological log list */}
              <div className="space-y-4">
                {notes.map(n => (
                  <div key={n.id} className="glass-card rounded-xl p-4 border border-neutral-850 text-xs">
                    <div className="flex items-center justify-between border-b border-border/20 pb-2 mb-2">
                      <span className="text-[10px] text-muted-foreground">Logged on {new Date(n.created_at).toLocaleString()}</span>
                      <span className="px-1.5 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-neutral-400 text-[9px] font-bold uppercase tracking-wider">{n.note_type}</span>
                    </div>
                    <p className="text-neutral-300 leading-relaxed">{n.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
