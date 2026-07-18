import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { GeneralLedgerAccount } from '../../types/finance';
import { Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const ChartOfAccounts: React.FC = () => {
  const { accessToken } = useAuth();
  const [accounts, setAccounts] = useState<GeneralLedgerAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modals state
  const [creationModal, setCreationModal] = useState(false);

  // Form state
  const [accForm, setAccForm] = useState({
    code: '',
    name: '',
    account_type: 'ASSET',
    parent_id: '',
    opening_balance: ''
  });

  const fetchAccounts = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/accounts', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setAccounts(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchAccounts();
    }
  }, [accessToken]);

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/accounts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          code: accForm.code,
          name: accForm.name,
          account_type: accForm.account_type,
          parent_id: accForm.parent_id || undefined,
          opening_balance: parseFloat(accForm.opening_balance || '0')
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setAccForm({ code: '', name: '', account_type: 'ASSET', parent_id: '', opening_balance: '' });
        fetchAccounts();
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
            Chart of Accounts
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Organize assets, liabilities, equities, revenues, and expenditures inside a hierarchical code directory.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Add Account
        </button>
      </div>

      {/* Account List Tree table */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : accounts.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No accounts seeded inside General Ledger Chart.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Account Code</th>
                <th className="px-6 py-4">Account Name</th>
                <th className="px-6 py-4">Classification</th>
                <th className="px-6 py-4 text-right">Balance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {accounts.map(acc => {
                const isChild = !!acc.parent_id;
                return (
                  <tr key={acc.id} className="hover:bg-secondary/15 transition">
                    <td className="px-6 py-4 font-mono text-neutral-300">
                      <span className={isChild ? 'pl-4 block text-[10px] text-muted-foreground' : ''}>
                        {isChild && '└ '} {acc.code}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={isChild ? 'pl-4 block text-[11px] text-muted-foreground' : 'font-bold'}>
                        {acc.name}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                        {acc.account_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-neutral-200">
                      ${acc.current_balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}
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
              <h2 className="text-base font-bold text-white mb-4">Add Account</h2>
              <form onSubmit={handleCreateAccount} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Account Code</label>
                    <input
                      required
                      placeholder="e.g. 1010"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={accForm.code}
                      onChange={e => setAccForm(prev => ({ ...prev, code: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Classification</label>
                    <select
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={accForm.account_type}
                      onChange={e => setAccForm(prev => ({ ...prev, account_type: e.target.value }))}
                    >
                      <option value="ASSET">ASSET</option>
                      <option value="LIABILITY">LIABILITY</option>
                      <option value="EQUITY">EQUITY</option>
                      <option value="REVENUE">REVENUE</option>
                      <option value="EXPENSE">EXPENSE</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Account Name</label>
                  <input
                    required
                    placeholder="e.g. Citibank Operating Account"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={accForm.name}
                    onChange={e => setAccForm(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Parent Account (Optional)</label>
                    <select
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={accForm.parent_id}
                      onChange={e => setAccForm(prev => ({ ...prev, parent_id: e.target.value }))}
                    >
                      <option value="">None</option>
                      {accounts.filter(a => !a.parent_id).map(a => (
                        <option key={a.id} value={a.id}>{a.code} - {a.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Opening Balance ($)</label>
                    <input
                      type="number"
                      placeholder="0.00"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={accForm.opening_balance}
                      onChange={e => setAccForm(prev => ({ ...prev, opening_balance: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Account</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
