import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { Shield, Zap, Sparkles, BarChart2, ChevronRight, Moon, Sun } from 'lucide-react';
import { motion } from 'framer-motion';

export const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary selection:text-primary-foreground overflow-x-hidden">
      {/* Dynamic Header */}
      <header className="fixed top-0 w-full z-50 glass-navbar transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold font-display tracking-tight text-white flex items-center gap-1.5">
              <span className="bg-gradient-to-r from-blue-500 to-indigo-500 w-5 h-5 rounded-md flex items-center justify-center text-xs text-white">⚡</span>
              AI Business<span className="text-blue-500">OS</span>
            </span>
          </div>

          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition-colors">Features</a>
            <a href="#architecture" className="hover:text-foreground transition-colors">Architecture</a>
            <a href="#security" className="hover:text-foreground transition-colors">Security</a>
          </nav>

          <div className="flex items-center space-x-4">
            <button 
              onClick={toggleTheme} 
              className="p-2 rounded-full hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Toggle Theme"
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>

            {isAuthenticated ? (
              <Link 
                to="/dashboard" 
                className="inline-flex items-center justify-center px-4 py-2 text-xs font-semibold bg-white text-black hover:bg-neutral-200 rounded-lg transition-all duration-200"
              >
                Go to Dashboard
                <ChevronRight size={14} className="ml-1" />
              </Link>
            ) : (
              <>
                <Link to="/login" className="text-sm font-medium hover:text-white transition-colors">
                  Log in
                </Link>
                <Link 
                  to="/register" 
                  className="inline-flex items-center justify-center px-4 py-2 text-xs font-semibold bg-white text-black hover:bg-neutral-200 rounded-lg transition-all duration-200"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 md:pt-40 md:pb-32 px-6 flex flex-col items-center text-center">
        {/* Glow behind */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />

        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center space-x-1.5 px-3 py-1 bg-secondary text-muted-foreground border border-border rounded-full text-xs font-medium mb-6"
        >
          <Sparkles size={12} className="text-blue-500" />
          <span>The Next Generation SaaS ERP Foundation</span>
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-5xl md:text-7xl font-bold font-display tracking-tight max-w-4xl leading-[1.1] mb-8"
        >
          Engineered for <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">Scale</span>. Built for <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-500">Developers</span>.
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mb-10 leading-relaxed"
        >
          AI BusinessOS is a production-ready enterprise SaaS boilerplate featuring SQLAlchemy 2, Alembic, structured logging, JWT rotation, global rate limiting, and an adaptive glassmorphic frontend shell.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <Link 
            to="/register" 
            className="inline-flex items-center justify-center px-6 py-3 text-sm font-semibold bg-white text-black hover:bg-neutral-200 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
          >
            Create Developer Account
          </Link>
          <a 
            href="#features" 
            className="inline-flex items-center justify-center px-6 py-3 text-sm font-semibold bg-secondary hover:bg-neutral-800 text-white rounded-lg border border-border transition-all duration-200"
          >
            Explore Architecture
          </a>
        </motion.div>

        {/* Hero Image Mockup */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-20 w-full max-w-5xl aspect-[16/9] rounded-xl overflow-hidden glass-card p-2 glow-border shadow-2xl relative"
        >
          <div className="w-full h-full rounded-lg bg-black/60 flex flex-col overflow-hidden border border-neutral-800">
            {/* Window bar */}
            <div className="h-10 px-4 bg-neutral-900/60 border-b border-neutral-800 flex items-center justify-between">
              <div className="flex space-x-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
              <div className="text-[11px] text-neutral-500 font-mono">https://app.aibusinessos.com/dashboard</div>
              <div className="w-12" />
            </div>
            
            {/* Window Content Placeholder */}
            <div className="flex-1 p-6 grid grid-cols-4 gap-4 opacity-50 select-none">
              <div className="col-span-1 rounded-lg bg-neutral-900 border border-neutral-800 h-full flex flex-col p-4">
                <div className="w-8 h-8 rounded-full bg-neutral-800 mb-6" />
                <div className="h-4 bg-neutral-800 rounded w-3/4 mb-3" />
                <div className="h-3 bg-neutral-800 rounded w-1/2 mb-2" />
                <div className="h-3 bg-neutral-800 rounded w-2/3" />
              </div>
              <div className="col-span-3 grid grid-rows-3 gap-4">
                <div className="row-span-1 grid grid-cols-3 gap-4">
                  <div className="rounded-lg bg-neutral-900 border border-neutral-800 p-4 flex flex-col justify-between">
                    <div className="h-2 bg-neutral-800 rounded w-1/2" />
                    <div className="h-6 bg-neutral-800 rounded w-3/4" />
                  </div>
                  <div className="rounded-lg bg-neutral-900 border border-neutral-800 p-4 flex flex-col justify-between">
                    <div className="h-2 bg-neutral-800 rounded w-1/2" />
                    <div className="h-6 bg-neutral-800 rounded w-3/4" />
                  </div>
                  <div className="rounded-lg bg-neutral-900 border border-neutral-800 p-4 flex flex-col justify-between">
                    <div className="h-2 bg-neutral-800 rounded w-1/2" />
                    <div className="h-6 bg-neutral-800 rounded w-3/4" />
                  </div>
                </div>
                <div className="row-span-2 rounded-lg bg-neutral-900 border border-neutral-800 p-6 flex flex-col justify-between">
                  <div className="h-4 bg-neutral-800 rounded w-1/4" />
                  <div className="h-24 bg-neutral-800 rounded w-full" />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 max-w-7xl mx-auto px-6 relative border-t border-border">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-3xl sm:text-4xl font-bold font-display tracking-tight mb-4">The Complete Enterprise Toolkit</h2>
          <p className="text-muted-foreground">Every architectural capability a scaling SaaS requires, built directly from day one.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Card 1 */}
          <div className="glass-card rounded-2xl p-8 flex flex-col justify-between relative hover:border-neutral-700 transition-all duration-300">
            <div>
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 mb-6 border border-blue-500/20">
                <Shield size={20} />
              </div>
              <h3 className="text-lg font-semibold mb-3">JWT Refresh Token Rotation</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Prevents replay attacks by invalidating old refresh tokens and issuing rotating pairs. Blacklists are stored efficiently in Redis.
              </p>
            </div>
          </div>

          {/* Card 2 */}
          <div className="glass-card rounded-2xl p-8 flex flex-col justify-between relative hover:border-neutral-700 transition-all duration-300">
            <div>
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-6 border border-indigo-500/20">
                <Zap size={20} />
              </div>
              <h3 className="text-lg font-semibold mb-3">Global & Auth Rate Limiting</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Redis-backed rate limiters enforce 100 req/min globally, alongside specialized caps for login paths (10/hr) and password recovery (5/hr).
              </p>
            </div>
          </div>

          {/* Card 3 */}
          <div className="glass-card rounded-2xl p-8 flex flex-col justify-between relative hover:border-neutral-700 transition-all duration-300">
            <div>
              <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 mb-6 border border-purple-500/20">
                <BarChart2 size={20} />
              </div>
              <h3 className="text-lg font-semibold mb-3">Audit Base & Soft Deletes</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Database entities inherit universal identifiers, trace timestamps, and soft deletion flags. Standard database queries respect active states automatically.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-6 bg-black/40">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between text-xs text-muted-foreground">
          <p>© 2026 AI BusinessOS. Built with React 19, FastAPI, and PostgreSQL.</p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#features" className="hover:text-foreground">Terms</a>
            <a href="#features" className="hover:text-foreground">Privacy</a>
            <a href="#features" className="hover:text-foreground">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
};
