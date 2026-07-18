import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Product, ProductCategory } from '../../types/inventory';
import { Search, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const ProductCatalog: React.FC = () => {
  const { accessToken } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Search & Filter state
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [creationDrawer, setCreationDrawer] = useState(false);

  // Creation form state
  const [newProduct, setNewProduct] = useState({
    sku: '', barcode: '', name: '', brand: '',
    cost_price: '', selling_price: '', category_id: '',
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const pRes = await fetch('/api/v1/products', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const cRes = await fetch('/api/v1/products/categories', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (pRes.ok) setProducts(await pRes.json());
      if (cRes.ok) setCategories(await cRes.json());
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

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/products', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          sku: newProduct.sku,
          barcode: newProduct.barcode,
          name: newProduct.name,
          brand: newProduct.brand,
          cost_price: parseFloat(newProduct.cost_price),
          selling_price: parseFloat(newProduct.selling_price),
          category_id: newProduct.category_id || undefined,
        })
      });
      if (res.ok) {
        setCreationDrawer(false);
        setNewProduct({ sku: '', barcode: '', name: '', brand: '', cost_price: '', selling_price: '', category_id: '' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const filteredProducts = products.filter(p => {
    const matchSearch = p.name.toLowerCase().includes(search.toLowerCase()) || p.sku.toLowerCase().includes(search.toLowerCase());
    const matchCategory = categoryFilter ? p.category_id === categoryFilter : true;
    return matchSearch && matchCategory;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Product Catalog
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Manage your global retail inventory products, variants, brands, and price points.
          </p>
        </div>

        <button
          onClick={() => setCreationDrawer(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Add Product
        </button>
      </div>

      {/* Filter panel */}
      <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative col-span-2">
            <input
              placeholder="Search by product name, SKU..."
              className="w-full pl-10 pr-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          </div>

          <select
            className="w-full px-4 py-2.5 bg-secondary text-white border border-border rounded-lg text-sm focus:outline-none focus:ring-2"
            value={categoryFilter}
            onChange={e => setCategoryFilter(e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
          </select>
        </div>
      </div>

      {/* Product Catalog Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => <div key={i} className="h-48 w-full animate-pulse bg-neutral-800/40 rounded-2xl" />)}
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No products registered in catalog.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map(p => {
            const primaryImg = p.images?.find(img => img.is_primary)?.image_url || 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=500';
            return (
              <div 
                key={p.id} 
                className="glass-card rounded-2xl overflow-hidden border border-neutral-800 hover:border-neutral-700 transition flex flex-col justify-between h-80 bg-card/40"
              >
                <div className="h-36 overflow-hidden relative">
                  <img src={primaryImg} alt={p.name} className="w-full h-full object-cover" />
                  <span className="absolute top-3 right-3 px-2 py-0.5 rounded bg-black/60 text-white font-mono text-[9px] uppercase border border-white/10">
                    {p.brand || 'General'}
                  </span>
                </div>

                <div className="p-4 flex-grow flex flex-col justify-between">
                  <div>
                    <h3 className="font-bold text-white text-xs truncate">{p.name}</h3>
                    <span className="text-[10px] text-muted-foreground font-mono mt-0.5 block">{p.sku}</span>
                  </div>

                  <div className="flex justify-between items-center pt-3 border-t border-border/40 text-xs">
                    <div>
                      <span className="text-muted-foreground block text-[9px] uppercase font-semibold">Cost / Sale</span>
                      <span className="text-white font-semibold font-mono">${p.cost_price} / ${p.selling_price}</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                      p.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
                    }`}>
                      {p.status}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Product Creation Drawer */}
      <AnimatePresence>
        {creationDrawer && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setCreationDrawer(false)} />
            <motion.aside
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              className="fixed inset-y-0 right-0 w-full max-w-md bg-card border-l border-border p-8 z-50 overflow-y-auto"
            >
              <h2 className="text-lg font-bold text-white mb-6">Create Catalog Product</h2>
              <form onSubmit={handleCreateProduct} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground uppercase font-semibold text-[10px] mb-1.5">SKU Code (Unique)</label>
                  <input
                    required
                    className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={newProduct.sku}
                    onChange={e => setNewProduct(prev => ({ ...prev, sku: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-muted-foreground uppercase font-semibold text-[10px] mb-1.5">Barcode</label>
                  <input
                    className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={newProduct.barcode}
                    onChange={e => setNewProduct(prev => ({ ...prev, barcode: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-muted-foreground uppercase font-semibold text-[10px] mb-1.5">Product Name</label>
                  <input
                    required
                    className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={newProduct.name}
                    onChange={e => setNewProduct(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-muted-foreground uppercase font-semibold text-[10px] mb-1.5">Brand</label>
                  <input
                    className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={newProduct.brand}
                    onChange={e => setNewProduct(prev => ({ ...prev, brand: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground uppercase font-semibold text-[10px] mb-1.5">Cost Price</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={newProduct.cost_price}
                      onChange={e => setNewProduct(prev => ({ ...prev, cost_price: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground uppercase font-semibold text-[10px] mb-1.5">Selling Price</label>
                    <input
                      required
                      type="number"
                      className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={newProduct.selling_price}
                      onChange={e => setNewProduct(prev => ({ ...prev, selling_price: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground uppercase font-semibold text-[10px] mb-1.5">Category</label>
                  <select
                    className="w-full px-3 py-2.5 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={newProduct.category_id}
                    onChange={e => setNewProduct(prev => ({ ...prev, category_id: e.target.value }))}
                  >
                    <option value="">Select Category</option>
                    {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                  </select>
                </div>

                <div className="flex space-x-3 pt-6 border-t border-border/40">
                  <button type="button" onClick={() => setCreationDrawer(false)} className="w-1/2 py-2.5 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2.5 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Product</button>
                </div>
              </form>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
