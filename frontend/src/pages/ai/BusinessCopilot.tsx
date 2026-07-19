import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { AIMessage } from '../../types/ai';
import { 
  Bot, User, Send, Sparkles, ShieldCheck, 
  ChevronRight, AlertCircle
} from 'lucide-react';

export const BusinessCopilot: React.FC = () => {
  const { accessToken } = useAuth();
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [inputPrompt, setInputPrompt] = useState('');
  const [conversationId, setConversationId] = useState<string>('00000000-0000-0000-0000-000000000000');
  const [isSending, setIsSending] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Suggestions list
  const suggestions = [
    "Explain revenue this month",
    "Show active employee headcount",
    "Search ERP entities for Initech",
    "Simulate safety stock reorder thresholds"
  ];

  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, lineIdx) => {
      const parts = line.split(/(\*\*[^*]+\*\*)/g);
      const elements = parts.map((part, partIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={partIdx} className="font-bold text-white">{part.slice(2, -2)}</strong>;
        }
        return part;
      });
      
      if (line.trim() === '') {
        return <div key={lineIdx} className="h-2" />;
      }

      return (
        <p key={lineIdx} className="text-neutral-300 leading-relaxed font-medium mt-1">
          {elements}
        </p>
      );
    });
  };

  const handleSend = async (text: string) => {
    if (!text.trim() || isSending) return;
    setErrorMessage('');
    setIsSending(true);

    // Append User message locally
    const userMsg: AIMessage = {
      id: Math.random().toString(),
      conversation_id: conversationId,
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);
    setInputPrompt('');

    try {
      const res = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          prompt: text
        })
      });

      if (res.ok) {
        const d = await res.json();
        setConversationId(d.conversation_id);
        
        // Append assistant response
        const assistantMsg: AIMessage = {
          id: Math.random().toString(),
          conversation_id: d.conversation_id,
          role: 'assistant',
          content: d.content,
          confidence_score: d.confidence,
          created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, assistantMsg]);
      } else {
        const errData = await res.json();
        setErrorMessage(errData.detail || 'An error occurred during execution');
      }
    } catch (e) {
      console.error(e);
      setErrorMessage('Network connection error');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] max-w-5xl mx-auto space-y-4">
      {/* Page Header */}
      <div className="flex items-center justify-between border-b border-neutral-800 pb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold font-display text-white tracking-tight flex items-center gap-2">
            <Sparkles size={20} className="text-indigo-400" />
            Enterprise Business Copilot
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Modular multi-agent planning engine. Ask the copilot anything about HR, Finance, CRM, or Inventory.
          </p>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/25 rounded-full text-emerald-400 text-[10px] font-bold">
          <ShieldCheck size={12} />
          RBAC GUARDRAILS ACTIVE
        </div>
      </div>

      {/* Message Output Console */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 bg-card/35 border border-neutral-800 rounded-2xl">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6 max-w-md mx-auto">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/25 text-indigo-400">
              <Bot size={24} />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Plan-Execute Controller</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Send a request to let the Planner map sequential execution steps, route to specialized supervisor agents, check security criteria, and compile results.
              </p>
            </div>

            {/* Suggestions lists */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left pt-4">
              {suggestions.map((sug, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(sug)}
                  className="p-3 bg-secondary/35 border border-border/40 hover:bg-secondary/70 rounded-xl text-[10px] font-semibold text-neutral-300 transition flex items-center justify-between"
                >
                  <span>{sug}</span>
                  <ChevronRight size={12} className="text-muted-foreground" />
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4 text-xs">
            {messages.map(m => (
              <div key={m.id} className={`flex gap-3.5 p-4 rounded-2xl border ${
                m.role === 'user' ? 'bg-secondary/20 border-border/30 justify-end' : 'bg-card border-neutral-800'
              }`}>
                {m.role !== 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/25 text-indigo-400 shrink-0">
                    <Bot size={16} />
                  </div>
                )}
                <div className="space-y-2 flex-1 max-w-3xl">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white uppercase text-[10px]">
                      {m.role === 'user' ? 'You' : 'Business Copilot'}
                    </span>
                    {m.confidence_score && (
                      <span className="px-1.5 py-0.5 rounded text-[8px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {m.confidence_score} CONFIDENCE
                      </span>
                    )}
                  </div>
                  <div className="space-y-1">{renderFormattedContent(m.content)}</div>
                </div>
                {m.role === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-neutral-800 flex items-center justify-center border border-neutral-700 text-neutral-300 shrink-0">
                    <User size={16} />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {errorMessage && (
        <div className="p-3.5 bg-rose-500/10 border border-rose-500/25 text-rose-400 text-xs rounded-xl flex items-center gap-2">
          <AlertCircle size={14} />
          {errorMessage}
        </div>
      )}

      {/* Input console */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(inputPrompt); }} className="relative flex gap-3 text-xs">
        <input
          required
          disabled={isSending}
          placeholder="Ask about dynamic ledger values attrition rates or search catalog entries..."
          className="w-full px-4 py-3 bg-card border border-neutral-800 rounded-xl text-white focus:outline-none focus:border-indigo-500 transition disabled:opacity-50"
          value={inputPrompt}
          onChange={e => setInputPrompt(e.target.value)}
        />
        <button
          type="submit"
          disabled={isSending}
          className="px-4 py-3 bg-white text-black hover:bg-neutral-200 rounded-xl font-bold transition flex items-center gap-1.5 disabled:opacity-50"
        >
          <Send size={14} />
          Send
        </button>
      </form>
    </div>
  );
};
