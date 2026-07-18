import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Customer } from '../../types/crm';
import { Search, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const CustomerDirectory: React.FC = () => {
  const { accessToken } = useAuth();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Filter state
  const [search, setSearch] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('');
  
  // Modals state
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [customerTimeline, setCustomerTimeline] = useState<any[]>([]);
  const [creationModal, setCreationModal] = useState(false);
  
  // Creation form state
  const [custForm, setCustForm] = useState({
    name: '',
    customer_type: 'COMPANY',
    gst_number: '',
    industry: '',
    segment: 'SME',
    credit_limit: '',
    payment_terms: 'NET30',
    territory_id: ''
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const custRes = await fetch('/api/v1/customers', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (custRes.ok) setCustomers(await custRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTimeline = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/customers/${id}/timeline`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setCustomerTimeline(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchData();
    }
  }, [accessToken]);

  const handleCreateCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/customers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          name: custForm.name,
          customer_type: custForm.customer_type,
          gst_number: custForm.gst_number || undefined,
          industry: custForm.industry || undefined,
          segment: custForm.segment,
          credit_limit: parseFloat(custForm.credit_limit || '0'),
          payment_terms: custForm.payment_terms
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setCustForm({ name: '', customer_type: 'COMPANY', gst_number: '', industry: '', segment: 'SME', credit_limit: '', payment_terms: 'NET30', territory_id: '' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const filteredCustomers = customers.filter(c => {
    const matchSearch = c.name.toLowerCase().includes(search.toLowerCase()) || (c.industry && c.industry.toLowerCase().includes(search.toLowerCase()));
    const matchSegment = segmentFilter ? c.segment === segmentFilter : true;
    return matchSearch && matchSegment;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Customer Directory
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Manage company profiles, contact lists, payment terms, and communications history.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Add Customer
        </button>
      </div>

      {/* Filter bar */}
      <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative col-span-2">
            <input
              placeholder="Search by customer name or industry..."
              className="w-full pl-10 pr-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          </div>

          <select
            className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2"
            value={segmentFilter}
            onChange={e => setSegmentFilter(e.target.value)}
          >
            <option value="">All Segments</option>
            <option value="VIP">VIP Segment</option>
            <option value="ENTERPRISE">Enterprise Segment</option>
            <option value="SME">SME Segment</option>
            <option value="DISTRIBUTOR">Distributor Segment</option>
            <option value="GOVERNMENT">Government Segment</option>
          </select>
        </div>
      </div>

      {/* Table grid */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-16 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : filteredCustomers.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No customer records matching selection.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">GST Number</th>
                <th className="px-6 py-4">Segment</th>
                <th className="px-6 py-4">Credit Limit</th>
                <th className="px-6 py-4">Payment Terms</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {filteredCustomers.map(cust => (
                <tr 
                  key={cust.id} 
                  onClick={() => {
                    setSelectedCustomer(cust);
                    fetchTimeline(cust.id);
                  }}
                  className="hover:bg-secondary/15 transition cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <span className="font-bold block">{cust.name}</span>
                    <span className="text-[10px] text-muted-foreground font-medium uppercase mt-0.5 block">{cust.industry || 'General'}</span>
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-300">{cust.gst_number || 'N/A'}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                      {cust.segment}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-300">${cust.credit_limit}</td>
                  <td className="px-6 py-4 text-neutral-300">{cust.payment_terms}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold border bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                      {cust.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Customer details modal */}
      <AnimatePresence>
        {selectedCustomer && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setSelectedCustomer(null)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl space-y-6"
            >
              <div className="flex justify-between items-center border-b border-border/40 pb-3">
                <div>
                  <h3 className="font-bold text-white text-sm">{selectedCustomer.name}</h3>
                  <span className="text-[10px] text-muted-foreground">Industry: {selectedCustomer.industry || 'General'} | Segment: {selectedCustomer.segment}</span>
                </div>
              </div>

              {/* Timeline layout */}
              <div className="space-y-3 text-xs">
                <h4 className="font-semibold text-white uppercase text-[9px] tracking-wider text-muted-foreground">Activity Timeline</h4>
                <div className="bg-secondary/40 border border-border rounded-xl p-4 space-y-3 max-h-48 overflow-y-auto pr-1">
                  {customerTimeline.length === 0 ? (
                    <p className="text-[10px] text-muted-foreground">No activities logged yet.</p>
                  ) : (
                    customerTimeline.map((act, idx) => (
                      <div key={idx} className="flex space-x-3 text-[11px] border-b border-border/10 pb-2 last:border-0 last:pb-0">
                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                        <div>
                          <span className="text-white block font-medium">{act.description}</span>
                          <span className="text-[9px] text-muted-foreground">{act.created_at.slice(0, 16).replace('T', ' ')}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Customer Creation Modal */}
      <AnimatePresence>
        {creationModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setCreationModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Create Customer Profile</h2>
              <form onSubmit={handleCreateCustomer} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Customer / Corporate Name</label>
                  <input
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={custForm.name}
                    onChange={e => setCustForm(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Segment</label>
                    <select
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={custForm.segment}
                      onChange={e => setCustForm(prev => ({ ...prev, segment: e.target.value }))}
                    >
                      <option value="SME">SME</option>
                      <option value="VIP">VIP</option>
                      <option value="ENTERPRISE">Enterprise</option>
                      <option value="DISTRIBUTOR">Distributor</option>
                      <option value="GOVERNMENT">Government</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Industry</label>
                    <input
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={custForm.industry}
                      onChange={e => setCustForm(prev => ({ ...prev, industry: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Credit Limit ($)</label>
                    <input
                      type="number"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={custForm.credit_limit}
                      onChange={e => setCustForm(prev => ({ ...prev, credit_limit: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Payment Terms</label>
                    <select
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={custForm.payment_terms}
                      onChange={e => setCustForm(prev => ({ ...prev, payment_terms: e.target.value }))}
                    >
                      <option value="NET15">NET15</option>
                      <option value="NET30">NET30</option>
                      <option value="NET45">NET45</option>
                      <option value="NET60">NET60</option>
                    </select>
                  </div>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Customer</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
