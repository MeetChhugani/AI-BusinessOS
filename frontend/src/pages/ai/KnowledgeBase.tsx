import React from 'react';
import { BookOpen } from 'lucide-react';

export const KnowledgeBase: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          Abstract Retrieval-Augmented Generation (RAG)
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Review versioned documentation chunks, employee policies manuals, and vector records mappings.
        </p>
      </div>

      <div className="p-12 text-center border border-dashed border-border rounded-2xl flex flex-col items-center justify-center gap-2">
        <BookOpen size={32} className="text-muted-foreground mb-1 animate-pulse" />
        <span className="text-sm font-bold text-white uppercase tracking-wider">RAG Knowledge Repository</span>
        <p className="text-xs text-muted-foreground max-w-md">
          Upload PDF/CSV Policies manuals to chunk and calculate similarity vectors for search-context retrieval queries.
        </p>
      </div>
    </div>
  );
};
