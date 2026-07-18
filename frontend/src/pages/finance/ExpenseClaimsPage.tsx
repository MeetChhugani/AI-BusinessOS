import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { ExpenseClaim, ExpenseCategory } from '../../types/finance';
import { Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const ExpenseClaimsPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [claims, setClaims] = useState<ExpenseClaim[]>([]);
  const [categories, setCategories] = useState<ExpenseCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Form states
  const [creationModal, setCreationModal] = useState(false);
  const [amount, setAmount] = useState('');
  const [claimDate, setClaimDate] = useState(new Date().toISOString().split('T')[0]);
  const [catId, setCatId] = useState('');
  const [description, setDescription] = useState('');

  // Approval state
  const [commentModal, setCommentModal] = useState(false);
  const [activeClaimId, setActiveClaimId] = useState<string>('');
  const [appComment, setAppComment] = useState('');

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const cRes = await fetch('/api/v1/expenses', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      await fetch('/api/v1/accounts', { headers: { 'Authorization': `Bearer ${accessToken}` } }); // we'll mock categories list from accounts or default configuration
      if (cRes.ok) setClaims(await cRes.json());
      // Seed default categories mock
      setCategories([
        { id: '1', name: 'Travel & Transport', code: 'TRAVEL' },
        { id: '2', name: 'Meals & Business Entertainment', code: 'MEALS' }
      ]);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/expenses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          expense_category_id: categories[0].id, // fallback default
          amount: parseFloat(amount),
          claim_date: claimDate,
          description
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setAmount('');
        setDescription('');
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const openApprove = (id: string) => {
    setActiveClaimId(id);
    setAppComment('');
    setCommentModal(true);
  };

  const handleDecision = async (approved: boolean) => {
    try {
      const res = await fetch(`/api/v1/expenses/${activeClaimId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          approved,
          comments: appComment
        })
      });
      if (res.ok) {
        setCommentModal(false);
        fetchData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Corporate Expense Claims
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Submit out-of-pocket employee expense reimbursements and run approval logic workflows.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Submit Claim
        </button>
      </div>

      {/* Claims List Table */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : claims.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No expense claims recorded.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Claim #</th>
                <th className="px-6 py-4">Claim Date</th>
                <th className="px-6 py-4">Memo / Description</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {claims.map(claim => (
                <tr key={claim.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4 font-mono font-bold text-neutral-300">
                    {claim.claim_number}
                  </td>
                  <td className="px-6 py-4 text-neutral-300">{claim.claim_date}</td>
                  <td className="px-6 py-4 text-neutral-300 max-w-sm truncate">{claim.description}</td>
                  <td className="px-6 py-4 font-mono text-neutral-200">${claim.amount.toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${
                      claim.status === 'REIMBURSED' || claim.status === 'APPROVED'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : claim.status === 'REJECTED'
                        ? 'bg-red-500/10 text-red-400 border-red-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>
                      {claim.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {claim.status === 'SUBMITTED' && (
                      <button
                        onClick={() => openApprove(claim.id)}
                        className="px-2.5 py-1 bg-white text-black hover:bg-neutral-200 rounded text-[10px] font-bold"
                      >
                        Workflow Action
                      </button>
                    )}
                  </td>
                </tr>
              ))}
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
              <h2 className="text-base font-bold text-white mb-4">Submit Expense Claim</h2>
              <form onSubmit={handleSubmit} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Claim Date</label>
                    <input
                      type="date"
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={claimDate}
                      onChange={e => setClaimDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Claim Amount ($)</label>
                    <input
                      type="number"
                      required
                      placeholder="0.00"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={amount}
                      onChange={e => setAmount(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Claim Category</label>
                  <select
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={catId}
                    onChange={e => setCatId(e.target.value)}
                  >
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Memo Explanation</label>
                  <input
                    required
                    placeholder="e.g. Sales team client dinner"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                  />
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Submit Claim</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Decision/Workflow Modal */}
      <AnimatePresence>
        {commentModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setCommentModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-sm bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-2">Workflow Action</h2>
              <p className="text-[10px] text-muted-foreground mb-4">Provide reviewer review comments below</p>
              
              <div className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Comments</label>
                  <input
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    placeholder="e.g. Approved within standard policy"
                    value={appComment}
                    onChange={e => setAppComment(e.target.value)}
                  />
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button
                    onClick={() => handleDecision(false)}
                    className="w-1/2 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded font-semibold transition"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleDecision(true)}
                    className="w-1/2 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 rounded font-semibold transition"
                  >
                    Approve
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
