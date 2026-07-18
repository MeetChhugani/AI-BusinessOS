import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Inventory, Warehouse, Product } from '../../types/inventory';
import { Search, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const InventoryDirectory: React.FC = () => {
  const { accessToken } = useAuth();
  const [inventory, setInventory] = useState<Inventory[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Filter states
  const [search, setSearch] = useState('');
  const [warehouseFilter, setWarehouseFilter] = useState('');
  
  // Stock adjustment modal states
  const [adjustmentModal, setAdjustmentModal] = useState(false);
  const [adjustForm, setAdjustForm] = useState({
    warehouse_id: '',
    product_id: '',
    new_quantity: '',
    reason: 'Cycle Count Reconciliation'
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const whRes = await fetch('/api/v1/warehouses', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const pRes = await fetch('/api/v1/products', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const invRes = await fetch('/api/v1/inventory', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (whRes.ok) setWarehouses(await whRes.json());
      if (pRes.ok) setProducts(await pRes.json());
      if (invRes.ok) setInventory(await invRes.json());
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

  const handleAdjustStock = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/inventory/adjust', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          warehouse_id: adjustForm.warehouse_id,
          product_id: adjustForm.product_id,
          new_quantity: parseFloat(adjustForm.new_quantity),
          reason: adjustForm.reason
        })
      });
      if (res.ok) {
        setAdjustmentModal(false);
        setAdjustForm({ warehouse_id: '', product_id: '', new_quantity: '', reason: 'Cycle Count Reconciliation' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Helper mapping names
  const getProductName = (prodId: string) => {
    const prod = products.find(p => p.id === prodId);
    return prod ? prod.name : 'Unknown Product';
  };
  const getProductSku = (prodId: string) => {
    const prod = products.find(p => p.id === prodId);
    return prod ? prod.sku : 'Unknown SKU';
  };
  const getWarehouseName = (whId: string) => {
    const wh = warehouses.find(w => w.id === whId);
    return wh ? wh.name : 'Unknown Warehouse';
  };

  const filteredInventory = inventory.filter(item => {
    const matchSearch = getProductName(item.product_id).toLowerCase().includes(search.toLowerCase()) || 
                        getProductSku(item.product_id).toLowerCase().includes(search.toLowerCase());
    const matchWarehouse = warehouseFilter ? item.warehouse_id === warehouseFilter : true;
    return matchSearch && matchWarehouse;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Inventory stock directory
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Trace stock locations, reserved balances, available values, and post corrections.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setAdjustmentModal(true)}
            className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
          >
            <Plus size={14} className="mr-2" />
            Stock Correction
          </button>
        </div>
      </div>

      {/* Filter panel */}
      <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative col-span-2">
            <input
              placeholder="Search by product name or SKU..."
              className="w-full pl-10 pr-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          </div>

          <select
            className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2"
            value={warehouseFilter}
            onChange={e => setWarehouseFilter(e.target.value)}
          >
            <option value="">All Warehouses</option>
            {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
        </div>
      </div>

      {/* Inventory Grid lists */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => <div key={i} className="h-16 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : filteredInventory.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No inventory stock logs matching selection.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Product</th>
                <th className="px-6 py-4">Warehouse</th>
                <th className="px-6 py-4">Physical on-hand</th>
                <th className="px-6 py-4">Reserved</th>
                <th className="px-6 py-4">Available</th>
                <th className="px-6 py-4">Incoming</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {filteredInventory.map(item => (
                <tr key={item.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4">
                    <span className="font-semibold block">{getProductName(item.product_id)}</span>
                    <span className="text-[10px] text-muted-foreground font-mono">{getProductSku(item.product_id)}</span>
                  </td>
                  <td className="px-6 py-4 text-neutral-300">{getWarehouseName(item.warehouse_id)}</td>
                  <td className="px-6 py-4 font-mono text-neutral-200">{item.quantity_on_hand}</td>
                  <td className="px-6 py-4 font-mono text-yellow-400/90">{item.quantity_reserved}</td>
                  <td className="px-6 py-4 font-mono text-emerald-400">{item.quantity_available}</td>
                  <td className="px-6 py-4 font-mono text-blue-400">{item.quantity_incoming}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Adjust Modal Popup */}
      <AnimatePresence>
        {adjustmentModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setAdjustmentModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Post Stock Correction</h2>
              <form onSubmit={handleAdjustStock} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Select Warehouse</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={adjustForm.warehouse_id}
                    onChange={e => setAdjustForm(prev => ({ ...prev, warehouse_id: e.target.value }))}
                  >
                    <option value="">Select Warehouse</option>
                    {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Select Product</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={adjustForm.product_id}
                    onChange={e => setAdjustForm(prev => ({ ...prev, product_id: e.target.value }))}
                  >
                    <option value="">Select Product</option>
                    {products.map(p => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">New Corrected Quantity</label>
                  <input
                    required
                    type="number"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={adjustForm.new_quantity}
                    onChange={e => setAdjustForm(prev => ({ ...prev, new_quantity: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Reason for Variance</label>
                  <input
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={adjustForm.reason}
                    onChange={e => setAdjustForm(prev => ({ ...prev, reason: e.target.value }))}
                  />
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setAdjustmentModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Correction</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
