import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { AgentExecution } from '../../types/ai';

export const AgentCenter: React.FC = () => {
  const { accessToken } = useAuth();
  const [executions, setExecutions] = useState<AgentExecution[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTraces = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/ai/agents/executions', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setExecutions(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) fetchTraces();
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Supervisor Agent Execution Logs
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Review dynamic planning steps, active tools duration logs, inputs schemas, and computed confidence evaluations.
        </p>
      </div>

      {/* Execution logs table */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : executions.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No supervisor agent runs logged yet. Chat with the Copilot to trigger audits.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Tool Used</th>
                <th className="px-6 py-4">Duration</th>
                <th className="px-6 py-4">Inputs Payload</th>
                <th className="px-6 py-4">Outputs Payload</th>
                <th className="px-6 py-4">Confidence</th>
                <th className="px-6 py-4 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {executions.map(ex => (
                <tr key={ex.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4">
                    <span className="px-1.5 py-0.5 bg-neutral-800 border border-neutral-700 rounded text-[9px] font-mono text-neutral-300">
                      {ex.tool_used || 'None'}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-300">{ex.duration_ms} ms</td>
                  <td className="px-6 py-4 text-neutral-400 max-w-xs truncate font-mono text-[10px]" title={JSON.stringify(ex.inputs_payload)}>
                    {JSON.stringify(ex.inputs_payload)}
                  </td>
                  <td className="px-6 py-4 text-neutral-400 max-w-xs truncate font-mono text-[10px]" title={JSON.stringify(ex.outputs_payload)}>
                    {JSON.stringify(ex.outputs_payload)}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                      {ex.confidence}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right text-neutral-400 font-mono text-[10px]">
                    {new Date(ex.created_at).toLocaleString()}
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
