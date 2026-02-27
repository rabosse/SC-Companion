import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../App';
import { Users, Box, Crosshair, LogOut, Menu, X, Briefcase, GitCompareArrows, Wrench } from 'lucide-react';
import { useState } from 'react';
import SpaceshipIcon from './SpaceshipIcon';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: '/', label: 'Dashboard', icon: SpaceshipIcon },
    { path: '/fleet', label: 'My Fleet', icon: Briefcase },
    { path: '/ships', label: 'Ships', icon: SpaceshipIcon },
    { path: '/vehicles', label: 'Vehicles', icon: Users },
    { path: '/components', label: 'Components', icon: Box },
    { path: '/weapons', label: 'Weapons', icon: Crosshair },
    { path: '/compare', label: 'Compare', icon: GitCompareArrows },
    { path: '/loadout', label: 'Loadout', icon: Wrench },
  ];

  const isActive = (path) => {
    if (path === '/') return location.pathname === path;
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen" style={{ background: '#050508' }}>
      {/* Header */}
      <header className="glass-panel border-b border-white/5 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <img 
                src="https://robertsspaceindustries.com/rsi/static/images/account/avatar_default_big.jpg" 
                alt="Star Citizen Logo"
                className="w-10 h-10 rounded-full"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "https://media.robertsspaceindustries.com/logo/SC-Logo-white.png";
                }}
              />
              <h1 className="text-2xl font-bold tracking-tight uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
                Star Citizen Fleet Manager
              </h1>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    data-testid={`nav-${item.label.toLowerCase()}`}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-300 ${
                      isActive(item.path)
                        ? 'bg-cyan-500 text-black'
                        : 'text-gray-400 hover:text-cyan-500 hover:bg-white/5'
                    }`}
                    style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600, letterSpacing: '0.05em' }}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-3">
                <span className="text-sm text-gray-400">{user?.username}</span>
                <button
                  onClick={logout}
                  data-testid="logout-button"
                  className="flex items-center space-x-2 px-4 py-2 rounded-full border border-red-500/30 text-red-500 hover:bg-red-500 hover:text-white transition-all duration-300"
                  style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600 }}
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg text-gray-400 hover:text-cyan-500 hover:bg-white/5"
                data-testid="mobile-menu-button"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden pb-4 space-y-2" data-testid="mobile-menu">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                      isActive(item.path)
                        ? 'bg-cyan-500 text-black'
                        : 'text-gray-400 hover:text-cyan-500 hover:bg-white/5'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
              <button
                onClick={() => { logout(); setMobileMenuOpen(false); }}
                className="w-full flex items-center space-x-2 px-4 py-2 rounded-lg border border-red-500/30 text-red-500 hover:bg-red-500 hover:text-white transition-all"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;