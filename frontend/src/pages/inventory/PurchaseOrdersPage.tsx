import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { PurchaseOrder, Supplier, Product, Warehouse } from '../../types/inventory';
import { Plus, Package } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const PurchaseOrdersPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal / Detail states
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [creationModal, setCreationModal] = useState(false);
  const [receiveModal, setReceiveModal] = useState(false);
  
  // Creation form state
  const [poForm, setPoForm] = useState({
    supplier_id: '',
    product_id: '',
    quantity: '',
    unit_price: '',
    tax_amount: '0.00',
    discount_amount: '0.00'
  });
  const [receiveWh, setReceiveWh] = useState('');

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const poRes = await fetch('/api/v1/purchase-orders', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const supRes = await fetch('/api/v1/suppliers', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const prodRes = await fetch('/api/v1/products', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const whRes = await fetch('/api/v1/warehouses', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (poRes.ok) setPurchaseOrders(await poRes.json());
      if (supRes.ok) setSuppliers(await supRes.json());
      if (prodRes.ok) setProducts(await prodRes.json());
      if (whRes.ok) setWarehouses(await whRes.json());
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

  const handleCreatePO = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/purchase-orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          supplier_id: poForm.supplier_id,
          items: [{
            product_id: poForm.product_id,
            quantity_ordered: parseFloat(poForm.quantity),
            unit_price: parseFloat(poForm.unit_price),
            tax_rate: 18.0
          }],
          tax_amount: parseFloat(poForm.tax_amount),
          discount_amount: parseFloat(poForm.discount_amount)
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setPoForm({ supplier_id: '', product_id: '', quantity: '', unit_price: '', tax_amount: '0.00', discount_amount: '0.00' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmitPO = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/purchase-orders/${id}/submit`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setSelectedPO(null);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleApprovePO = async (id: string, approved: boolean) => {
    try {
      const res = await fetch(`/api/v1/purchase-orders/${id}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({ approved, comments: 'Approved via procurement manager' })
      });
      if (res.ok) {
        setSelectedPO(null);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReceivePO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPO) return;
    try {
      const res = await fetch(`/api/v1/purchase-orders/${selectedPO.id}/receive?warehouse_id=${receiveWh}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setReceiveModal(false);
        setSelectedPO(null);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const getSupplierName = (supId: string) => {
    return suppliers.find(s => s.id === supId)?.name || 'Unknown Supplier';
  };
  const getProductName = (pId: string) => {
    return products.find(p => p.id === pId)?.name || 'Unknown Product';
  };

  // Kanban boards configuration
  const columns: Array<{ title: string; status: PurchaseOrder['status'] }> = [
    { title: 'Draft', status: 'DRAFT' },
    { title: 'Submitted', status: 'SUBMITTED' },
    { title: 'Approved', status: 'APPROVED' },
    { title: 'Received', status: 'RECEIVED' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Procurement & Purchase Orders
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Procure stock items, approve purchase requisitions, and record Goods Receipt notes.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Create PO Requisition
        </button>
      </div>

      {/* Kanban Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-96 w-full animate-pulse bg-neutral-800/40 rounded-2xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {columns.map(col => {
            const pos = purchaseOrders.filter(po => po.status === col.status);
            return (
              <div key={col.status} className="glass-card rounded-2xl p-4 border border-neutral-800 bg-card/25 min-h-[500px] flex flex-col space-y-4">
                <div className="flex justify-between items-center pb-2 border-b border-border/40">
                  <span className="font-bold text-white text-xs uppercase tracking-wider">{col.title}</span>
                  <span className="bg-secondary text-neutral-300 font-mono text-[10px] px-2 py-0.5 rounded-full">{pos.length}</span>
                </div>

                <div className="flex-grow space-y-3 overflow-y-auto max-h-[450px] pr-1">
                  {pos.map(po => (
                    <div 
                      key={po.id}
                      onClick={() => setSelectedPO(po)}
                      className="p-4 bg-secondary/35 border border-border/60 rounded-xl hover:border-neutral-750 transition cursor-pointer text-xs space-y-2.5"
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-white font-mono">{po.po_number}</span>
                        <span className="text-[10px] text-muted-foreground">{po.created_at.slice(0, 10)}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground font-semibold uppercase text-[9px] block">Supplier</span>
                        <span className="text-white block font-medium truncate">{getSupplierName(po.supplier_id)}</span>
                      </div>
                      <div className="flex justify-between items-center pt-2 border-t border-border/20">
                        <span className="text-[9px] text-muted-foreground uppercase font-semibold">Total Cost</span>
                        <span className="font-bold text-emerald-400 font-mono">${po.total_amount}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* PO Detail / Approval Dialog */}
      <AnimatePresence>
        {selectedPO && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setSelectedPO(null)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl space-y-6"
            >
              <div className="flex justify-between items-center border-b border-border/40 pb-4">
                <div>
                  <h3 className="font-bold text-white text-sm">Purchase Order: {selectedPO.po_number}</h3>
                  <span className="text-[10px] text-muted-foreground">Created by ID: {selectedPO.created_by_id}</span>
                </div>
                <span className="px-2 py-0.5 rounded font-mono text-[9px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/15">
                  {selectedPO.status}
                </span>
              </div>

              {/* Items listing */}
              <div className="space-y-3 text-xs">
                <h4 className="font-semibold text-white uppercase text-[9px] tracking-wider text-muted-foreground">Items Ordered</h4>
                <div className="bg-secondary/40 border border-border rounded-xl p-4 divide-y divide-border/20">
                  {selectedPO.items?.map(it => (
                    <div key={it.id} className="py-2 first:pt-0 last:pb-0 flex justify-between items-center">
                      <div>
                        <span className="text-white font-medium block">{getProductName(it.product_id)}</span>
                        <span className="text-[9px] text-muted-foreground font-mono">Qty Ordered: {it.quantity_ordered} | Recv: {it.quantity_received}</span>
                      </div>
                      <span className="font-semibold text-white font-mono">${it.total_cost}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Aggregates pricing */}
              <div className="border-t border-border/40 pt-4 flex justify-between items-center text-xs">
                <span className="text-muted-foreground font-semibold uppercase text-[9px]">Total Requisition Value</span>
                <span className="font-bold text-emerald-400 font-mono text-base">${selectedPO.total_amount}</span>
              </div>

              {/* PO Workflows buttons */}
              <div className="flex space-x-3 pt-4 border-t border-border/40 text-xs">
                {selectedPO.status === 'DRAFT' && (
                  <button 
                    onClick={() => handleSubmitPO(selectedPO.id)} 
                    className="w-full py-2.5 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition"
                  >
                    Submit for Approval
                  </button>
                )}
                {selectedPO.status === 'SUBMITTED' && (
                  <div className="flex w-full space-x-3">
                    <button 
                      onClick={() => handleApprovePO(selectedPO.id, false)} 
                      className="w-1/2 py-2.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded hover:bg-red-500/15 transition"
                    >
                      Reject
                    </button>
                    <button 
                      onClick={() => handleApprovePO(selectedPO.id, true)} 
                      className="w-1/2 py-2.5 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition"
                    >
                      Approve PO
                    </button>
                  </div>
                )}
                {selectedPO.status === 'APPROVED' && (
                  <button 
                    onClick={() => {
                      setReceiveWh(warehouses[0]?.id || '');
                      setReceiveModal(true);
                    }} 
                    className="w-full py-2.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded hover:bg-emerald-500/15 transition flex items-center justify-center font-semibold"
                  >
                    <Package size={14} className="mr-2" />
                    Record Goods Receipt (GRN)
                  </button>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Requisition Creation Modal */}
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
              <h2 className="text-base font-bold text-white mb-4">Create Requisition PO</h2>
              <form onSubmit={handleCreatePO} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Supplier</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={poForm.supplier_id}
                    onChange={e => setPoForm(prev => ({ ...prev, supplier_id: e.target.value }))}
                  >
                    <option value="">Select Supplier</option>
                    {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Product</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={poForm.product_id}
                    onChange={e => setPoForm(prev => ({ ...prev, product_id: e.target.value }))}
                  >
                    <option value="">Select Product</option>
                    {products.map(p => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Quantity</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={poForm.quantity}
                      onChange={e => setPoForm(prev => ({ ...prev, quantity: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Unit Cost ($)</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={poForm.unit_price}
                      onChange={e => setPoForm(prev => ({ ...prev, unit_price: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Requisition</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Record Goods Receipt modal */}
      <AnimatePresence>
        {receiveModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40 animate-fade-in" onClick={() => setReceiveModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Record Goods Receipt note (GRN)</h2>
              <form onSubmit={handleReceivePO} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Target Warehouse</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={receiveWh}
                    onChange={e => setReceiveWh(e.target.value)}
                  >
                    {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                  </select>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setReceiveModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Complete Receipt</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
