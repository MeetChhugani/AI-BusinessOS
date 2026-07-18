import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { SearchIndex } from '../../types/platform';
import { Search, Compass } from 'lucide-react';

export const SearchCenter: React.FC = () => {
  const { accessToken } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchIndex[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim().length < 2) return;

    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/search?q=${query}`, { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setResults(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-10">
      {/* Central Input Search Form */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold font-display tracking-tight text-white">
          Unified Platform Search
        </h1>
        <p className="text-sm text-muted-foreground">
          Find matching profiles, orders, inventory lines, or journal entries across all BusinessOS modules.
        </p>
      </div>

      <form onSubmit={handleSearch} className="relative">
        <input
          required
          placeholder="Type keywords (e.g. laptop, Initech, Marcus)..."
          className="w-full px-5 py-4 pl-12 bg-card border border-neutral-800 rounded-2xl text-white text-sm focus:outline-none focus:border-indigo-500 transition shadow-lg"
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
      </form>

      {/* Results grid */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2].map(i => <div key={i} className="h-16 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : results.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground text-xs flex flex-col items-center gap-2">
          <Compass size={24} className="text-neutral-600" />
          No results index matches. Try another keyword search query.
        </div>
      ) : (
        <div className="space-y-3">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
            Search Matches ({results.length})
          </span>
          {results.map(row => (
            <div key={row.id} className="p-4 bg-secondary/35 border border-border/40 rounded-2xl flex justify-between items-center hover:bg-secondary/60 transition">
              <div>
                <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-indigo-500/10 text-indigo-400 border-indigo-500/20 mr-2 uppercase inline-block">
                  {row.entity_type}
                </span>
                <span className="text-xs font-bold text-white inline-block">{row.title}</span>
                <span className="text-muted-foreground text-[10px] block mt-1">{row.description}</span>
              </div>
              <div className="text-right">
                <span className="font-mono text-[9px] text-neutral-500 block">ID: {row.entity_id.substring(0, 8)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
