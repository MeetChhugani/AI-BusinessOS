import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Quotation, SalesOrder, Customer } from '../../types/crm';
import { Product } from '../../types/inventory';
import { Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const QuotationsOrdersPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [quotations, setQuotations] = useState<Quotation[]>([]);
  const [salesOrders, setSalesOrders] = useState<SalesOrder[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Active Tab
  const [activeTab, setActiveTab] = useState<'quotes' | 'orders'>('quotes');
  const [selectedQuote, setSelectedQuote] = useState<Quotation | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);

  // Requisitions modally
  const [quoteModal, setQuoteModal] = useState(false);
  const [orderModal, setOrderModal] = useState(false);

  // Form states
  const [qForm, setQForm] = useState({
    customer_id: '',
    product_id: '',
    quantity: '',
    unit_price: '',
    valid_until: ''
  });
  const [soForm, setSoForm] = useState({
    customer_id: '',
    product_id: '',
    quantity: '',
    unit_price: ''
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const qRes = await fetch('/api/v1/quotations', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const soRes = await fetch('/api/v1/orders', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const custRes = await fetch('/api/v1/customers', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const prodRes = await fetch('/api/v1/products', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (qRes.ok) setQuotations(await qRes.json());
      if (soRes.ok) setSalesOrders(await soRes.json());
      if (custRes.ok) setCustomers(await custRes.json());
      if (prodRes.ok) setProducts(await prodRes.json());
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

  const handleCreateQuote = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/quotations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          customer_id: qForm.customer_id,
          items: [{
            product_id: qForm.product_id,
            quantity: parseFloat(qForm.quantity),
            unit_price: parseFloat(qForm.unit_price)
          }],
          valid_until: qForm.valid_until
        })
      });
      if (res.ok) {
        setQuoteModal(false);
        setQForm({ customer_id: '', product_id: '', quantity: '', unit_price: '', valid_until: '' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          customer_id: soForm.customer_id,
          items: [{
            product_id: soForm.product_id,
            quantity: parseFloat(soForm.quantity),
            unit_price: parseFloat(soForm.unit_price)
          }]
        })
      });
      if (res.ok) {
        setOrderModal(false);
        setSoForm({ customer_id: '', product_id: '', quantity: '', unit_price: '' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmitQuote = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/quotations/${id}/submit`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setSelectedQuote(null);
        fetchData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmitOrder = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/orders/${id}/submit`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setSelectedOrder(null);
        fetchData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleApproveOrder = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/orders/${id}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({ approved: true, comments: 'Sales order check correct. Allocated stock.' })
      });
      if (res.ok) {
        setSelectedOrder(null);
        fetchData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const getCustomerName = (id: string) => {
    return customers.find(c => c.id === id)?.name || 'Unknown Customer';
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Quotations & Sales Orders
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Pricing engine quotes, sales order pipelines, and stock reservation controls.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => {
              if (activeTab === 'quotes') setQuoteModal(true);
              else setOrderModal(true);
            }}
            className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
          >
            <Plus size={14} className="mr-2" />
            Create {activeTab === 'quotes' ? 'Quotation' : 'Sales Order'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-border/40 pb-px text-xs">
        <button 
          onClick={() => setActiveTab('quotes')}
          className={`pb-3 font-semibold ${activeTab === 'quotes' ? 'border-b-2 border-blue-500 text-white' : 'text-muted-foreground hover:text-white'}`}
        >
          Quotations
        </button>
        <button 
          onClick={() => setActiveTab('orders')}
          className={`pb-3 font-semibold ${activeTab === 'orders' ? 'border-b-2 border-blue-500 text-white' : 'text-muted-foreground hover:text-white'}`}
        >
          Sales Orders
        </button>
      </div>

      {/* Grid lists */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-16 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : activeTab === 'quotes' ? (
        // Quotation grid
        quotations.length === 0 ? (
          <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
            No quotations generated.
          </div>
        ) : (
          <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
                <tr>
                  <th className="px-6 py-4">Quote Number</th>
                  <th className="px-6 py-4">Customer</th>
                  <th className="px-6 py-4">Total Amount</th>
                  <th className="px-6 py-4">Valid Until</th>
                  <th className="px-6 py-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
                {quotations.map(q => (
                  <tr 
                    key={q.id}
                    onClick={() => setSelectedQuote(q)}
                    className="hover:bg-secondary/15 transition cursor-pointer"
                  >
                    <td className="px-6 py-4 font-mono font-bold text-neutral-200">{q.quotation_number} (v{q.version})</td>
                    <td className="px-6 py-4 text-neutral-300">{getCustomerName(q.customer_id)}</td>
                    <td className="px-6 py-4 font-mono text-emerald-400">${q.total_amount}</td>
                    <td className="px-6 py-4 font-mono text-neutral-300">{q.valid_until}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded text-[9px] font-bold border bg-blue-500/10 text-blue-400 border-blue-500/15">
                        {q.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ) : (
        // Sales Orders grid
        salesOrders.length === 0 ? (
          <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
            No sales orders created.
          </div>
        ) : (
          <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
                <tr>
                  <th className="px-6 py-4">Order Number</th>
                  <th className="px-6 py-4">Customer</th>
                  <th className="px-6 py-4">Total Amount</th>
                  <th className="px-6 py-4">Shipping</th>
                  <th className="px-6 py-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
                {salesOrders.map(so => (
                  <tr 
                    key={so.id}
                    onClick={() => setSelectedOrder(so)}
                    className="hover:bg-secondary/15 transition cursor-pointer"
                  >
                    <td className="px-6 py-4 font-mono font-bold text-neutral-200">{so.order_number}</td>
                    <td className="px-6 py-4 text-neutral-300">{getCustomerName(so.customer_id)}</td>
                    <td className="px-6 py-4 font-mono text-emerald-400">${so.total_amount}</td>
                    <td className="px-6 py-4 text-neutral-300">{so.shipping_status}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded text-[9px] font-bold border bg-purple-500/10 text-purple-400 border-purple-500/15">
                        {so.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {/* Quote Dialog */}
      <AnimatePresence>
        {selectedQuote && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setSelectedQuote(null)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl space-y-6"
            >
              <h3 className="font-bold text-white text-sm border-b border-border/40 pb-3">Quote: {selectedQuote.quotation_number}</h3>
              <div className="space-y-3 text-xs">
                <p className="text-white">Customer: {getCustomerName(selectedQuote.customer_id)}</p>
                <p className="text-white">Quote total amount: <span className="font-mono text-emerald-400">${selectedQuote.total_amount}</span></p>
              </div>

              {selectedQuote.status === 'DRAFT' && (
                <button 
                  onClick={() => handleSubmitQuote(selectedQuote.id)}
                  className="w-full py-2.5 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition text-xs"
                >
                  Submit Quote for Approval
                </button>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Order Dialog with reservation button */}
      <AnimatePresence>
        {selectedOrder && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setSelectedOrder(null)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl space-y-6"
            >
              <h3 className="font-bold text-white text-sm border-b border-border/40 pb-3">Order: {selectedOrder.order_number}</h3>
              <div className="space-y-3 text-xs">
                <p className="text-white">Customer: {getCustomerName(selectedOrder.customer_id)}</p>
                <p className="text-white">Order total: <span className="font-mono text-emerald-400">${selectedOrder.total_amount}</span></p>
              </div>

              <div className="flex space-x-3 pt-4 border-t border-border/40 text-xs">
                {selectedOrder.status === 'DRAFT' && (
                  <button 
                    onClick={() => handleSubmitOrder(selectedOrder.id)}
                    className="w-full py-2.5 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition"
                  >
                    Submit for Review
                  </button>
                )}
                {selectedOrder.status === 'PENDING_APPROVAL' && (
                  <button 
                    onClick={() => handleApproveOrder(selectedOrder.id)}
                    className="w-full py-2.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded hover:bg-emerald-500/15 transition flex items-center justify-center font-semibold animate-pulse"
                  >
                    Approve Order & Reserve stock
                  </button>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Quote Requisition Modal */}
      <AnimatePresence>
        {quoteModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setQuoteModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Generate pricing quote</h2>
              <form onSubmit={handleCreateQuote} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Select Customer</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={qForm.customer_id}
                    onChange={e => setQForm(prev => ({ ...prev, customer_id: e.target.value }))}
                  >
                    <option value="">Select Customer</option>
                    {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.segment} Segment)</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Select Product</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={qForm.product_id}
                    onChange={e => setQForm(prev => ({ ...prev, product_id: e.target.value }))}
                  >
                    <option value="">Select Product</option>
                    {products.map(p => <option key={p.id} value={p.id}>{p.name} (${p.selling_price})</option>)}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Quantity</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={qForm.quantity}
                      onChange={e => setQForm(prev => ({ ...prev, quantity: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Baseline Unit price</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={qForm.unit_price}
                      onChange={e => setQForm(prev => ({ ...prev, unit_price: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Valid Until</label>
                  <input
                    required
                    type="date"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={qForm.valid_until}
                    onChange={e => setQForm(prev => ({ ...prev, valid_until: e.target.value }))}
                  />
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setQuoteModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Run Pricing Engine</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Order Requisition Modal */}
      <AnimatePresence>
        {orderModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setOrderModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Create Sales Order</h2>
              <form onSubmit={handleCreateOrder} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Customer</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={soForm.customer_id}
                    onChange={e => setSoForm(prev => ({ ...prev, customer_id: e.target.value }))}
                  >
                    <option value="">Select Customer</option>
                    {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Select Product</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={soForm.product_id}
                    onChange={e => setSoForm(prev => ({ ...prev, product_id: e.target.value }))}
                  >
                    <option value="">Select Product</option>
                    {products.map(p => <option key={p.id} value={p.id}>{p.name} (${p.selling_price})</option>)}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Quantity</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={soForm.quantity}
                      onChange={e => setSoForm(prev => ({ ...prev, quantity: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Unit Price</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={soForm.unit_price}
                      onChange={e => setSoForm(prev => ({ ...prev, unit_price: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setOrderModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Order</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
