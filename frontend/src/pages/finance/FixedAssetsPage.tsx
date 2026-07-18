import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Asset } from '../../types/finance';
import { Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const FixedAssetsPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Form states
  const [creationModal, setCreationModal] = useState(false);
  const [name, setName] = useState('');
  const [category, setCategory] = useState('MACHINERY');
  const [purchaseDate, setPurchaseDate] = useState(new Date().toISOString().split('T')[0]);
  const [purchaseValue, setPurchaseValue] = useState('');
  const [residualValue, setResidualValue] = useState('0');
  const [usefulLife, setUsefulLife] = useState('36');
  const [assetAcc, setAssetAcc] = useState('');
  const [depAcc, setDepAcc] = useState('');

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const aRes = await fetch('/api/v1/assets', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const accRes = await fetch('/api/v1/accounts', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (aRes.ok) setAssets(await aRes.json());
      if (accRes.ok) {
        const accs = await accRes.json();
        const firstAssetAcc = accs.find((a: any) => a.code.startsWith('16'));
        const firstDepAcc = accs.find((a: any) => a.code.startsWith('55'));
        if (firstAssetAcc) setAssetAcc(firstAssetAcc.id);
        if (firstDepAcc) setDepAcc(firstDepAcc.id);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/assets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          name,
          category,
          purchase_date: purchaseDate,
          purchase_value: parseFloat(purchaseValue),
          residual_value: parseFloat(residualValue),
          useful_life_months: parseInt(usefulLife),
          asset_account_id: assetAcc,
          depreciation_account_id: depAcc
        })
      });
      if (res.ok) {
        setCreationModal(false);
        setName('');
        setPurchaseValue('');
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const triggerDepreciation = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/assets/${id}/depreciate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        alert('Depreciation posted successfully in Ledger!');
        fetchData();
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
            Fixed Asset Registry
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Register capitalized company assets and execute monthly straight-line depreciation calculations.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Capitalize Asset
        </button>
      </div>

      {/* Assets Grid list */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : assets.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No capitalized fixed assets registered.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Asset #</th>
                <th className="px-6 py-4">Asset Name</th>
                <th className="px-6 py-4">Purchase Date</th>
                <th className="px-6 py-4">Capitalized Value</th>
                <th className="px-6 py-4">Useful Life</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {assets.map(asset => (
                <tr key={asset.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4 font-mono font-bold text-neutral-300">
                    {asset.asset_number}
                  </td>
                  <td className="px-6 py-4 text-neutral-300">{asset.name}</td>
                  <td className="px-6 py-4 text-neutral-300">{asset.purchase_date}</td>
                  <td className="px-6 py-4 font-mono">${asset.purchase_value.toLocaleString()}</td>
                  <td className="px-6 py-4 text-neutral-300">{asset.useful_life_months} Months</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                      {asset.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {asset.status === 'ACTIVE' && (
                      <button
                        onClick={() => triggerDepreciation(asset.id)}
                        className="px-2.5 py-1 bg-white text-black hover:bg-neutral-200 rounded text-[10px] font-bold"
                      >
                        Run Depreciation
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
              <h2 className="text-base font-bold text-white mb-4">Capitalize Fixed Asset</h2>
              <form onSubmit={handleSubmit} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Asset Name</label>
                  <input
                    required
                    placeholder="e.g. Delivery Truck Model F"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={name}
                    onChange={e => setName(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Category</label>
                    <select
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={category}
                      onChange={e => setCategory(e.target.value)}
                    >
                      <option value="MACHINERY">MACHINERY</option>
                      <option value="VEHICLES">VEHICLES</option>
                      <option value="OFFICE_EQUIPMENT">OFFICE EQUIPMENT</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Purchase Date</label>
                    <input
                      type="date"
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={purchaseDate}
                      onChange={e => setPurchaseDate(e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Value ($)</label>
                    <input
                      type="number"
                      required
                      placeholder="0"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={purchaseValue}
                      onChange={e => setPurchaseValue(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Residual ($)</label>
                    <input
                      type="number"
                      placeholder="0"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={residualValue}
                      onChange={e => setResidualValue(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Life (Months)</label>
                    <input
                      type="number"
                      required
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={usefulLife}
                      onChange={e => setUsefulLife(e.target.value)}
                    />
                  </div>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Register Asset</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
