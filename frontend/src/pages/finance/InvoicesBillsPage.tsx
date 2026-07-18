import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { CustomerInvoice, VendorBill } from '../../types/finance';
import { motion, AnimatePresence } from 'framer-motion';

export const InvoicesBillsPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [invoices, setInvoices] = useState<CustomerInvoice[]>([]);
  const [bills, setBills] = useState<VendorBill[]>([]);
  const [activeTab, setActiveTab] = useState<'invoices' | 'bills'>('invoices');
  const [isLoading, setIsLoading] = useState(true);

  // Apply Payment dialog state
  const [paymentModal, setPaymentModal] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<any>(null);
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState('BANK_TRANSFER');

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const invRes = await fetch('/api/v1/invoices', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const billRes = await fetch('/api/v1/vendor-bills', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (invRes.ok) setInvoices(await invRes.json());
      if (billRes.ok) setBills(await billRes.json());
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

  const handleOpenPayment = (doc: any, type: 'invoice' | 'bill') => {
    setSelectedDoc({ ...doc, docType: type });
    setPayAmount(doc.outstanding_balance.toString());
    setPaymentModal(true);
  };

  const handleApplyPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDoc) return;

    try {
      const payload = {
        payment_type: selectedDoc.docType === 'invoice' ? 'CUSTOMER_INFLOW' : 'VENDOR_OUTFLOW',
        payment_date: new Date().toISOString().split('T')[0],
        amount: parseFloat(payAmount),
        payment_method: payMethod,
        allocations: [
          {
            invoice_id: selectedDoc.docType === 'invoice' ? selectedDoc.id : undefined,
            vendor_bill_id: selectedDoc.docType === 'bill' ? selectedDoc.id : undefined,
            allocated_amount: parseFloat(payAmount)
          }
        ]
      };

      const res = await fetch('/api/v1/payments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setPaymentModal(false);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Invoices & Vendor Bills
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Process customer receivables and track upcoming liabilities from purchase orders.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-neutral-800">
        <button
          onClick={() => setActiveTab('invoices')}
          className={`px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 transition ${
            activeTab === 'invoices' ? 'border-indigo-500 text-white' : 'border-transparent text-muted-foreground hover:text-white'
          }`}
        >
          Customer Invoices
        </button>
        <button
          onClick={() => setActiveTab('bills')}
          className={`px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 transition ${
            activeTab === 'bills' ? 'border-indigo-500 text-white' : 'border-transparent text-muted-foreground hover:text-white'
          }`}
        >
          Vendor Bills
        </button>
      </div>

      {/* Loading state */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : activeTab === 'invoices' ? (
        // INVOICES LIST
        invoices.length === 0 ? (
          <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
            No customer invoices generated yet.
          </div>
        ) : (
          <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
                <tr>
                  <th className="px-6 py-4">Invoice #</th>
                  <th className="px-6 py-4">Due Date</th>
                  <th className="px-6 py-4">Terms</th>
                  <th className="px-6 py-4">Total</th>
                  <th className="px-6 py-4">Outstanding</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
                {invoices.map(inv => (
                  <tr key={inv.id} className="hover:bg-secondary/15 transition">
                    <td className="px-6 py-4 font-mono font-bold text-neutral-300">
                      {inv.invoice_number}
                    </td>
                    <td className="px-6 py-4 text-neutral-300">{inv.due_date}</td>
                    <td className="px-6 py-4 text-neutral-300">{inv.payment_terms}</td>
                    <td className="px-6 py-4">${inv.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="px-6 py-4 font-mono text-emerald-400">${inv.outstanding_balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${
                        inv.status === 'PAID' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {inv.outstanding_balance > 0 && (
                        <button
                          onClick={() => handleOpenPayment(inv, 'invoice')}
                          className="px-2.5 py-1 bg-white text-black hover:bg-neutral-200 rounded text-[10px] font-bold"
                        >
                          Receive Payment
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ) : (
        // VENDOR BILLS LIST
        bills.length === 0 ? (
          <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
            No vendor bills generated yet.
          </div>
        ) : (
          <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
                <tr>
                  <th className="px-6 py-4">Bill #</th>
                  <th className="px-6 py-4">Due Date</th>
                  <th className="px-6 py-4">Total</th>
                  <th className="px-6 py-4">Outstanding</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
                {bills.map(b => (
                  <tr key={b.id} className="hover:bg-secondary/15 transition">
                    <td className="px-6 py-4 font-mono font-bold text-neutral-300">
                      {b.bill_number}
                    </td>
                    <td className="px-6 py-4 text-neutral-300">{b.due_date}</td>
                    <td className="px-6 py-4">${b.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="px-6 py-4 font-mono text-red-400">${b.outstanding_balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${
                        b.status === 'PAID' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                        {b.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {b.outstanding_balance > 0 && (
                        <button
                          onClick={() => handleOpenPayment(b, 'bill')}
                          className="px-2.5 py-1 bg-white text-black hover:bg-neutral-200 rounded text-[10px] font-bold"
                        >
                          Record Payment
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {/* Apply Payment Dialog Modal */}
      <AnimatePresence>
        {paymentModal && selectedDoc && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setPaymentModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-sm bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-2">
                {selectedDoc.docType === 'invoice' ? 'Receive Payment' : 'Pay Vendor Bill'}
              </h2>
              <p className="text-[10px] text-muted-foreground mb-4">
                Applying transaction for: {selectedDoc.invoice_number || selectedDoc.bill_number}
              </p>

              <form onSubmit={handleApplyPayment} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Payment Method</label>
                  <select
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={payMethod}
                    onChange={e => setPayMethod(e.target.value)}
                  >
                    <option value="BANK_TRANSFER">BANK TRANSFER</option>
                    <option value="CASH">CASH</option>
                    <option value="CHEQUE">CHEQUE</option>
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Amount ($)</label>
                  <input
                    type="number"
                    required
                    step="0.01"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={payAmount}
                    onChange={e => setPayAmount(e.target.value)}
                  />
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setPaymentModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Post Payment</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
