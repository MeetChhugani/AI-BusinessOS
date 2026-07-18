import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Budget, GeneralLedgerAccount } from '../../types/finance';
import { Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const BudgetsPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [accounts, setAccounts] = useState<GeneralLedgerAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Form states
  const [creationModal, setCreationModal] = useState(false);
  const [name, setName] = useState('');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [lines, setLines] = useState<any[]>([{ account_id: '', allocated_amount: 0 }]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const bRes = await fetch('/api/v1/budgets', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const accRes = await fetch('/api/v1/accounts', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (bRes.ok) setBudgets(await bRes.json());
      if (accRes.ok) setAccounts(await accRes.json());
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

  const handleAddLine = () => {
    setLines([...lines, { account_id: '', allocated_amount: 0 }]);
  };

  const handleLineChange = (index: number, field: string, value: any) => {
    const updated = [...lines];
    updated[index][field] = value;
    setLines(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Mock Cost Center lookup/assign
      const costCenterRes = await fetch('/api/v1/accounts', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      let ccId = '';
      if (costCenterRes.ok) {
        const testData = await costCenterRes.json();
        ccId = testData[0]?.id || '';
      }

      const res = await fetch('/api/v1/budgets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          name,
          cost_center_id: ccId,
          start_date: startDate,
          end_date: endDate,
          lines: lines.map(l => ({
            account_id: l.account_id,
            allocated_amount: parseFloat(l.allocated_amount || '0')
          }))
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setName('');
        setLines([{ account_id: '', allocated_amount: 0 }]);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Cost Center Budgets
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Monitor allocated department limits against real-time expense and debit GL entries.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Establish Budget
        </button>
      </div>

      {/* Budgets List Table */}
      {isLoading ? (
        <div className="space-y-4">
          {[1].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : budgets.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No budgets configured yet.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Budget Name</th>
                <th className="px-6 py-4">Start Date</th>
                <th className="px-6 py-4">End Date</th>
                <th className="px-6 py-4">Allocated Value</th>
                <th className="px-6 py-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {budgets.map(b => {
                const totalAlloc = b.lines.reduce((sum, curr) => sum + curr.allocated_amount, 0);
                return (
                  <tr key={b.id} className="hover:bg-secondary/15 transition">
                    <td className="px-6 py-4 font-bold text-neutral-300">{b.name}</td>
                    <td className="px-6 py-4 text-neutral-300">{b.start_date}</td>
                    <td className="px-6 py-4 text-neutral-300">{b.end_date}</td>
                    <td className="px-6 py-4 font-mono">${totalAlloc.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="px-6 py-4 text-right">
                      <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                        {b.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

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
              <h2 className="text-base font-bold text-white mb-4">Establish Cost Budget</h2>
              <form onSubmit={handleSubmit} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Budget Title</label>
                  <input
                    required
                    placeholder="e.g. FY-2026 Engineering Budget"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={name}
                    onChange={e => setName(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Start Date</label>
                    <input
                      type="date"
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={startDate}
                      onChange={e => setStartDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">End Date</label>
                    <input
                      type="date"
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={endDate}
                      onChange={e => setEndDate(e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-2 pt-2">
                  <div className="flex justify-between items-center">
                    <span className="uppercase text-[10px] font-bold text-muted-foreground">Allocation Lines</span>
                    <button type="button" onClick={handleAddLine} className="text-[10px] text-indigo-400 font-semibold">+ Add line</button>
                  </div>
                  {lines.map((line, idx) => (
                    <div key={idx} className="grid grid-cols-2 gap-2">
                      <select
                        required
                        className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                        value={line.account_id}
                        onChange={e => handleLineChange(idx, 'account_id', e.target.value)}
                      >
                        <option value="">Select Account...</option>
                        {accounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
                      </select>
                      <input
                        type="number"
                        placeholder="Allocated Amount"
                        className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                        value={line.allocated_amount || ''}
                        onChange={e => handleLineChange(idx, 'allocated_amount', e.target.value)}
                      />
                    </div>
                  ))}
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Establish</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
