import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { ToolDefinition } from '../../types/ai';
import { ShieldCheck } from 'lucide-react';

export const ModelManager: React.FC = () => {
  const { accessToken } = useAuth();
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTools = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/ai/tools', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setTools(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) fetchTools();
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          AI Tools Registry & Model Configs
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Dynamic Tool registry advertising input schemas, timeouts, and required RBAC permission checks.
        </p>
      </div>

      {/* Model Providers summary */}
      <div className="p-5 bg-card border border-neutral-800 rounded-2xl text-xs space-y-2">
        <span className="font-bold text-white uppercase text-[10px] block">Active Provider</span>
        <div className="flex items-center justify-between">
          <span className="font-mono text-neutral-300">OPENAI (gpt-4o)</span>
          <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
            DEFAULT ACTIVE
          </span>
        </div>
      </div>

      {/* Tools Table list */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : tools.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No dynamic tools registered.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Tool Name</th>
                <th className="px-6 py-4">Required Permissions</th>
                <th className="px-6 py-4">Description</th>
                <th className="px-6 py-4 text-right">Input Schema</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {tools.map(t => (
                <tr key={t.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4 font-mono font-bold text-indigo-400">{t.name}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-neutral-800 border border-neutral-700 rounded text-[9px] font-mono text-neutral-300">
                      <ShieldCheck size={10} className="text-emerald-400" />
                      {t.required_permissions}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-neutral-300 max-w-sm truncate">{t.description}</td>
                  <td className="px-6 py-4 text-right font-mono text-[9px] text-neutral-500">
                    {JSON.stringify(t.input_schema)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
