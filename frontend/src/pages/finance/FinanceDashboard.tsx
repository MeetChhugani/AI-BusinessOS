import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  PiggyBank, ShoppingCart, ArrowUpRight, Landmark, Layers, TrendingUp 
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const FinanceDashboard: React.FC = () => {
  const { accessToken } = useAuth();
  const [cashBalance, setCashBalance] = useState<number>(0);
  const [arVal, setArVal] = useState<number>(0);
  const [apVal, setApVal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);

  // Automation rules list
  const automationRules = [
    { trigger: 'Invoice Created', condition: 'Total Amount > $100,000', action: 'Require CFO Approval', active: true },
    { trigger: 'Inventory Dropped', condition: 'Quantity < Safety Stock', action: 'Create Purchase Request', active: true },
    { trigger: 'Customer Balance Overdue', condition: 'Overdue > 60 Days', action: 'Freeze Customer Order', active: false }
  ];

  const fetchBalances = async () => {
    setIsLoading(true);
    try {
      const accRes = await fetch('/api/v1/accounts', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (accRes.ok) {
        const accounts = await accRes.json();
        const cashAcc = accounts.find((a: any) => a.code === '1000');
        const arAcc = accounts.find((a: any) => a.code === '1200');
        const apAcc = accounts.find((a: any) => a.code === '2000');

        if (cashAcc) setCashBalance(parseFloat(cashAcc.current_balance));
        if (arAcc) setArVal(parseFloat(arAcc.current_balance));
        if (apAcc) setApVal(parseFloat(apAcc.current_balance));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchBalances();
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
          Financial Control Center
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          General ledger accounting, cash liquidity ratios, accounts receivable, and automated approval parameters.
        </p>
      </div>

      {/* Stats Indicators Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Cash & bank balance</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400">
              <Landmark size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">${cashBalance.toLocaleString()}</span>
            <span className="text-[10px] text-muted-foreground">GL account: 1000 Cash Equivalents</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Accounts Receivable</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 text-emerald-400">
              <PiggyBank size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">${arVal.toLocaleString()}</span>
            <span className="text-[10px] text-muted-foreground">Outstanding customer invoices</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Accounts Payable</span>
            <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center border border-red-500/20 text-red-400">
              <ShoppingCart size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">${apVal.toLocaleString()}</span>
            <span className="text-[10px] text-muted-foreground">Unpaid vendor bills</span>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between h-36 bg-card/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Gross Profit Margin</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400">
              <TrendingUp size={16} />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold text-white block">34.8%</span>
            <span className="text-[10px] text-muted-foreground">FY-2026 Profitability index</span>
          </div>
        </div>
      </div>

      {/* Split Details View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workflow Automation Rules */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Layers size={16} className="text-muted-foreground" />
            Workflow Automation Engine
          </h3>
          <div className="space-y-3">
            {automationRules.map((rule, idx) => (
              <div key={idx} className="p-4 bg-secondary/35 border border-border/60 rounded-xl flex justify-between items-center text-xs">
                <div>
                  <span className="font-bold text-white block">If: {rule.trigger}</span>
                  <span className="text-muted-foreground text-[10px] mt-0.5 block">Condition: {rule.condition}</span>
                </div>
                <div className="text-right">
                  <span className="font-semibold text-indigo-400 block">{rule.action}</span>
                  <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded border inline-block mt-1 ${
                    rule.active ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/15' : 'bg-neutral-800 text-neutral-500 border-neutral-700'
                  }`}>
                    {rule.active ? 'ACTIVE' : 'INACTIVE'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Links */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 flex flex-col justify-between">
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Quick Shortcuts
            </h3>
            <div className="space-y-2.5 text-xs">
              <Link to="/dashboard/finance/accounts" className="flex justify-between items-center p-2.5 bg-secondary/30 hover:bg-secondary/65 border border-border/40 rounded-xl text-white transition">
                <span>Chart of Accounts</span>
                <ArrowUpRight size={14} className="text-muted-foreground" />
              </Link>
              <Link to="/dashboard/finance/journal" className="flex justify-between items-center p-2.5 bg-secondary/30 hover:bg-secondary/65 border border-border/40 rounded-xl text-white transition">
                <span>Post Journal Lines</span>
                <ArrowUpRight size={14} className="text-muted-foreground" />
              </Link>
              <Link to="/dashboard/finance/reconciliation" className="flex justify-between items-center p-2.5 bg-secondary/30 hover:bg-secondary/65 border border-border/40 rounded-xl text-white transition">
                <span>Bank Statement Sync</span>
                <ArrowUpRight size={14} className="text-muted-foreground" />
              </Link>
              <Link to="/dashboard/finance/reports" className="flex justify-between items-center p-2.5 bg-secondary/30 hover:bg-secondary/65 border border-border/40 rounded-xl text-white transition">
                <span>Financial Reports</span>
                <ArrowUpRight size={14} className="text-muted-foreground" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
