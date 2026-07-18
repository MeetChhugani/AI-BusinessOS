import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Employee, Department, Designation } from '../../types/hcm';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Search, Plus, Download, Upload, Trash2, LayoutGrid, List 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const EmployeeDirectory: React.FC = () => {
  const { accessToken } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Search & Filter state
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  
  // Pagination & Sort
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');

  // Bulk selections
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  // Open creation drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    first_name: '', last_name: '', email: '', phone: '',
    status: 'PROBATION', employment_type: 'FULL_TIME',
    location: '', department_id: '', designation_id: '',
  });

  const fetchFilters = async () => {
    try {
      const dRes = await fetch('/api/v1/departments', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const dsRes = await fetch('/api/v1/designations', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (dRes.ok) setDepartments(await dRes.json());
      if (dsRes.ok) setDesignations(await dsRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchEmployees = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        skip: '0',
        limit: '50',
      });
      if (search) params.append('search', search);
      if (deptFilter) params.append('department_id', deptFilter);
      if (statusFilter) params.append('status', statusFilter);
      if (typeFilter) params.append('employment_type', typeFilter);

      const res = await fetch(`/api/v1/employees?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setEmployees(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchFilters();
    }
  }, [accessToken]);

  useEffect(() => {
    if (accessToken) {
      fetchEmployees();
    }
  }, [accessToken, search, deptFilter, statusFilter, typeFilter]);

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(employees.map(e => e.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedIds(prev => [...prev, id]);
    } else {
      setSelectedIds(prev => prev.filter(item => item !== id));
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/employees', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(createForm)
      });
      if (res.ok) {
        setDrawerOpen(false);
        setCreateForm({
          first_name: '', last_name: '', email: '', phone: '',
          status: 'PROBATION', employment_type: 'FULL_TIME',
          location: '', department_id: '', designation_id: '',
        });
        fetchEmployees();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleBulkDeactivate = async () => {
    for (const id of selectedIds) {
      try {
        await fetch(`/api/v1/employees/${id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${accessToken}` }
        });
      } catch (e) {
        console.error(e);
      }
    }
    setSelectedIds([]);
    fetchEmployees();
  };

  // Client-side CSV exporter helper
  const handleExportCSV = () => {
    const activeList = selectedIds.length > 0 
      ? employees.filter(e => selectedIds.includes(e.id))
      : employees;
      
    const headers = ['ID', 'First Name', 'Last Name', 'Email', 'Status', 'Type', 'Department', 'Designation'];
    const rows = activeList.map(e => [
      e.employee_id || '',
      e.first_name,
      e.last_name,
      e.email,
      e.status,
      e.employment_type,
      e.department?.name || '',
      e.designation?.name || ''
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "employees_directory.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Employee Directory
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Manage your global workforce lifecycle from onboarding to active directory.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/dashboard/hcm/import"
            className="inline-flex items-center justify-center px-4 py-2.5 bg-secondary text-white rounded-lg border border-border text-xs font-semibold hover:bg-neutral-800 transition"
          >
            <Upload size={14} className="mr-2" />
            Import CSV
          </Link>
          
          <button
            onClick={() => setDrawerOpen(true)}
            className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
          >
            <Plus size={14} className="mr-2" />
            Add Employee
          </button>
        </div>
      </div>

      {/* Search and Filters panel */}
      <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative col-span-2">
            <input
              placeholder="Search by name, email, employee ID..."
              className="w-full pl-10 pr-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          </div>

          <select
            className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2"
            value={deptFilter}
            onChange={e => setDeptFilter(e.target.value)}
          >
            <option value="">All Departments</option>
            {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>

          <select
            className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2"
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="PROBATION">Probation</option>
            <option value="ON_LEAVE">On Leave</option>
            <option value="TERMINATED">Terminated</option>
          </select>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-border/40 text-xs">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <span className="text-muted-foreground">Type:</span>
              <select 
                className="bg-transparent border-0 text-white font-medium focus:ring-0 cursor-pointer"
                value={typeFilter}
                onChange={e => setTypeFilter(e.target.value)}
              >
                <option value="">All Types</option>
                <option value="FULL_TIME">Full Time</option>
                <option value="PART_TIME">Part Time</option>
                <option value="CONTRACT">Contract</option>
                <option value="INTERN">Intern</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button 
              onClick={() => setViewMode('list')} 
              className={`p-1.5 rounded ${viewMode === 'list' ? 'bg-secondary text-white' : 'text-muted-foreground'}`}
            >
              <List size={14} />
            </button>
            <button 
              onClick={() => setViewMode('grid')} 
              className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-secondary text-white' : 'text-muted-foreground'}`}
            >
              <LayoutGrid size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Bulk action buttons */}
      {selectedIds.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl text-xs"
        >
          <span className="text-blue-400 font-semibold">{selectedIds.length} employees selected</span>
          <div className="flex space-x-3">
            <button 
              onClick={handleExportCSV}
              className="inline-flex items-center px-3 py-1.5 bg-secondary hover:bg-neutral-800 text-white rounded border border-border transition"
            >
              <Download size={12} className="mr-1.5" />
              Export CSV
            </button>
            <button 
              onClick={handleBulkDeactivate}
              className="inline-flex items-center px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded transition"
            >
              <Trash2 size={12} className="mr-1.5" />
              Deactivate
            </button>
          </div>
        </motion.div>
      )}

      {/* Grid or List displays */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 w-full animate-pulse bg-neutral-800/40 rounded-xl" />
          ))}
        </div>
      ) : employees.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border">
          <p className="text-muted-foreground">No employees found matching the current filters.</p>
        </div>
      ) : viewMode === 'list' ? (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4 w-12">
                  <input 
                    type="checkbox" 
                    className="rounded border-border bg-transparent focus:ring-0"
                    checked={selectedIds.length === employees.length}
                    onChange={e => handleSelectAll(e.target.checked)}
                  />
                </th>
                <th className="px-6 py-4">Employee</th>
                <th className="px-6 py-4">Department</th>
                <th className="px-6 py-4">Designation</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {employees.map(emp => (
                <tr key={emp.id} className="hover:bg-secondary/20 transition-all">
                  <td className="px-6 py-4">
                    <input 
                      type="checkbox" 
                      className="rounded border-border bg-transparent focus:ring-0"
                      checked={selectedIds.includes(emp.id)}
                      onChange={e => handleSelectOne(emp.id, e.target.checked)}
                    />
                  </td>
                  <td className="px-6 py-4">
                    <Link to={`/dashboard/hcm/profile/${emp.id}`} className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-full bg-secondary border border-border flex items-center justify-center font-display text-white text-xs">
                        {emp.first_name[0]}{emp.last_name[0]}
                      </div>
                      <div>
                        <span className="font-semibold text-white block">{emp.first_name} {emp.last_name}</span>
                        <span className="text-[11px] text-muted-foreground font-mono">{emp.employee_id || 'Draft'}</span>
                      </div>
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-neutral-300">{emp.department?.name || 'General'}</td>
                  <td className="px-6 py-4 text-neutral-300">{emp.designation?.name || 'Staff'}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border ${
                      emp.status === 'ACTIVE' 
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                    }`}>
                      {emp.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-neutral-300 capitalize">{emp.employment_type.toLowerCase().replace('_', ' ')}</td>
                  <td className="px-6 py-4">
                    <Link to={`/dashboard/hcm/profile/${emp.id}`} className="text-xs text-blue-400 hover:underline">
                      Manage
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {employees.map(emp => (
            <div key={emp.id} className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-48 hover:border-neutral-700 transition">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-secondary border border-border flex items-center justify-center font-display text-white text-sm">
                    {emp.first_name[0]}{emp.last_name[0]}
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-sm">{emp.first_name} {emp.last_name}</h3>
                    <p className="text-[10px] text-muted-foreground font-mono">{emp.employee_id || 'Draft'}</p>
                  </div>
                </div>
                <input 
                  type="checkbox" 
                  className="rounded border-border bg-transparent focus:ring-0"
                  checked={selectedIds.includes(emp.id)}
                  onChange={e => handleSelectOne(emp.id, e.target.checked)}
                />
              </div>

              <div className="text-xs space-y-1.5 text-neutral-400">
                <p>Dept: <span className="text-white">{emp.department?.name || 'General'}</span></p>
                <p>Designation: <span className="text-white">{emp.designation?.name || 'Staff'}</span></p>
              </div>

              <div className="flex justify-between items-center pt-3 border-t border-border/40">
                <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                  emp.status === 'ACTIVE' 
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                }`}>
                  {emp.status}
                </span>
                <Link to={`/dashboard/hcm/profile/${emp.id}`} className="text-xs text-blue-400 hover:underline">
                  View Profile →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Creation Drawer Modal */}
      <AnimatePresence>
        {drawerOpen && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setDrawerOpen(false)} />
            <motion.aside
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              className="fixed inset-y-0 right-0 w-full max-w-lg bg-card border-l border-border p-8 z-50 overflow-y-auto"
            >
              <h2 className="text-xl font-bold text-white mb-6">Create Employee Profile</h2>
              <form onSubmit={handleCreate} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-muted-foreground font-semibold uppercase tracking-wider mb-2">First Name</label>
                    <input 
                      required
                      className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm"
                      value={createForm.first_name}
                      onChange={e => setCreateForm(prev => ({ ...prev, first_name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-muted-foreground font-semibold uppercase tracking-wider mb-2">Last Name</label>
                    <input 
                      required
                      className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm"
                      value={createForm.last_name}
                      onChange={e => setCreateForm(prev => ({ ...prev, last_name: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-muted-foreground font-semibold uppercase tracking-wider mb-2">Email Address</label>
                  <input 
                    required
                    type="email"
                    className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm"
                    value={createForm.email}
                    onChange={e => setCreateForm(prev => ({ ...prev, email: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-xs text-muted-foreground font-semibold uppercase tracking-wider mb-2">Phone Number</label>
                  <input 
                    className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm"
                    placeholder="+1234567890"
                    value={createForm.phone}
                    onChange={e => setCreateForm(prev => ({ ...prev, phone: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-muted-foreground font-semibold uppercase tracking-wider mb-2">Department</label>
                    <select
                      className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm"
                      value={createForm.department_id}
                      onChange={e => setCreateForm(prev => ({ ...prev, department_id: e.target.value }))}
                    >
                      <option value="">Select Department</option>
                      {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-muted-foreground font-semibold uppercase tracking-wider mb-2">Designation</label>
                    <select
                      className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm"
                      value={createForm.designation_id}
                      onChange={e => setCreateForm(prev => ({ ...prev, designation_id: e.target.value }))}
                    >
                      <option value="">Select Designation</option>
                      {designations.map(ds => <option key={ds.id} value={ds.id}>{ds.name}</option>)}
                    </select>
                  </div>
                </div>

                <div className="flex space-x-3 pt-6 border-t border-border/40">
                  <button 
                    type="button" 
                    onClick={() => setDrawerOpen(false)}
                    className="w-1/2 py-2.5 bg-secondary text-white rounded-lg text-sm hover:bg-neutral-850 transition"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    className="w-1/2 py-2.5 bg-white text-black rounded-lg text-sm font-semibold hover:bg-neutral-200 transition"
                  >
                    Save Draft
                  </button>
                </div>
              </form>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
