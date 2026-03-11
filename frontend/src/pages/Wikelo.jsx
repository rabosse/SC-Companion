import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { useAuth } from '../App';
import { Search, X, Shield, Crosshair, Rocket, Coins, Wrench, Package, ChevronRight, Star } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

const CAT_CONFIG = {
  Vehicles: { color: '#00D4FF', icon: Rocket, label: 'Vehicles' },
  Weapons: { color: '#FF6B35', icon: Crosshair, label: 'Weapons' },
  Armor: { color: '#A855F7', icon: Shield, label: 'Armor' },
  Currencies: { color: '#FFD700', icon: Coins, label: 'Currencies' },
  Utility: { color: '#00FF9D', icon: Wrench, label: 'Utility' },
};

const Wikelo = () => {
  const { API } = useAuth();
  const [contracts, setContracts] = useState([]);
  const [categories, setCategories] = useState({});
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('Vehicles');
  const [search, setSearch] = useState('');
  const [showInactive, setShowInactive] = useState(true);
  const [selectedContract, setSelectedContract] = useState(null);
  const [shipImages, setShipImages] = useState({});

  useEffect(() => {
    const load = async () => {
      try {
        const [cRes, iRes] = await Promise.all([
          axios.get(`${API}/wikelo/contracts`),
          axios.get(`${API}/wikelo/info`),
        ]);
        setContracts(cRes.data.data || []);
        setCategories(cRes.data.categories || {});
        setInfo(iRes.data.data || null);
        // Fetch ship images for vehicle reward matching
        try {
          const sRes = await axios.get(`${API}/ships`);
          const vRes = await axios.get(`${API}/vehicles`);
          const all = [...(sRes.data.data || []), ...(vRes.data.data || [])];
          const imgMap = {};
          all.forEach(s => {
            if (s.image) {
              imgMap[s.name.toLowerCase()] = s.image;
              imgMap[s.id] = s.image;
            }
          });
          setShipImages(imgMap);
        } catch {}
      } catch { toast.error('Failed to load Wikelo data'); }
      finally { setLoading(false); }
    };
    load();
  }, []);

  const filtered = useMemo(() => {
    let items = contracts.filter(c => c.category === activeTab);
    if (!showInactive) items = items.filter(c => c.active);
    if (search) {
      const q = search.toLowerCase();
      items = items.filter(c =>
        c.name.toLowerCase().includes(q) ||
        c.reward.some(r => r.toLowerCase().includes(q)) ||
        c.items_needed.some(i => i.toLowerCase().includes(q))
      );
    }
    return items;
  }, [contracts, activeTab, search, showInactive]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  const tabOrder = ['Vehicles', 'Weapons', 'Armor', 'Currencies', 'Utility'];

  return (
    <div className="space-y-6" data-testid="wikelo-page">
      {/* Header */}
      <div className="flex items-start gap-5">
        {info?.image && (
          <img src={info.image} alt="Wikelo" className="w-20 h-20 rounded-xl object-cover border border-white/10 hidden sm:block" />
        )}
        <div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-1 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#FFD700' }}>
            Wikelo
          </h1>
          <p className="text-gray-400 text-sm">{info?.description}</p>
          <div className="flex gap-3 mt-2 flex-wrap">
            {info?.locations?.map(loc => (
              <span key={loc.name} className="text-xs px-2 py-1 rounded-md bg-white/5 border border-white/10 text-gray-400">
                {loc.name} <span className="text-amber-400">({loc.near})</span>
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 flex-wrap" data-testid="wikelo-tabs">
        {tabOrder.map(cat => {
          const cfg = CAT_CONFIG[cat] || {};
          const Icon = cfg.icon || Package;
          const catData = categories[cat] || { total: 0, active: 0 };
          return (
            <button key={cat} onClick={() => { setActiveTab(cat); setSearch(''); }}
              data-testid={`wikelo-tab-${cat.toLowerCase()}`}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-xs uppercase transition-all ${activeTab === cat
                ? `border bg-opacity-20 text-opacity-100`
                : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}
              style={activeTab === cat ? { backgroundColor: `${cfg.color}20`, color: cfg.color, borderColor: `${cfg.color}40` } : {}}>
              <Icon className="w-4 h-4" />
              {cfg.label || cat} ({catData.active}/{catData.total})
            </button>
          );
        })}
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-xl p-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)}
            data-testid="wikelo-search"
            placeholder="Search contracts, rewards, or items..."
            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-cyan-500" />
        </div>
        <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer select-none">
          <input type="checkbox" checked={showInactive} onChange={e => setShowInactive(e.target.checked)}
            data-testid="wikelo-show-inactive"
            className="rounded border-gray-600 bg-transparent text-cyan-500 focus:ring-cyan-500" />
          Show inactive contracts
        </label>
      </div>

      {/* Count */}
      <div className="text-sm text-gray-500">{filtered.length} contracts found</div>

      {/* Contract Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((contract, i) => (
          <ContractCard key={contract.id} contract={contract} index={i} onClick={() => setSelectedContract(contract)} shipImages={shipImages} />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12 text-gray-500">No contracts found matching your criteria.</div>
      )}

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedContract && (
          <ContractModal contract={selectedContract} onClose={() => setSelectedContract(null)} shipImages={shipImages} />
        )}
      </AnimatePresence>
    </div>
  );
};

const ContractCard = ({ contract, index, onClick, shipImages }) => {
  const cfg = CAT_CONFIG[contract.category] || {};
  const color = cfg.color || '#888';
  // Resolve image: use contract image first, then try matching reward ship name
  let displayImage = contract.image;
  if (!displayImage && contract.category === 'Vehicles' && contract.reward?.length > 0) {
    const rewardName = contract.reward[0].toLowerCase();
    displayImage = shipImages[rewardName];
    if (!displayImage) {
      // Try partial match
      const keys = Object.keys(shipImages);
      const match = keys.find(k => rewardName.includes(k) || k.includes(rewardName));
      if (match) displayImage = shipImages[match];
    }
  }
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.03 }}
      onClick={onClick}
      data-testid={`contract-card-${contract.id}`}
      className="glass-panel rounded-xl p-0 overflow-hidden cursor-pointer group hover:border-white/20 transition-all"
    >
      {/* Image or colored header */}
      {displayImage ? (
        <div className="h-36 bg-black/40 flex items-center justify-center overflow-hidden">
          <img src={displayImage} alt={contract.name}
            className="h-full w-full object-contain group-hover:scale-105 transition-transform duration-300"
            onError={e => { e.target.style.display = 'none'; }} />
        </div>
      ) : (
        <div className="h-16" style={{ background: `linear-gradient(135deg, ${color}15, transparent)` }}>
          <div className="h-full flex items-center justify-center">
            {cfg.icon && <cfg.icon className="w-8 h-8 opacity-20" style={{ color }} />}
          </div>
        </div>
      )}
      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="text-sm font-bold text-white leading-tight group-hover:text-cyan-400 transition-colors" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
            {contract.name}
          </h3>
          <div className="flex gap-1.5 shrink-0">
            {!contract.active && (
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30 uppercase">
                Inactive
              </span>
            )}
            {contract.req_rank && (
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-0.5">
                <Star className="w-2.5 h-2.5" /> {contract.req_rank}
              </span>
            )}
          </div>
        </div>
        <div className="mb-2">
          <p className="text-xs text-gray-500 mb-1">Reward:</p>
          {contract.reward.map((r, i) => (
            <p key={i} className="text-xs font-semibold" style={{ color }}>{r}</p>
          ))}
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-gray-600">{contract.items_needed.length} items required</span>
          <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-cyan-400 transition-colors" />
        </div>
      </div>
    </motion.div>
  );
};

const ContractModal = ({ contract, onClose, shipImages }) => {
  const cfg = CAT_CONFIG[contract.category] || {};
  const color = cfg.color || '#888';
  let modalImage = contract.image;
  if (!modalImage && contract.category === 'Vehicles' && contract.reward?.length > 0) {
    const rewardName = contract.reward[0].toLowerCase();
    modalImage = shipImages[rewardName];
    if (!modalImage) {
      const keys = Object.keys(shipImages);
      const match = keys.find(k => rewardName.includes(k) || k.includes(rewardName));
      if (match) modalImage = shipImages[match];
    }
  }
  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={onClose}
      data-testid="wikelo-contract-modal"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
        onClick={e => e.stopPropagation()}
        className="w-full max-w-lg bg-gray-900 border border-white/10 rounded-2xl overflow-hidden max-h-[85vh] flex flex-col"
      >
        {/* Header */}
        {modalImage && (
          <div className="h-44 bg-black/60 flex items-center justify-center">
            <img src={modalImage} alt={contract.name} className="h-full object-contain" />
          </div>
        )}
        <div className="p-6 overflow-y-auto flex-1">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                {contract.name}
              </h2>
              <div className="flex gap-2 mt-1">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase" style={{ backgroundColor: `${color}20`, color, border: `1px solid ${color}40` }}>
                  {contract.category}
                </span>
                {contract.active ? (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 border border-green-500/30 uppercase">Active</span>
                ) : (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 uppercase">Inactive</span>
                )}
                {contract.req_rank && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 uppercase flex items-center gap-1">
                    <Star className="w-2.5 h-2.5" /> {contract.req_rank}
                  </span>
                )}
              </div>
            </div>
            <button onClick={onClose} data-testid="close-wikelo-modal"
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-gray-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Reward Section */}
          <div className="mb-5">
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Reward</h3>
            <div className="bg-white/5 rounded-lg p-3 border border-white/10 space-y-1">
              {contract.reward.map((r, i) => (
                <p key={i} className="text-sm font-semibold" style={{ color }}>{r}</p>
              ))}
            </div>
          </div>

          {/* Items Needed Section */}
          <div>
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
              Items Needed ({contract.items_needed.length})
            </h3>
            <div className="space-y-1.5">
              {contract.items_needed.map((item, i) => (
                <div key={i} className="flex items-center gap-3 bg-white/5 rounded-lg px-3 py-2 border border-white/5">
                  <span className="w-5 h-5 rounded-full bg-white/10 flex items-center justify-center text-[10px] text-gray-500 shrink-0">{i + 1}</span>
                  <span className="text-sm text-gray-300">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Wikelo;
