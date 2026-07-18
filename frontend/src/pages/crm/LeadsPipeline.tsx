import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Lead } from '../../types/crm';
import { Search, Plus, UserCheck, RefreshCw, Flame } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const LeadsPipeline: React.FC = () => {
  const { accessToken } = useAuth();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  
  // Modals state
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [creationModal, setCreationModal] = useState(false);
  const [conversionSuccess, setConversionSuccess] = useState(false);

  // Form state
  const [leadForm, setLeadForm] = useState({
    first_name: '',
    last_name: '',
    company_name: '',
    email: '',
    phone: '',
    source: 'MANUAL',
    status: 'NEW'
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/leads', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setLeads(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchData();
    }
  }, [accessToken]);

  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/leads', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(leadForm)
      });
      if (res.ok) {
        setCreationModal(false);
        setLeadForm({ first_name: '', last_name: '', company_name: '', email: '', phone: '', source: 'MANUAL', status: 'NEW' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleQualifyLead = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/leads/${id}/qualify`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        const updatedLead = await res.json();
        setSelectedLead(updatedLead);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleConvertLead = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/leads/${id}/convert`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setConversionSuccess(true);
        setSelectedLead(null);
        fetchData();
        setTimeout(() => setConversionSuccess(false), 3000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const filteredLeads = leads.filter(l => {
    const matchSearch = `${l.first_name} ${l.last_name}`.toLowerCase().includes(search.toLowerCase()) || 
                        (l.company_name && l.company_name.toLowerCase().includes(search.toLowerCase()));
    const matchSource = sourceFilter ? l.source === sourceFilter : true;
    return matchSearch && matchSource;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Leads Pipeline
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Qualify incoming prospects, run qualification score algorithms, and trigger customer conversions.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Capture Lead
        </button>
      </div>

      {/* Success notification banner */}
      <AnimatePresence>
        {conversionSuccess && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-xl flex items-center gap-2"
          >
            <UserCheck size={16} />
            Lead successfully converted to Customer and contact accounts!
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filter panel */}
      <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative col-span-2">
            <input
              placeholder="Search leads by name or company..."
              className="w-full pl-10 pr-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          </div>

          <select
            className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2"
            value={sourceFilter}
            onChange={e => setSourceFilter(e.target.value)}
          >
            <option value="">All Sources</option>
            <option value="WEBSITE">Website Source</option>
            <option value="REFERRAL">Referral Source</option>
            <option value="CAMPAIGN">Campaign Source</option>
            <option value="MANUAL">Manual Entry</option>
          </select>
        </div>
      </div>

      {/* Leads grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => <div key={i} className="h-44 w-full animate-pulse bg-neutral-800/40 rounded-2xl" />)}
        </div>
      ) : filteredLeads.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No active leads captured.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredLeads.map(l => (
            <div 
              key={l.id}
              onClick={() => setSelectedLead(l)}
              className="glass-card rounded-2xl p-5 border border-neutral-800 hover:border-neutral-700 bg-card/40 transition cursor-pointer flex flex-col justify-between h-44"
            >
              <div>
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white text-xs truncate">{l.first_name} {l.last_name}</span>
                  <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${
                    l.status === 'CONVERTED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                  }`}>
                    {l.status}
                  </span>
                </div>
                <span className="text-[10px] text-muted-foreground mt-0.5 block">{l.company_name || 'Individual Prospect'}</span>
              </div>

              <div className="flex justify-between items-center pt-3 border-t border-border/40 text-xs">
                <span className="text-[9px] text-muted-foreground font-mono">Source: {l.source}</span>
                <span className="flex items-center text-[10px] font-bold font-mono text-yellow-400 bg-yellow-500/10 px-2 py-0.5 rounded border border-yellow-500/15">
                  <Flame size={10} className="mr-1" />
                  Score: {l.score}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Details / qualify convert popup */}
      <AnimatePresence>
        {selectedLead && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setSelectedLead(null)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl space-y-6"
            >
              <div className="flex justify-between items-center border-b border-border/40 pb-3 text-xs">
                <div>
                  <h3 className="font-bold text-white text-sm">{selectedLead.first_name} {selectedLead.last_name}</h3>
                  <span className="text-muted-foreground">{selectedLead.company_name || 'Individual Prospect'}</span>
                </div>
                <span className="font-mono font-bold text-yellow-400 bg-yellow-500/10 px-2 py-0.5 rounded border border-yellow-500/15">
                  Score: {selectedLead.score}%
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <span className="text-muted-foreground uppercase font-semibold text-[9px] block">Contact Card</span>
                <p className="text-white">Email: {selectedLead.email || 'N/A'}</p>
                <p className="text-white">Phone: {selectedLead.phone || 'N/A'}</p>
              </div>

              {selectedLead.status !== 'CONVERTED' && (
                <div className="flex space-x-3 pt-4 border-t border-border/40 text-xs">
                  <button 
                    onClick={() => handleQualifyLead(selectedLead.id)}
                    className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition flex items-center justify-center"
                  >
                    <RefreshCw size={12} className="mr-2" />
                    Qualify Score
                  </button>
                  <button 
                    onClick={() => handleConvertLead(selectedLead.id)}
                    className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition flex items-center justify-center"
                  >
                    <UserCheck size={14} className="mr-2" />
                    Convert to Customer
                  </button>
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Capture Lead Modal */}
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
              <h2 className="text-base font-bold text-white mb-4">Capture Prospect Lead</h2>
              <form onSubmit={handleCreateLead} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">First Name</label>
                    <input
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={leadForm.first_name}
                      onChange={e => setLeadForm(prev => ({ ...prev, first_name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Last Name</label>
                    <input
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={leadForm.last_name}
                      onChange={e => setLeadForm(prev => ({ ...prev, last_name: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Company Name</label>
                  <input
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={leadForm.company_name}
                    onChange={e => setLeadForm(prev => ({ ...prev, company_name: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Email</label>
                    <input
                      type="email"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={leadForm.email}
                      onChange={e => setLeadForm(prev => ({ ...prev, email: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Phone</label>
                    <input
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={leadForm.phone}
                      onChange={e => setLeadForm(prev => ({ ...prev, phone: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Source</label>
                  <select
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={leadForm.source}
                    onChange={e => setLeadForm(prev => ({ ...prev, source: e.target.value }))}
                  >
                    <option value="MANUAL">Manual Entry</option>
                    <option value="WEBSITE">Website</option>
                    <option value="REFERRAL">Referral</option>
                    <option value="CAMPAIGN">Marketing Campaign</option>
                  </select>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Lead</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
