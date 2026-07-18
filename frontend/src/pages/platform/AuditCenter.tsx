import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { AuditEvent } from '../../types/platform';

export const AuditCenter: React.FC = () => {
  const { accessToken } = useAuth();
  const [logs, setLogs] = useState<AuditEvent[]>([]);
  const [filterSource, setFilterSource] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const url = filterSource ? `/api/v1/audit?source=${filterSource}` : '/api/v1/audit';
      const res = await fetch(url, { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setLogs(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchLogs();
    }
  }, [accessToken, filterSource]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Security Audit Timeline
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Centralized timeline database recording operational transactions, client IP headers, and browser metadata.
          </p>
        </div>
      </div>

      {/* Filter Source toggles */}
      <div className="flex space-x-3 text-xs">
        {['', 'API', 'SCHEDULER', 'WORKFLOW', 'AI', 'MANUAL'].map(src => (
          <button
            key={src}
            onClick={() => setFilterSource(src)}
            className={`px-3.5 py-2 rounded-lg border font-semibold transition ${
              filterSource === src
                ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
                : 'bg-card text-muted-foreground border-neutral-800 hover:text-white'
            }`}
          >
            {src === '' ? 'ALL SOURCES' : src}
          </button>
        ))}
      </div>

      {/* Timeline list */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No audit logs matching this operational source category.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Source</th>
                <th className="px-6 py-4">Operation</th>
                <th className="px-6 py-4">Target Entity</th>
                <th className="px-6 py-4">IP Address</th>
                <th className="px-6 py-4">Browser Client</th>
                <th className="px-6 py-4 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {logs.map(log => (
                <tr key={log.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4">
                    <span className="px-1.5 py-0.5 bg-neutral-800 border border-neutral-700 rounded text-[9px] font-mono text-neutral-300">
                      {log.source}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-neutral-300 font-bold">{log.operation}</td>
                  <td className="px-6 py-4 text-neutral-300 font-mono text-[10px]">
                    {log.entity_name} ({log.entity_id.substring(0, 8)})
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-400">{log.ip_address || '127.0.0.1'}</td>
                  <td className="px-6 py-4 text-neutral-400 max-w-xs truncate text-[10px]">{log.browser || 'Postman Runtime'}</td>
                  <td className="px-6 py-4 text-right text-neutral-400 font-mono text-[10px]">
                    {new Date(log.created_at).toLocaleString()}
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
