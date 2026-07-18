import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { StockTransfer, Warehouse, Product } from '../../types/inventory';
import { Plus, ArrowRight, Truck, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const StockTransfersPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [transfers, setTransfers] = useState<StockTransfer[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // States
  const [creationModal, setCreationModal] = useState(false);
  const [selectedTransfer, setSelectedTransfer] = useState<StockTransfer | null>(null);

  // Form state
  const [transferForm, setTransferForm] = useState({
    source_warehouse_id: '',
    destination_warehouse_id: '',
    product_id: '',
    quantity: ''
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const tfRes = await fetch('/api/v1/transfers', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const whRes = await fetch('/api/v1/warehouses', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const pRes = await fetch('/api/v1/products', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (tfRes.ok) setTransfers(await tfRes.json());
      if (whRes.ok) setWarehouses(await whRes.json());
      if (pRes.ok) setProducts(await pRes.json());
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

  const handleCreateTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/transfers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          source_warehouse_id: transferForm.source_warehouse_id,
          destination_warehouse_id: transferForm.destination_warehouse_id,
          items: [{
            product_id: transferForm.product_id,
            quantity: parseFloat(transferForm.quantity)
          }]
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setTransferForm({ source_warehouse_id: '', destination_warehouse_id: '', product_id: '', quantity: '' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/transfers/${id}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({ approved: true, comments: 'Dispatched for shipping' })
      });
      if (res.ok) {
        setSelectedTransfer(null);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReceive = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/transfers/${id}/receive`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setSelectedTransfer(null);
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const getWarehouseName = (id: string) => {
    return warehouses.find(w => w.id === id)?.name || 'Unknown Warehouse';
  };
  const getProductName = (id: string) => {
    return products.find(p => p.id === id)?.name || 'Unknown Product';
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Inter-Warehouse Stock Transfers
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Relocate stock across stores, issue transit approvals, and record destination intakes.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Request Stock Transfer
        </button>
      </div>

      {/* Timeline List of Transfers */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-28 w-full animate-pulse bg-neutral-800/40 rounded-2xl" />)}
        </div>
      ) : transfers.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No stock transfers requested.
        </div>
      ) : (
        <div className="space-y-4">
          {transfers.map(tf => (
            <div 
              key={tf.id}
              onClick={() => setSelectedTransfer(tf)}
              className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/45 hover:border-neutral-750 transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs"
            >
              <div className="flex items-center space-x-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
                  tf.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                  tf.status === 'IN_TRANSIT' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                  'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                }`}>
                  {tf.status === 'COMPLETED' ? <CheckCircle2 size={18} /> : <Truck size={18} />}
                </div>
                <div>
                  <span className="font-bold text-white font-mono text-sm block">{tf.transfer_number}</span>
                  <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider block mt-0.5">
                    {getWarehouseName(tf.source_warehouse_id)} 
                    <ArrowRight size={10} className="inline mx-1.5 text-neutral-500" /> 
                    {getWarehouseName(tf.destination_warehouse_id)}
                  </span>
                </div>
              </div>

              {/* Status display */}
              <div className="flex items-center space-x-6">
                <div>
                  <span className="text-[9px] text-muted-foreground uppercase font-semibold block">Transfer Date</span>
                  <span className="font-mono text-white block mt-0.5">{tf.created_at.slice(0, 10)}</span>
                </div>
                <span className={`px-2 py-0.5 rounded font-mono text-[9px] font-bold border ${
                  tf.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/15' :
                  tf.status === 'IN_TRANSIT' ? 'bg-blue-500/10 text-blue-400 border-blue-500/15' :
                  'bg-yellow-500/10 text-yellow-400 border-yellow-500/15'
                }`}>
                  {tf.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Transfer Dialog Modal */}
      <AnimatePresence>
        {selectedTransfer && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setSelectedTransfer(null)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl space-y-6"
            >
              <h3 className="font-bold text-white text-sm border-b border-border/40 pb-3">Stock Transfer Details</h3>
              
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-muted-foreground block text-[9px] uppercase font-semibold">Route</span>
                  <span className="text-white block font-medium">
                    From: {getWarehouseName(selectedTransfer.source_warehouse_id)} <br/>
                    To: {getWarehouseName(selectedTransfer.destination_warehouse_id)}
                  </span>
                </div>

                <h4 className="font-semibold text-white uppercase text-[9px] tracking-wider pt-2 text-muted-foreground">Items Relocating</h4>
                <div className="bg-secondary/40 border border-border rounded-xl p-4 space-y-2">
                  {selectedTransfer.items?.map(it => (
                    <div key={it.id} className="flex justify-between items-center text-xs">
                      <span className="text-white font-medium">{getProductName(it.product_id)}</span>
                      <span className="font-semibold text-neutral-300 font-mono">{it.quantity} units</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-3 pt-4 border-t border-border/40 text-xs">
                {selectedTransfer.status === 'DRAFT' && (
                  <button 
                    onClick={() => handleApprove(selectedTransfer.id)} 
                    className="w-full py-2.5 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition"
                  >
                    Approve & Dispatch Shipping
                  </button>
                )}
                {selectedTransfer.status === 'IN_TRANSIT' && (
                  <button 
                    onClick={() => handleReceive(selectedTransfer.id)} 
                    className="w-full py-2.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded hover:bg-emerald-500/15 transition flex items-center justify-center font-semibold"
                  >
                    Receive at Destination Warehouse
                  </button>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Transfer Requisition Modal */}
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
              <h2 className="text-base font-bold text-white mb-4">Request Stock Transfer</h2>
              <form onSubmit={handleCreateTransfer} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Source Warehouse</label>
                    <select
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={transferForm.source_warehouse_id}
                      onChange={e => setTransferForm(prev => ({ ...prev, source_warehouse_id: e.target.value }))}
                    >
                      <option value="">Select Source</option>
                      {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Destination Warehouse</label>
                    <select
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={transferForm.destination_warehouse_id}
                      onChange={e => setTransferForm(prev => ({ ...prev, destination_warehouse_id: e.target.value }))}
                    >
                      <option value="">Select Destination</option>
                      {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Product</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={transferForm.product_id}
                    onChange={e => setTransferForm(prev => ({ ...prev, product_id: e.target.value }))}
                  >
                    <option value="">Select Product</option>
                    {products.map(p => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Quantity</label>
                  <input
                    required
                    type="number"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={transferForm.quantity}
                    onChange={e => setTransferForm(prev => ({ ...prev, quantity: e.target.value }))}
                  />
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Submit Requisition</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
