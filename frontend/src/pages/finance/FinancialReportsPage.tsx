import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { BarChart3 } from 'lucide-react';

export const FinancialReportsPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [tbData, setTbData] = useState<any[]>([]);
  const [plData, setPlData] = useState<any>(null);
  const [activeReport, setActiveReport] = useState<'tb' | 'pl'>('tb');
  const [isLoading, setIsLoading] = useState(true);

  const fetchReports = async () => {
    setIsLoading(true);
    try {
      const tbRes = await fetch('/api/v1/reports/trial-balance', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const plRes = await fetch('/api/v1/reports/profit-loss', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (tbRes.ok) setTbData(await tbRes.json());
      if (plRes.ok) setPlData(await plRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchReports();
    }
  }, [accessToken]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Financial Statements & Reporting
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Generate real-time Trial Balance logs and Profit & Loss (Income Statement) structures.
        </p>
      </div>

      {/* Selector Tabs */}
      <div className="flex border-b border-neutral-800">
        <button
          onClick={() => setActiveReport('tb')}
          className={`px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 transition ${
            activeReport === 'tb' ? 'border-indigo-500 text-white' : 'border-transparent text-muted-foreground hover:text-white'
          }`}
        >
          Trial Balance
        </button>
        <button
          onClick={() => setActiveReport('pl')}
          className={`px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 transition ${
            activeReport === 'pl' ? 'border-indigo-500 text-white' : 'border-transparent text-muted-foreground hover:text-white'
          }`}
        >
          Profit & Loss Statement
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : activeReport === 'tb' ? (
        // TRIAL BALANCE VIEW
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Account Code</th>
                <th className="px-6 py-4">Account Name</th>
                <th className="px-6 py-4">Classification</th>
                <th className="px-6 py-4 text-right">Debit ($)</th>
                <th className="px-6 py-4 text-right">Credit ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {tbData.map((row, idx) => (
                <tr key={idx} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4 font-mono text-neutral-300">{row.code}</td>
                  <td className="px-6 py-4 text-neutral-300">{row.name}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                      {row.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right font-mono text-emerald-400">
                    {row.debit > 0 ? `$${row.debit.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : '-'}
                  </td>
                  <td className="px-6 py-4 text-right font-mono text-indigo-400">
                    {row.credit > 0 ? `$${row.credit.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        // PROFIT & LOSS VIEW
        plData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <BarChart3 size={16} className="text-muted-foreground" />
                Income Statement Breakdown
              </h3>

              <div className="space-y-3 text-xs">
                <div className="flex justify-between items-center p-3 bg-emerald-500/5 border border-emerald-500/10 rounded-xl">
                  <span className="font-bold text-emerald-400 uppercase tracking-wider">Total Sales Revenue</span>
                  <span className="font-mono text-emerald-400 font-bold">${plData.total_revenue.toLocaleString()}</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-red-500/5 border border-red-500/10 rounded-xl">
                  <span className="font-bold text-red-400 uppercase tracking-wider">Total Operating Expenses</span>
                  <span className="font-mono text-red-400 font-bold">${plData.total_expenses.toLocaleString()}</span>
                </div>

                <div className="flex justify-between items-center p-3 bg-indigo-500/5 border border-indigo-500/10 rounded-xl">
                  <span className="font-bold text-white uppercase tracking-wider">Net Operating Income</span>
                  <span className="font-mono text-indigo-400 font-bold font-display text-sm">${plData.net_income.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Account Breakdown</h3>
              <div className="space-y-2 text-xs">
                {plData.breakdown.map((item: any, idx: number) => (
                  <div key={idx} className="flex justify-between items-center py-2 border-b border-border/30">
                    <span className="text-muted-foreground">{item.code} - {item.name}</span>
                    <span className={`font-mono ${item.amount < 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                      ${Math.abs(item.amount).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )
      )}
    </div>
  );
};
