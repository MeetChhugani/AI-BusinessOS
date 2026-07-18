import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Building2, AlertTriangle, ArrowUpRight, TrendingUp, 
  ShoppingBag, ClipboardCheck 
} from 'lucide-react';
import { Link } from 'react-router-dom';

interface LowStockAlert {
  warehouse: string;
  product: string;
  sku: string;
  available: number;
  reorder_level: number;
  reorder_qty: number;
}

export const WarehouseDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [valuation, setValuation] = useState<number>(0);
  const [lowStock, setLowStock] = useState<LowStockAlert[]>([]);
  const [warehouseStats, setWarehouseStats] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const valRes = await fetch('/api/v1/inventory/valuation', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const lowRes = await fetch('/api/v1/inventory/low-stock', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const whRes = await fetch('/api/v1/warehouses/stats', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (valRes.ok) {
        const valData = await valRes.json();
        setValuation(valData.valuation || 0.0);
      }
      if (lowRes.ok) setLowStock(await lowRes.json());
      if (whRes.ok) setWarehouseStats(await whRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchDashboardData();
    }
  }, [accessToken]);

  if (isLoading) {
    return <div className="h-64 animate-pulse bg-neutral-800/40 rounded-2xl" />;
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Inventory Command Hub
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Real-time metrics, capacity limits, low stock alerts, and warehouse operations.
        </p>
      </div>

      {/* Aggregate metrics grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Inventory Value</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 text-emerald-400">
              <TrendingUp size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">
              ${valuation.toLocaleString()}
            </span>
            <span className="text-[10px] text-muted-foreground">Valued at actual cost price</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Low Stock Items</span>
            <div className="w-8 h-8 rounded-lg bg-yellow-500/10 flex items-center justify-center border border-yellow-500/20 text-yellow-400">
              <AlertTriangle size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">{lowStock.length}</span>
            <span className="text-[10px] text-muted-foreground">Alerts requiring replenishment</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Purchase Orders</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20 text-blue-400">
              <ShoppingBag size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">1</span>
            <span className="text-[10px] text-muted-foreground">Active in-flight orders</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Active Audits</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400">
              <ClipboardCheck size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">0</span>
            <span className="text-[10px] text-muted-foreground">Cycle count operations running</span>
          </div>
        </div>
      </div>

      {/* Warehouse capacities and low stock alerts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Warehouse utilization stats */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-neutral-800 space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Building2 size={16} className="text-muted-foreground" />
            Warehouse Capacities
          </h3>
          <div className="space-y-4">
            {warehouseStats.map(wh => (
              <div key={wh.id} className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <div>
                    <span className="text-white font-semibold block">{wh.name}</span>
                    <span className="text-[10px] text-muted-foreground font-mono">{wh.code}</span>
                  </div>
                  <span className="text-white font-mono">{wh.utilization}% ({wh.total_items} / {wh.capacity} m³)</span>
                </div>
                <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${wh.utilization > 85 ? 'bg-red-500' : 'bg-blue-500'}`} 
                    style={{ width: `${Math.min(100, wh.utilization)}%` }} 
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Low Stock Alerts */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between">
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle size={16} className="text-yellow-500" />
              Low Stock Warnings
            </h3>
            {lowStock.length === 0 ? (
              <p className="text-xs text-muted-foreground">All items currently above safety margins.</p>
            ) : (
              <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
                {lowStock.map((alert, idx) => (
                  <div key={idx} className="flex justify-between items-center text-xs border-b border-border/40 pb-2.5 last:border-0">
                    <div>
                      <span className="text-white font-semibold block">{alert.product}</span>
                      <span className="text-[9px] text-muted-foreground font-mono">SKU: {alert.sku} | Wh: {alert.warehouse}</span>
                    </div>
                    <span className="text-red-400 font-bold font-mono bg-red-500/10 px-2 py-0.5 rounded border border-red-500/15">
                      {alert.available} qty
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <Link to="/dashboard/hcm" className="w-full text-center py-2.5 bg-secondary hover:bg-neutral-850 text-white border border-border/40 rounded-xl text-xs transition mt-6 block">
            Replenish Items (PO Panel) →
          </Link>
        </div>
      </div>

      {/* Shortcuts grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <Link to="/dashboard/hcm/org" className="glass-card rounded-2xl p-6 border border-neutral-800 flex justify-between items-center hover:border-neutral-750 transition text-xs">
          <div>
            <span className="font-semibold text-white block">Stock Directories</span>
            <span className="text-muted-foreground block mt-1">Manage balances, adjustments</span>
          </div>
          <ArrowUpRight size={16} className="text-muted-foreground" />
        </Link>
        <Link to="/dashboard/hcm/pipeline" className="glass-card rounded-2xl p-6 border border-neutral-800 flex justify-between items-center hover:border-neutral-750 transition text-xs">
          <div>
            <span className="font-semibold text-white block">Product Catalog</span>
            <span className="text-muted-foreground block mt-1">Configure brand margins & SKU attributes</span>
          </div>
          <ArrowUpRight size={16} className="text-muted-foreground" />
        </Link>
        <Link to="/dashboard/hcm/leaves" className="glass-card rounded-2xl p-6 border border-neutral-800 flex justify-between items-center hover:border-neutral-750 transition text-xs">
          <div>
            <span className="font-semibold text-white block">Suppliers Hub</span>
            <span className="text-muted-foreground block mt-1">Check rating scores & payment terms</span>
          </div>
          <ArrowUpRight size={16} className="text-muted-foreground" />
        </Link>
      </div>
    </div>
  );
};
