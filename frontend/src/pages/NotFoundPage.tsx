import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { HelpCircle, ChevronLeft } from 'lucide-react';
import { motion } from 'framer-motion';

export const NotFoundPage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center px-6 relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] bg-red-500/5 rounded-full blur-[80px] pointer-events-none" />

      <div className="text-center max-w-md relative">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 100 }}
          className="w-16 h-16 rounded-2xl bg-destructive/10 border border-destructive/20 flex items-center justify-center text-red-400 mx-auto mb-6 shadow-lg"
        >
          <HelpCircle size={32} />
        </motion.div>

        <h1 className="text-6xl font-bold font-display tracking-tight text-white mb-2">404</h1>
        <h2 className="text-xl font-semibold text-neutral-200 mb-4">Resource not found</h2>
        
        <p className="text-sm text-muted-foreground leading-relaxed mb-8">
          The requested page does not exist or has been relocated. Future modules might map here.
        </p>

        <Link
          to={isAuthenticated ? '/dashboard' : '/'}
          className="inline-flex items-center justify-center px-5 py-3 bg-secondary hover:bg-neutral-800 text-white rounded-lg border border-border text-sm font-semibold transition"
        >
          <ChevronLeft size={16} className="mr-2" />
          {isAuthenticated ? 'Return to Dashboard' : 'Back to Home'}
        </Link>
      </div>
    </div>
  );
};
