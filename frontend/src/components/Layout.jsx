import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../App';
import { Users, Box, Crosshair, LogOut, Menu, X, Briefcase, GitCompareArrows, Wrench, Globe, Navigation, Shield, TrendingUp, Star } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import SpaceshipIcon from './SpaceshipIcon';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [headerVisible, setHeaderVisible] = useState(true);
  const lastScrollY = useRef(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentY = window.scrollY;
      if (currentY < 10) {
        setHeaderVisible(true);
      } else if (currentY > lastScrollY.current) {
        setHeaderVisible(false);
      } else {
        setHeaderVisible(true);
      }
      lastScrollY.current = currentY;
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { path: '/', label: 'Dashboard', icon: SpaceshipIcon },
    { path: '/fleet', label: 'My Fleet', icon: Briefcase },
    { path: '/ships', label: 'Ships', icon: SpaceshipIcon },
    { path: '/vehicles', label: 'Vehicles', icon: Users },
    { path: '/components', label: 'Components', icon: Box },
    { path: '/weapons', label: 'Weapons', icon: Crosshair },
    { path: '/compare', label: 'Compare', icon: GitCompareArrows },
    { path: '/loadout', label: 'Loadout', icon: Wrench },
    { path: '/community', label: 'Community', icon: Globe },
    { path: '/routes', label: 'Routes', icon: Navigation },
    { path: '/gear', label: 'Gear', icon: Shield },
    { path: '/wikelo', label: 'Wikelo', icon: Star },
    { path: '/prices', label: 'Prices', icon: TrendingUp },
  ];

  const isActive = (path) => {
    if (path === '/') return location.pathname === path;
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen" style={{ background: '#050508' }}>
      {/* Header */}
      <header
        className="glass-panel border-b border-white/5 fixed top-0 left-0 right-0 z-50 transition-transform duration-300"
        style={{ transform: headerVisible ? 'translateY(0)' : 'translateY(-100%)' }}
      >
        <div className="px-4 sm:px-6">
          <div className="flex items-center h-16 gap-4">
            <Link to="/" className="flex items-center gap-2.5 group shrink-0">
              <img 
                src="https://robertsspaceindustries.com/rsi/static/images/account/avatar_default_big.jpg" 
                alt="Star Citizen Logo"
                className="w-8 h-8 rounded-full ring-2 ring-cyan-500/30 group-hover:ring-cyan-500/60 transition-all"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "https://media.robertsspaceindustries.com/logo/SC-Logo-white.png";
                }}
              />
              <div className="leading-none hidden lg:block">
                <span className="text-[9px] font-bold uppercase tracking-[0.25em] text-cyan-500/70" style={{ fontFamily: 'Rajdhani, sans-serif' }}>Star Citizen</span>
                <div className="text-base font-bold uppercase tracking-wide text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>Companion</div>
              </div>
            </Link>

            {/* Desktop Navigation - scrollable */}
            <nav className="hidden md:flex items-center gap-1 overflow-x-auto scrollbar-hide flex-1 min-w-0" data-testid="desktop-nav">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    data-testid={`nav-${item.label.toLowerCase()}`}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all duration-300 whitespace-nowrap shrink-0 text-sm ${
                      isActive(item.path)
                        ? 'bg-cyan-500 text-black'
                        : 'text-gray-400 hover:text-cyan-500 hover:bg-white/5'
                    }`}
                    style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600, letterSpacing: '0.05em' }}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="flex items-center gap-3 shrink-0 ml-auto">
              <div className="hidden md:flex items-center gap-3">
                <span className="text-sm text-gray-400 whitespace-nowrap">{user?.username}</span>
                <button
                  onClick={logout}
                  data-testid="logout-button"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-red-500/30 text-red-500 hover:bg-red-500 hover:text-white transition-all duration-300 whitespace-nowrap"
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
            <div className="md:hidden pb-4 pt-2 px-2 space-y-2 bg-[#0a0e14] border-t border-white/5" data-testid="mobile-menu">
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

      {/* Main Content — offset for fixed header */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-16">
        {children}
      </main>
    </div>
  );
};

export default Layout;