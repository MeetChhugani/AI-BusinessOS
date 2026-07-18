import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { WorkflowDefinition } from '../../types/platform';
import { Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const WorkflowBuilder: React.FC = () => {
  const { accessToken } = useAuth();
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Form states
  const [creationModal, setCreationModal] = useState(false);
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');

  // TCA states
  const [triggerType, setTriggerType] = useState('EVENT_DRIVEN');
  const [eventName, setEventName] = useState('LOW_STOCK_ALERT');
  
  const [condField, setCondField] = useState('quantity');
  const [condOp, setCondOp] = useState('LT');
  const [condVal, setCondVal] = useState('safety_stock');

  const [actType, setActType] = useState('NOTIFY');
  const [actMsg, setActMsg] = useState('Inventory Alert: Quantity dropped!');

  const fetchWorkflows = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/workflows', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setWorkflows(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchWorkflows();
    }
  }, [accessToken]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        name,
        code,
        description,
        triggers: [
          { trigger_type: triggerType, event_name: eventName }
        ],
        conditions: [
          { operator: 'AND', expression: { field: condField, op: condOp, value: condVal } }
        ],
        actions: [
          { action_type: actType, parameters: { message: actMsg, user_id: '00000000-0000-0000-0000-000000000000' } }
        ]
      };

      const res = await fetch('/api/v1/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setCreationModal(false);
        setName('');
        setCode('');
        setDescription('');
        fetchWorkflows();
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
            Low-Code Workflow Engine
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Configure dynamic triggers, logical criteria, and sequences to automate notifications or API executions.
          </p>
        </div>

        <button
          onClick={() => setCreationModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Plus size={14} className="mr-2" />
          Add Workflow
        </button>
      </div>

      {/* Rules list */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : workflows.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No workflow rules created yet.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Rule Code</th>
                <th className="px-6 py-4">Workflow Name</th>
                <th className="px-6 py-4">Version</th>
                <th className="px-6 py-4">Description</th>
                <th className="px-6 py-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {workflows.map(wf => (
                <tr key={wf.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4 font-mono font-bold text-neutral-300">{wf.code}</td>
                  <td className="px-6 py-4 text-neutral-300">{wf.name}</td>
                  <td className="px-6 py-4 font-mono text-neutral-400">v{wf.version}</td>
                  <td className="px-6 py-4 text-neutral-400 max-w-xs truncate">{wf.description}</td>
                  <td className="px-6 py-4 text-right">
                    <span className="px-2 py-0.5 rounded text-[8px] font-bold border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                      {wf.status}
                    </span>
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
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl overflow-y-auto max-h-[90vh]"
            >
              <h2 className="text-base font-bold text-white mb-4">Add Workflow Rule</h2>
              <form onSubmit={handleSubmit} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Rule Code</label>
                    <input
                      required
                      placeholder="e.g. INV_APPROVE"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={code}
                      onChange={e => setCode(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Workflow Name</label>
                    <input
                      required
                      placeholder="e.g. Low Stock Reorder"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={name}
                      onChange={e => setName(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Description</label>
                  <input
                    placeholder="Provide memo explanation"
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                  />
                </div>

                {/* Trigger Criteria */}
                <div className="p-4 bg-secondary/35 border border-border/40 rounded-xl space-y-3">
                  <span className="uppercase text-[9px] font-bold text-indigo-400 block">Trigger Criteria</span>
                  <div className="grid grid-cols-2 gap-3">
                    <select
                      className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={triggerType}
                      onChange={e => setTriggerType(e.target.value)}
                    >
                      <option value="EVENT_DRIVEN">EVENT DRIVEN</option>
                      <option value="TIME_BASED">TIME BASED</option>
                    </select>
                    <input
                      required
                      className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      placeholder="Event name (e.g. LOW_STOCK)"
                      value={eventName}
                      onChange={e => setEventName(e.target.value)}
                    />
                  </div>
                </div>

                {/* Condition Criteria */}
                <div className="p-4 bg-secondary/35 border border-border/40 rounded-xl space-y-3">
                  <span className="uppercase text-[9px] font-bold text-indigo-400 block">Logical Condition</span>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      placeholder="Field (e.g. qty)"
                      className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={condField}
                      onChange={e => setCondField(e.target.value)}
                    />
                    <select
                      className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={condOp}
                      onChange={e => setCondOp(e.target.value)}
                    >
                      <option value="LT">LESS THAN</option>
                      <option value="GT">GREATER THAN</option>
                      <option value="EQ">EQUAL TO</option>
                    </select>
                    <input
                      placeholder="Value"
                      className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={condVal}
                      onChange={e => setCondVal(e.target.value)}
                    />
                  </div>
                </div>

                {/* Action Output */}
                <div className="p-4 bg-secondary/35 border border-border/40 rounded-xl space-y-3">
                  <span className="uppercase text-[9px] font-bold text-indigo-400 block">Workflow Action</span>
                  <div className="grid grid-cols-2 gap-3">
                    <select
                      className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={actType}
                      onChange={e => setActType(e.target.value)}
                    >
                      <option value="NOTIFY">IN-APP ALERT</option>
                      <option value="SEND_EMAIL">SEND EMAIL</option>
                    </select>
                    <input
                      placeholder="Action payload value"
                      className="px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={actMsg}
                      onChange={e => setActMsg(e.target.value)}
                    />
                  </div>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setCreationModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Establish Rule</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
