import React, { useState, useEffect } from 'react';
import { Employee, OnboardingStatus } from '../../types/hcm';
import { useAuth } from '../../contexts/AuthContext';
import { ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const ONBOARDING_COLUMNS: { key: OnboardingStatus; label: string; color: string }[] = [
  { key: 'DRAFT', label: 'Draft', color: 'border-t-neutral-600 bg-neutral-600/5' },
  { key: 'OFFER_SENT', label: 'Offer Sent', color: 'border-t-blue-500 bg-blue-500/5' },
  { key: 'OFFER_ACCEPTED', label: 'Offer Accepted', color: 'border-t-indigo-500 bg-indigo-500/5' },
  { key: 'DOCUMENTS_PENDING', label: 'Docs Pending', color: 'border-t-yellow-500 bg-yellow-500/5' },
  { key: 'DOCUMENTS_VERIFIED', label: 'Docs Verified', color: 'border-t-teal-500 bg-teal-500/5' },
  { key: 'IT_ACCOUNT_CREATED', label: 'IT Setup', color: 'border-t-purple-500 bg-purple-500/5' },
  { key: 'ONBOARDING_COMPLETE', label: 'Complete', color: 'border-t-emerald-500 bg-emerald-500/5' },
];

export const OnboardingPipeline: React.FC = () => {
  const { accessToken } = useAuth();
  const [candidates, setCandidates] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCandidates = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/employees?limit=100', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCandidates(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchCandidates();
    }
  }, [accessToken]);

  const advanceStage = async (id: string, currentStage: OnboardingStatus) => {
    const stageFlow: OnboardingStatus[] = [
      'DRAFT', 'OFFER_SENT', 'OFFER_ACCEPTED', 
      'DOCUMENTS_PENDING', 'DOCUMENTS_VERIFIED', 
      'IT_ACCOUNT_CREATED', 'ONBOARDING_COMPLETE'
    ];
    const currentIndex = stageFlow.indexOf(currentStage);
    if (currentIndex === -1 || currentIndex === stageFlow.length - 1) return;
    
    const nextStage = stageFlow[currentIndex + 1];
    
    // Update backend status
    const res = await fetch(`/api/v1/employees/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({ onboarding_status: nextStage })
    });
    
    if (res.ok) {
      // Add timeline log event triggers on backend automatically, refetch locally
      fetchCandidates();
    }
  };

  return (
    <div className="space-y-6 w-full max-w-7xl mx-auto overflow-hidden">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Employee Onboarding Pipeline
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Orchestrate recruitment offers, document verification, and IT setup steps.
        </p>
      </div>

      {isLoading ? (
        <div className="h-64 animate-pulse bg-neutral-800/40 rounded-2xl" />
      ) : (
        <div className="flex space-x-4 overflow-x-auto pb-6 scrollbar-thin">
          {ONBOARDING_COLUMNS.map(col => {
            const columnCandidates = candidates.filter(c => c.onboarding_status === col.key);
            
            return (
              <div 
                key={col.key} 
                className="w-72 shrink-0 flex flex-col min-h-[500px] rounded-2xl border border-neutral-800/60 bg-card p-4 relative"
              >
                {/* Column header */}
                <div className={`border-t-2 ${col.color} pt-2.5 pb-4 flex justify-between items-center`}>
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">{col.label}</h3>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-neutral-900 border border-neutral-850 text-neutral-400">
                    {columnCandidates.length}
                  </span>
                </div>

                {/* Column Card Lists */}
                <div className="flex-grow space-y-4 overflow-y-auto">
                  {columnCandidates.map(c => (
                    <motion.div 
                      key={c.id}
                      whileHover={{ y: -2 }}
                      className="glass-card rounded-xl p-4 border border-neutral-800 bg-card/60 relative flex flex-col justify-between h-32"
                    >
                      <div>
                        <h4 className="text-xs font-bold text-white truncate">{c.first_name} {c.last_name}</h4>
                        <p className="text-[10px] text-muted-foreground mt-0.5 truncate">{c.email}</p>
                      </div>
                      
                      <div className="flex justify-between items-center pt-2.5 border-t border-border/40">
                        <span className="text-[9px] text-neutral-500 font-mono">{c.employee_id || 'DRAFT'}</span>
                        
                        {col.key !== 'ONBOARDING_COMPLETE' && (
                          <button
                            onClick={() => advanceStage(c.id, c.onboarding_status)}
                            className="p-1 rounded bg-secondary hover:bg-neutral-800 text-blue-400 hover:text-white transition flex items-center gap-0.5"
                            title="Advance Stage"
                          >
                            <ArrowRight size={12} />
                          </button>
                        )}
                      </div>
                    </motion.div>
                  ))}
                  
                  {columnCandidates.length === 0 && (
                    <div className="text-center py-10 text-[10px] text-muted-foreground border border-dashed border-border/40 rounded-xl">
                      Empty column
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
