import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { JournalEntry, GeneralLedgerAccount } from '../../types/finance';
import { Plus, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const JournalEntries: React.FC = () => {
  const { accessToken } = useAuth();
  const [journals, setJournals] = useState<JournalEntry[]>([]);
  const [accounts, setAccounts] = useState<GeneralLedgerAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Form states
  const [creationModal, setCreationModal] = useState(false);
  const [description, setDescription] = useState('');
  const [entryDate, setEntryDate] = useState(new Date().toISOString().split('T')[0]);
  const [lines, setLines] = useState<any[]>([
    { account_id: '', debit: 0, credit: 0 },
    { account_id: '', debit: 0, credit: 0 }
  ]);
  const [errorMsg, setErrorMsg] = useState('');

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const jRes = await fetch('/api/v1/journal', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const aRes = await fetch('/api/v1/accounts', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (jRes.ok) setJournals(await jRes.json());
      if (aRes.ok) setAccounts(await aRes.json());
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
    setLines([...lines, { account_id: '', debit: 0, credit: 0 }]);
  };

  const handleRemoveLine = (idx: number) => {
    setLines(lines.filter((_, i) => i !== idx));
  };

  const handleLineChange = (index: number, field: string, val: any) => {
    const updated = [...lines];
    updated[index][field] = val;
    setLines(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    // Check balances
    const debits = lines.reduce((acc, curr) => acc + parseFloat(curr.debit || '0'), 0);
    const credits = lines.reduce((acc, curr) => acc + parseFloat(curr.credit || '0'), 0);

    if (Math.abs(debits - credits) > 0.01) {
      setErrorMsg(`Unbalanced journal: Debits ($${debits}) must equal Credits ($${credits})`);
      return;
    }

    try {
      const res = await fetch('/api/v1/journal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          entry_date: entryDate,
          description,
          lines: lines.map(l => ({
            account_id: l.account_id,
            debit: parseFloat(l.debit || '0'),
            credit: parseFloat(l.credit || '0')
          }))
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setDescription('');
        setLines([
          { account_id: '', debit: 0, credit: 0 },
          { account_id: '', debit: 0, credit: 0 }
        ]);
        fetchData();
      } else {
        const errorData = await res.json();
        setErrorMsg(errorData.detail || 'Failed to post entry');
      }
    } catch (err) {
      setErrorMsg('Network error posting journal entry');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            General Ledger Journal Entries
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Immutable transaction records. Debits must equal Credits to preserve the double-entry bookkeeping identity.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Create Entry
        </button>
      </div>

      {/* Journals Log Table */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : journals.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No journal entries recorded.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">JE Number</th>
                <th className="px-6 py-4">Posting Date</th>
                <th className="px-6 py-4">Memo / Description</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Debit Balance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {journals.map(j => {
                const totalDebits = j.lines.reduce((sum, curr) => sum + curr.debit, 0);
                return (
                  <tr key={j.id} className="hover:bg-secondary/15 transition">
                    <td className="px-6 py-4 font-mono font-bold text-neutral-300">
                      {j.entry_number}
                    </td>
                    <td className="px-6 py-4 text-neutral-300">
                      {j.entry_date}
                    </td>
                    <td className="px-6 py-4 max-w-sm truncate text-neutral-300">
                      {j.description}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                        {j.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-neutral-200">
                      ${totalDebits.toLocaleString(undefined, { minimumFractionDigits: 2 })}
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
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl overflow-y-auto max-h-[90vh]"
            >
              <h2 className="text-base font-bold text-white mb-4">Post Double-Entry Journal</h2>
              {errorMsg && (
                <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded text-[11px] font-medium">
                  {errorMsg}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Posting Date</label>
                    <input
                      type="date"
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={entryDate}
                      onChange={e => setEntryDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Memo Description</label>
                    <input
                      required
                      placeholder="e.g. Month-end utility accrual"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={description}
                      onChange={e => setDescription(e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-3 pt-2">
                  <div className="flex justify-between items-center">
                    <span className="uppercase text-[10px] font-bold text-muted-foreground">Ledger Lines</span>
                    <button type="button" onClick={handleAddLine} className="text-[10px] text-indigo-400 hover:text-indigo-300 font-semibold">
                      + Add Line
                    </button>
                  </div>

                  {lines.map((line, idx) => (
                    <div key={idx} className="grid grid-cols-12 gap-3 items-center">
                      <div className="col-span-6">
                        <select
                          required
                          className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                          value={line.account_id}
                          onChange={e => handleLineChange(idx, 'account_id', e.target.value)}
                        >
                          <option value="">Select Account...</option>
                          {accounts.map(a => (
                            <option key={a.id} value={a.id}>{a.code} - {a.name}</option>
                          ))}
                        </select>
                      </div>
                      <div className="col-span-2">
                        <input
                          type="number"
                          placeholder="Debit"
                          className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                          value={line.debit || ''}
                          onChange={e => handleLineChange(idx, 'debit', e.target.value)}
                        />
                      </div>
                      <div className="col-span-2">
                        <input
                          type="number"
                          placeholder="Credit"
                          className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                          value={line.credit || ''}
                          onChange={e => handleLineChange(idx, 'credit', e.target.value)}
                        />
                      </div>
                      <div className="col-span-2 text-right">
                        {lines.length > 2 && (
                          <button type="button" onClick={() => handleRemoveLine(idx)} className="text-red-400 hover:text-red-300 p-1.5">
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex space-x-3 pt-6 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2.5 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2.5 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Post Entry</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
