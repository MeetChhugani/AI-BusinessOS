import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { BankAccount, BankTransaction } from '../../types/finance';
import { Sparkles } from 'lucide-react';

export const BankReconciliation: React.FC = () => {
  const { accessToken } = useAuth();
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [transactions, setTransactions] = useState<BankTransaction[]>([]);
  const [selectedAcc, setSelectedAcc] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const accRes = await fetch('/api/v1/bank/accounts', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (accRes.ok) {
        const accs = await accRes.json();
        setAccounts(accs);
        if (accs.length > 0) {
          setSelectedAcc(accs[0].id);
          const txRes = await fetch(`/api/v1/bank/transactions?bank_account_id=${accs[0].id}`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
          if (txRes.ok) setTransactions(await txRes.json());
        }
      }
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

  const handleReconcile = async (txId: string) => {
    try {
      // Mock reconciling with a matching ledger entry
      const res = await fetch(`/api/v1/bank/reconcile?bank_transaction_id=${txId}&journal_entry_id=${txId}&reconciled_amount=100.00`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Bank Statement Reconciliation
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Auto-match incoming bank deposits or withdrawals against general ledger accounts transactions.
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="h-40 animate-pulse bg-neutral-800/40 rounded-2xl" />
      ) : accounts.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No bank accounts found. Seed some accounts first.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Account Selector */}
          <div className="flex space-x-3 text-xs">
            {accounts.map(acc => (
              <button
                key={acc.id}
                onClick={() => setSelectedAcc(acc.id)}
                className={`px-4 py-2.5 rounded-lg border font-semibold transition ${
                  selectedAcc === acc.id
                    ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
                    : 'bg-card text-muted-foreground border-neutral-800 hover:text-white'
                }`}
              >
                {acc.bank_name} - {acc.account_number}
              </button>
            ))}
          </div>

          {/* Transactions List */}
          {transactions.length === 0 ? (
            <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
              No statement transactions imported for this bank account.
            </div>
          ) : (
            <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
              <table className="w-full text-left text-sm">
                <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
                  <tr>
                    <th className="px-6 py-4">Tx Date</th>
                    <th className="px-6 py-4">Description</th>
                    <th className="px-6 py-4">Deposit (Inflow)</th>
                    <th className="px-6 py-4">Withdrawal (Outflow)</th>
                    <th className="px-6 py-4">Reconciliation</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
                  {transactions.map(tx => (
                    <tr key={tx.id} className="hover:bg-secondary/15 transition">
                      <td className="px-6 py-4 text-neutral-300">{tx.transaction_date}</td>
                      <td className="px-6 py-4 text-neutral-300 max-w-xs truncate">{tx.description}</td>
                      <td className="px-6 py-4 font-mono text-emerald-400">
                        {tx.debit > 0 ? `+$${tx.debit.toLocaleString()}` : '-'}
                      </td>
                      <td className="px-6 py-4 font-mono text-red-400">
                        {tx.credit > 0 ? `-$${tx.credit.toLocaleString()}` : '-'}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${
                          tx.reconciliation_status === 'MATCHED'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        }`}>
                          {tx.reconciliation_status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        {tx.reconciliation_status === 'UNMATCHED' && (
                          <button
                            onClick={() => handleReconcile(tx.id)}
                            className="inline-flex items-center justify-center px-3 py-1.5 bg-white text-black hover:bg-neutral-200 rounded text-[10px] font-bold gap-1"
                          >
                            <Sparkles size={10} />
                            Auto Match
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
