import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Ship, User, Clock, Copy, Shield, Zap, Cpu, Box, Crosshair, Download, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SLOT_META = {
  shield: { label: 'Shield', icon: Shield, color: '#00D4FF' },
  power_plant: { label: 'Power Plant', icon: Zap, color: '#FFAE00' },
  cooler: { label: 'Cooler', icon: Box, color: '#00FF9D' },
  quantum_drive: { label: 'Quantum Drive', icon: Cpu, color: '#D4AF37' },
  weapon: { label: 'Weapon', icon: Crosshair, color: '#FF0055' },
};

const SharedLoadout = () => {
  const { shareCode } = useParams();
  const [loadout, setLoadout] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cloning, setCloning] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await axios.get(`${API}/community/loadouts/${shareCode}`);
        setLoadout(res.data.data);
      } catch {
        toast.error('Loadout not found');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [shareCode]);

  const copyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('Share link copied!');
  };

  const cloneLoadout = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      toast.error('Please log in to clone this loadout');
      return;
    }
    setCloning(true);
    try {
      await axios.post(`${API}/loadouts/clone/${shareCode}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Loadout cloned to your collection!');
    } catch {
      toast.error('Failed to clone loadout');
    } finally {
      setCloning(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#050508' }}>
        <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!loadout) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#050508' }}>
        <div className="text-center">
          <Ship className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <h2 className="text-2xl font-bold text-white mb-2" style={{ fontFamily: 'Rajdhani, sans-serif' }}>Loadout Not Found</h2>
          <p className="text-gray-400 mb-6">This loadout may have been deleted or the link is invalid.</p>
          <Link to="/community" className="btn-origin inline-block">Browse Community</Link>
        </div>
      </div>
    );
  }

  const slots = loadout.slots || {};
  const componentEntries = Object.entries(slots).filter(([k]) => !k.startsWith('weapon_'));
  const weaponEntries = Object.entries(slots).filter(([k]) => k.startsWith('weapon_'));
  const totalCost = Object.values(slots).reduce((s, item) => s + (item.cost_auec || 0), 0);

  const getSlotMeta = (key) => {
    const base = key.replace(/_\d+$/, '');
    return SLOT_META[base] || SLOT_META.weapon;
  };

  return (
    <div className="min-h-screen" style={{ background: '#050508' }}>
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        {/* Header */}
        <div className="flex items-center gap-3">
          <Link to="/community" className="p-2 hover:bg-white/10 rounded-lg transition-colors" data-testid="back-to-community">
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </Link>
          <span className="text-sm text-gray-500">Shared Loadout</span>
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-panel rounded-3xl overflow-hidden" data-testid="shared-loadout-view">
          {/* Title section */}
          <div className="p-8 border-b border-white/5">
            <div className="flex items-start justify-between flex-wrap gap-4">
              <div>
                <h1 className="text-3xl sm:text-4xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  {loadout.loadout_name}
                </h1>
                <div className="flex items-center gap-3 mt-2 flex-wrap">
                  <div className="flex items-center gap-2">
                    <Ship className="w-4 h-4 text-cyan-500" />
                    <span className="text-cyan-400 font-semibold">{loadout.ship_name}</span>
                  </div>
                  <span className="text-gray-600">|</span>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <User className="w-3.5 h-3.5" />
                    <span>{loadout.username || 'Unknown Pilot'}</span>
                  </div>
                  <span className="text-gray-600">|</span>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{loadout.updated_at ? new Date(loadout.updated_at).toLocaleDateString() : 'N/A'}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={copyLink} data-testid="copy-share-link"
                  className="flex items-center gap-2 px-4 py-2 rounded-xl border border-white/10 text-gray-400 hover:text-white hover:border-white/20 transition-all text-sm">
                  <Copy className="w-4 h-4" /> Copy Link
                </button>
                <button onClick={cloneLoadout} disabled={cloning} data-testid="clone-loadout-btn"
                  className="flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-black disabled:opacity-50 transition-all text-sm"
                  style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}>
                  <Download className="w-4 h-4" /> {cloning ? 'Cloning...' : 'Clone to My Loadouts'}
                </button>
              </div>
            </div>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-3 border-b border-white/5">
            <div className="p-4 text-center">
              <div className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{Object.keys(slots).length}</div>
              <div className="text-xs text-gray-500">Items Equipped</div>
            </div>
            <div className="p-4 text-center border-x border-white/5">
              <div className="text-2xl font-bold text-yellow-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{totalCost.toLocaleString()}</div>
              <div className="text-xs text-gray-500">Total aUEC</div>
            </div>
            <div className="p-4 text-center">
              <div className="text-2xl font-bold text-red-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{weaponEntries.length}</div>
              <div className="text-xs text-gray-500">Weapons</div>
            </div>
          </div>

          {/* Equipment list */}
          <div className="p-6 space-y-6">
            {/* Components */}
            {componentEntries.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">Components</h3>
                <div className="space-y-2">
                  {componentEntries.map(([key, item]) => {
                    const meta = getSlotMeta(key);
                    const Icon = meta.icon;
                    return (
                      <div key={key} className="flex items-center justify-between p-3 bg-white/[0.03] rounded-xl border border-white/5" data-testid={`shared-slot-${key}`}>
                        <div className="flex items-center gap-3 min-w-0">
                          <Icon className="w-5 h-5 shrink-0" style={{ color: meta.color }} />
                          <div className="min-w-0">
                            <div className="font-semibold text-white text-sm truncate">{item.name}</div>
                            <div className="text-xs text-gray-500">{meta.label} - {item.manufacturer || ''} {item.size ? `S${item.size}` : ''}</div>
                          </div>
                        </div>
                        {item.cost_auec > 0 && (
                          <span className="text-sm text-yellow-400 font-semibold shrink-0 ml-3">{item.cost_auec.toLocaleString()} aUEC</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Weapons */}
            {weaponEntries.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">Weapons</h3>
                <div className="space-y-2">
                  {weaponEntries.map(([key, item]) => (
                    <div key={key} className="flex items-center justify-between p-3 bg-white/[0.03] rounded-xl border border-white/5" data-testid={`shared-slot-${key}`}>
                      <div className="flex items-center gap-3 min-w-0">
                        <Crosshair className="w-5 h-5 shrink-0 text-red-500" />
                        <div className="min-w-0">
                          <div className="font-semibold text-white text-sm truncate">{item.name}</div>
                          <div className="text-xs text-gray-500">{item.manufacturer || ''} {item.size ? `S${item.size}` : ''} {item.damage > 0 ? `DMG: ${item.damage}` : ''}</div>
                        </div>
                      </div>
                      {item.cost_auec > 0 && (
                        <span className="text-sm text-yellow-400 font-semibold shrink-0 ml-3">{item.cost_auec.toLocaleString()} aUEC</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(slots).length === 0 && (
              <div className="text-center py-8 text-gray-500">This loadout has no items equipped.</div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SharedLoadout;
