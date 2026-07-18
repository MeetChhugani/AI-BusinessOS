import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { InventoryAudit, Warehouse, Inventory, Product } from '../../types/inventory';
import { Plus, ClipboardCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const AuditsPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [audits, setAudits] = useState<InventoryAudit[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [inventory, setInventory] = useState<Inventory[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // States
  const [selectedAudit, setSelectedAudit] = useState<InventoryAudit | null>(null);
  const [creationModal, setCreationModal] = useState(false);
  const [countModal, setCountModal] = useState(false);

  // Form states
  const [scheduleWarehouse, setScheduleWarehouse] = useState('');
  const [countForm, setCountForm] = useState({
    inventory_id: '',
    physical_qty: ''
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const auRes = await fetch('/api/v1/audits', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const whRes = await fetch('/api/v1/warehouses', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const invRes = await fetch('/api/v1/inventory', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const pRes = await fetch('/api/v1/products', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (auRes.ok) setAudits(await auRes.json());
      if (whRes.ok) setWarehouses(await whRes.json());
      if (invRes.ok) setInventory(await invRes.json());
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

  const handleScheduleAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`/api/v1/audits?warehouse_id=${scheduleWarehouse}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setCreationModal(false);
        setScheduleWarehouse('');
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRecordCount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAudit) return;
    try {
      const res = await fetch(`/api/v1/audits/${selectedAudit.id}/count?inventory_id=${countForm.inventory_id}&physical_qty=${parseFloat(countForm.physical_qty)}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setCountModal(false);
        setCountForm({ inventory_id: '', physical_qty: '' });
        // Refetch audit detail
        const detRes = await fetch('/api/v1/audits', { headers: { 'Authorization': `Bearer ${accessToken}` } });
        if (detRes.ok) {
          const allAu = await detRes.json();
          const updated = allAu.find((a: any) => a.id === selectedAudit.id);
          if (updated) setSelectedAudit(updated);
          setAudits(allAu);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCommitAudit = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/audits/${id}/commit`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setSelectedAudit(null);
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
  const getProductSku = (id: string) => {
    return products.find(p => p.id === id)?.sku || 'Unknown SKU';
  };

  // Filter inventory items specifically inside selected audit warehouse
  const filteredInvForAudit = selectedAudit 
    ? inventory.filter(inv => inv.warehouse_id === selectedAudit.warehouse_id)
    : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Inventory Cycle Count & Audits
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Schedule physical stock counts, log inventory discrepancies, and reconcile variance books.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Schedule Cycle Count
        </button>
      </div>

      {/* Grid listing audits */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-20 w-full animate-pulse bg-neutral-800/40 rounded-2xl" />)}
        </div>
      ) : audits.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No inventory audits scheduled.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {audits.map(au => (
            <div 
              key={au.id}
              onClick={() => setSelectedAudit(au)}
              className="glass-card rounded-2xl p-6 border border-neutral-800 bg-card/45 hover:border-neutral-750 transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs"
            >
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400">
                  <ClipboardCheck size={18} />
                </div>
                <div>
                  <span className="font-bold text-white font-mono text-sm block">{au.audit_number}</span>
                  <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider block mt-0.5">
                    Warehouse: {getWarehouseName(au.warehouse_id)}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <div>
                  <span className="text-[9px] text-muted-foreground uppercase font-semibold block">Scheduled At</span>
                  <span className="font-mono text-white block mt-0.5">
                    {au.started_at ? au.started_at.slice(0, 16).replace('T', ' ') : 'N/A'}
                  </span>
                </div>
                <span className={`px-2 py-0.5 rounded font-mono text-[9px] font-bold border ${
                  au.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/15' :
                  au.status === 'IN_PROGRESS' ? 'bg-blue-500/10 text-blue-400 border-blue-500/15' :
                  'bg-yellow-500/10 text-yellow-400 border-yellow-500/15'
                }`}>
                  {au.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Cycle Count Audit Dialog Modal */}
      <AnimatePresence>
        {selectedAudit && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setSelectedAudit(null)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl space-y-6"
            >
              <div className="flex justify-between items-center border-b border-border/40 pb-3">
                <h3 className="font-bold text-white text-sm">Audit: {selectedAudit.audit_number}</h3>
                <span className="px-2 py-0.5 rounded font-mono text-[9px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/15">
                  {selectedAudit.status}
                </span>
              </div>

              {/* Items listing counted */}
              <div className="space-y-3 text-xs">
                <div className="flex justify-between items-center">
                  <h4 className="font-semibold text-white uppercase text-[9px] tracking-wider text-muted-foreground">Variance Reports</h4>
                  {selectedAudit.status !== 'COMPLETED' && (
                    <button 
                      onClick={() => setCountModal(true)} 
                      className="px-2 py-1 bg-secondary hover:bg-neutral-800 text-white rounded text-[10px] border border-border/40 transition"
                    >
                      Count item quantity
                    </button>
                  )}
                </div>

                <div className="bg-secondary/40 border border-border rounded-xl p-4 divide-y divide-border/20 max-h-48 overflow-y-auto pr-1">
                  {selectedAudit.items?.length === 0 ? (
                    <p className="text-[10px] text-muted-foreground py-2">No items counted yet.</p>
                  ) : (
                    selectedAudit.items?.map(it => {
                      const matchedInv = inventory.find(i => i.id === it.inventory_id);
                      const prodName = matchedInv ? getProductName(matchedInv.product_id) : 'Unknown Item';
                      return (
                        <div key={it.id} className="py-2.5 first:pt-0 last:pb-0 flex justify-between items-center">
                          <div>
                            <span className="text-white font-medium block">{prodName}</span>
                            <span className="text-[9px] text-muted-foreground font-mono">System: {it.system_quantity} | Counted: {it.physical_quantity}</span>
                          </div>
                          <span className={`font-semibold font-mono ${it.variance === 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {it.variance > 0 ? `+${it.variance}` : it.variance}
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              {/* Action buttons */}
              {selectedAudit.status !== 'COMPLETED' && (
                <button 
                  onClick={() => handleCommitAudit(selectedAudit.id)} 
                  className="w-full py-2.5 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition text-xs"
                >
                  Commit & Reconcile Variance Discrepancies
                </button>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Schedule Audit Modal */}
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
              <h2 className="text-base font-bold text-white mb-4">Schedule Cycle Count Audit</h2>
              <form onSubmit={handleScheduleAudit} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Audit Warehouse Target</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={scheduleWarehouse}
                    onChange={e => setScheduleWarehouse(e.target.value)}
                  >
                    <option value="">Select Warehouse</option>
                    {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                  </select>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Schedule Audit</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Record counted item quantity modal */}
      <AnimatePresence>
        {countModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setCountModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Log Counted Item</h2>
              <form onSubmit={handleRecordCount} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Select stock Item</label>
                  <select
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={countForm.inventory_id}
                    onChange={e => setCountForm(prev => ({ ...prev, inventory_id: e.target.value }))}
                  >
                    <option value="">Select Item</option>
                    {filteredInvForAudit.map(inv => (
                      <option key={inv.id} value={inv.id}>{getProductName(inv.product_id)} ({getProductSku(inv.product_id)})</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Physical Count Quantity</label>
                  <input
                    required
                    type="number"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={countForm.physical_qty}
                    onChange={e => setCountForm(prev => ({ ...prev, physical_qty: e.target.value }))}
                  />
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCountModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Count</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
