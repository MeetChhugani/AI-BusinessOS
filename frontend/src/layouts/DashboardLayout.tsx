import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { 
  LayoutDashboard, Users, Package, HeartHandshake, Bot, Landmark,
  Menu, X, Sun, Moon, LogOut, ChevronDown 
} from 'lucide-react';

export const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard', active: true },
    { name: 'Employee Management', icon: Users, path: '/dashboard/hcm', active: true },
    { name: 'Inventory & Stock', icon: Package, path: '/dashboard/inventory', active: true },
    { name: 'CRM & Client Hub', icon: HeartHandshake, path: '/dashboard/crm', active: true },
    { name: 'Finance & Ledger', icon: Landmark, path: '/dashboard/finance', active: true },
    { name: 'AI Features', icon: Bot, path: '/dashboard/ai', active: false },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground flex overflow-hidden">
      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex md:w-64 md:flex-col bg-card border-r border-border shrink-0">
        {/* Sidebar Header */}
        <div className="h-16 px-6 border-b border-border flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold font-display tracking-tight text-white flex items-center gap-1.5">
              <span className="bg-gradient-to-r from-blue-500 to-indigo-500 w-4 h-4 rounded-md flex items-center justify-center text-[10px] text-white">⚡</span>
              Business<span className="text-blue-500">OS</span>
            </span>
          </Link>
        </div>

        {/* Sidebar Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map((item, idx) => {
            const Icon = item.icon;
            if (item.active) {
              return (
                <Link
                  key={idx}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    location.pathname === item.path
                      ? 'bg-secondary text-white border border-border shadow-sm'
                      : 'text-muted-foreground hover:bg-secondary/40 hover:text-white'
                  }`}
                >
                  <Icon size={18} className={location.pathname === item.path ? 'text-blue-500' : ''} />
                  <span>{item.name}</span>
                </Link>
              );
            } else {
              return (
                <div
                  key={idx}
                  className="flex items-center justify-between px-4 py-2.5 rounded-lg text-sm text-muted-foreground/40 cursor-not-allowed group relative"
                  title="Future Module - Not Installed"
                >
                  <div className="flex items-center space-x-3">
                    <Icon size={18} />
                    <span>{item.name}</span>
                  </div>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-neutral-500 uppercase tracking-wide">
                    Future
                  </span>
                </div>
              );
            }
          })}
        </nav>

        {/* Sidebar Footer / User Identity */}
        <div className="p-4 border-t border-border bg-black/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 overflow-hidden">
              <img
                src={user?.profile_image || `https://api.dicebear.com/7.x/initials/svg?seed=${user?.full_name}`}
                alt="Profile"
                className="w-9 h-9 rounded-full bg-secondary border border-border shrink-0"
              />
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-white truncate">{user?.full_name}</p>
                <p className="text-[10px] text-muted-foreground truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="p-1.5 rounded-md hover:bg-secondary text-muted-foreground hover:text-red-400 transition"
              title="Logout"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-grow flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="h-16 border-b border-border flex items-center justify-between px-6 bg-card/60 backdrop-blur-md z-40">
          <div className="flex items-center space-x-4">
            {/* Mobile menu trigger */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md hover:bg-secondary text-muted-foreground md:hidden"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>

            {/* Breadcrumb / Title */}
            <div className="flex items-center space-x-2 text-xs font-medium text-muted-foreground">
              <span>SaaS Platform</span>
              <span className="text-neutral-600">/</span>
              <span className="text-white capitalize">
                {location.pathname.split('/').pop() || 'Overview'}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Environment Badge */}
            <span className="hidden sm:inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              <span>Core Foundation Active</span>
            </span>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>

            {/* User Dropdown */}
            <div className="relative">
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center space-x-1.5 p-1 rounded-full hover:bg-secondary text-muted-foreground transition"
              >
                <img
                  src={user?.profile_image || `https://api.dicebear.com/7.x/initials/svg?seed=${user?.full_name}`}
                  alt="Avatar"
                  className="w-7 h-7 rounded-full bg-secondary border border-border"
                />
                <ChevronDown size={14} />
              </button>

              {userDropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => setUserDropdownOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-56 rounded-xl bg-card border border-border p-2 shadow-2xl z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                    <div className="px-3 py-2 border-b border-border mb-1.5">
                      <p className="text-xs font-semibold text-white truncate">{user?.full_name}</p>
                      <p className="text-[10px] text-muted-foreground truncate">{user?.email}</p>
                      <span className="mt-1 inline-block text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-wider">
                        {user?.role}
                      </span>
                    </div>

                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-2 px-3 py-2 text-xs text-red-400 hover:bg-red-500/10 rounded-lg transition text-left"
                    >
                      <LogOut size={14} />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Route content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-background relative">
          {children}
        </main>
      </div>

      {/* Mobile Drawer Navigation Overlay */}
      {mobileMenuOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/60 z-40 md:hidden"
            onClick={() => setMobileMenuOpen(false)}
          />
          <aside className="fixed inset-y-0 left-0 w-64 bg-card border-r border-border p-6 flex flex-col justify-between z-50 md:hidden animate-in slide-in-from-left duration-200">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold font-display tracking-tight text-white flex items-center gap-1.5">
                  <span className="bg-gradient-to-r from-blue-500 to-indigo-500 w-4 h-4 rounded-md flex items-center justify-center text-[10px] text-white">⚡</span>
                  BusinessOS
                </span>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1 rounded-md hover:bg-secondary text-muted-foreground"
                >
                  <X size={18} />
                </button>
              </div>

              <nav className="space-y-1.5">
                {navItems.map((item, idx) => {
                  const Icon = item.icon;
                  if (item.active) {
                    return (
                      <Link
                        key={idx}
                        to={item.path}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                          location.pathname === item.path
                            ? 'bg-secondary text-white border border-border shadow-sm'
                            : 'text-muted-foreground hover:bg-secondary/40 hover:text-white'
                        }`}
                      >
                        <Icon size={18} className={location.pathname === item.path ? 'text-blue-500' : ''} />
                        <span>{item.name}</span>
                      </Link>
                    );
                  } else {
                    return (
                      <div
                        key={idx}
                        className="flex items-center justify-between px-4 py-2.5 rounded-lg text-sm text-muted-foreground/30 cursor-not-allowed"
                      >
                        <div className="flex items-center space-x-3">
                          <Icon size={18} />
                          <span>{item.name}</span>
                        </div>
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-neutral-900 border border-border text-neutral-500 uppercase">
                          Future
                        </span>
                      </div>
                    );
                  }
                })}
              </nav>
            </div>

            <div className="border-t border-border pt-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 overflow-hidden">
                  <img
                    src={user?.profile_image || `https://api.dicebear.com/7.x/initials/svg?seed=${user?.full_name}`}
                    alt="Profile"
                    className="w-9 h-9 rounded-full bg-secondary border border-border"
                  />
                  <div className="overflow-hidden">
                    <p className="text-xs font-semibold text-white truncate">{user?.full_name}</p>
                    <p className="text-[10px] text-muted-foreground truncate">{user?.email}</p>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-1.5 rounded-md hover:bg-secondary text-muted-foreground hover:text-red-400"
                >
                  <LogOut size={16} />
                </button>
              </div>
            </div>
          </aside>
        </>
      )}
    </div>
  );
};
