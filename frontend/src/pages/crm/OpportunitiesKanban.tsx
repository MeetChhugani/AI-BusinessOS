import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Opportunity, Customer } from '../../types/crm';
import { Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const OpportunitiesKanban: React.FC = () => {
  const { accessToken } = useAuth();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // States
  const [selectedOpp, setSelectedOpp] = useState<Opportunity | null>(null);
  const [creationModal, setCreationModal] = useState(false);
  
  // Creation form state
  const [oppForm, setOppForm] = useState({
    name: '',
    customer_id: '',
    stage: 'PROSPECTING',
    expected_revenue: '',
    close_date: '',
    risk_level: 'LOW'
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const oppRes = await fetch('/api/v1/opportunities', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const custRes = await fetch('/api/v1/customers', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (oppRes.ok) setOpportunities(await oppRes.json());
      if (custRes.ok) setCustomers(await custRes.json());
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

  const handleCreateOpp = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/opportunities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          name: oppForm.name,
          customer_id: oppForm.customer_id,
          stage: oppForm.stage,
          expected_revenue: parseFloat(oppForm.expected_revenue),
          close_date: oppForm.close_date,
          risk_level: oppForm.risk_level
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setOppForm({ name: '', customer_id: '', stage: 'PROSPECTING', expected_revenue: '', close_date: '', risk_level: 'LOW' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleMoveStage = async (id: string, stage: string) => {
    try {
      const res = await fetch(`/api/v1/opportunities/${id}/stage?stage=${stage}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setSelectedOpp(null);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const getCustomerName = (id: string) => {
    return customers.find(c => c.id === id)?.name || 'Unknown Customer';
  };

  const columns: Array<{ title: string; stage: Opportunity['stage'] }> = [
    { title: 'Prospecting', stage: 'PROSPECTING' },
    { title: 'Qualification', stage: 'QUALIFICATION' },
    { title: 'Proposal', stage: 'PROPOSAL' },
    { title: 'Negotiation', stage: 'NEGOTIATION' },
    { title: 'Won', stage: 'WON' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Deals & Opportunities Pipeline
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Monitor sales cycles, expected revenue values, and drag deals across stages.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Add Opportunity
        </button>
      </div>

      {/* Kanban Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-96 w-full animate-pulse bg-neutral-800/40 rounded-2xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {columns.map(col => {
            const opps = opportunities.filter(o => o.stage === col.stage);
            return (
              <div key={col.stage} className="glass-card rounded-2xl p-4 border border-neutral-800 bg-card/25 min-h-[500px] flex flex-col space-y-4">
                <div className="flex justify-between items-center pb-2 border-b border-border/40">
                  <span className="font-bold text-white text-[10px] uppercase tracking-wider">{col.title}</span>
                  <span className="bg-secondary text-neutral-300 font-mono text-[9px] px-2 py-0.5 rounded-full">{opps.length}</span>
                </div>

                <div className="flex-grow space-y-3 overflow-y-auto max-h-[450px] pr-1">
                  {opps.map(opp => (
                    <div 
                      key={opp.id}
                      onClick={() => setSelectedOpp(opp)}
                      className="p-3 bg-secondary/35 border border-border/60 rounded-xl hover:border-neutral-750 transition cursor-pointer text-xs space-y-2"
                    >
                      <div className="flex justify-between items-start">
                        <span className="font-bold text-white truncate max-w-[110px]">{opp.name}</span>
                        <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold ${
                          opp.risk_level === 'HIGH' ? 'bg-red-500/10 text-red-400 border border-red-500/15' : 'bg-green-500/10 text-green-400 border border-green-500/15'
                        }`}>
                          {opp.risk_level}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground text-[9px] block">Customer</span>
                        <span className="text-white block truncate">{getCustomerName(opp.customer_id)}</span>
                      </div>
                      <div className="flex justify-between items-center pt-1.5 border-t border-border/20">
                        <span className="text-[9px] text-muted-foreground font-mono">Prob: {opp.probability}%</span>
                        <span className="font-bold text-emerald-400 font-mono">${opp.expected_revenue}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Opportunity Stage Shifter Dialog */}
      <AnimatePresence>
        {selectedOpp && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setSelectedOpp(null)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl space-y-6"
            >
              <div className="flex justify-between items-center border-b border-border/40 pb-3">
                <h3 className="font-bold text-white text-sm">{selectedOpp.name}</h3>
                <span className="px-2 py-0.5 rounded font-mono text-[9px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/15">
                  {selectedOpp.stage}
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <p className="text-white">Customer: {getCustomerName(selectedOpp.customer_id)}</p>
                <p className="text-white">Expected revenue forecast: <span className="font-mono text-emerald-400">${selectedOpp.expected_revenue}</span></p>
                <p className="text-white">Close Date: <span className="font-mono text-neutral-300">{selectedOpp.close_date}</span></p>
              </div>

              <div className="space-y-2 pt-4 border-t border-border/40 text-xs">
                <span className="text-muted-foreground uppercase font-semibold text-[9px] block">Move Stage</span>
                <div className="grid grid-cols-2 gap-2">
                  {columns.map(col => (
                    <button 
                      key={col.stage}
                      onClick={() => handleMoveStage(selectedOpp.id, col.stage)}
                      className="py-1.5 bg-secondary hover:bg-neutral-800 text-white rounded text-[10px] transition border border-border/40"
                    >
                      {col.title}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Creation Modal */}
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
              <h2 className="text-base font-bold text-white mb-4">Add Opportunity</h2>
              <form onSubmit={handleCreateOpp} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Deal Name</label>
                  <input
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={oppForm.name}
                    onChange={e => setOppForm(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Customer</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={oppForm.customer_id}
                    onChange={e => setOppForm(prev => ({ ...prev, customer_id: e.target.value }))}
                  >
                    <option value="">Select Customer</option>
                    {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Expected Revenue ($)</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={oppForm.expected_revenue}
                      onChange={e => setOppForm(prev => ({ ...prev, expected_revenue: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Target Close Date</label>
                    <input
                      required
                      type="date"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={oppForm.close_date}
                      onChange={e => setOppForm(prev => ({ ...prev, close_date: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Risk Level</label>
                  <select
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={oppForm.risk_level}
                    onChange={e => setOppForm(prev => ({ ...prev, risk_level: e.target.value }))}
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                  </select>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Deal</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
