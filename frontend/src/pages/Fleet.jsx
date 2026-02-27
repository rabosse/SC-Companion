import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Trash2, Search, TrendingUp, Package, Users, DollarSign, Plus, Check, X, Ship } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import SpaceshipIcon from '../components/SpaceshipIcon';

const Fleet = () => {
  const { API } = useAuth();
  const [fleet, setFleet] = useState([]);
  const [filteredFleet, setFilteredFleet] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [ships, setShips] = useState([]);
  const [showImport, setShowImport] = useState(false);

  const fetchFleet = async () => {
    try {
      const [fleetRes, shipsRes] = await Promise.all([
        axios.get(`${API}/fleet/my`),
        axios.get(`${API}/ships`)
      ]);
      setFleet(fleetRes.data.data || []);
      setFilteredFleet(fleetRes.data.data || []);
      setShips(shipsRes.data.data || []);
    } catch {
      toast.error('Failed to load your fleet');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchFleet(); }, [API]);

  useEffect(() => {
    if (searchQuery) {
      setFilteredFleet(fleet.filter(item =>
        item.ship_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.manufacturer.toLowerCase().includes(searchQuery.toLowerCase())
      ));
    } else {
      setFilteredFleet(fleet);
    }
  }, [searchQuery, fleet]);

  const removeFromFleet = async (fleetId) => {
    try {
      await axios.delete(`${API}/fleet/${fleetId}`);
      toast.success('Removed from your fleet');
      await fetchFleet();
    } catch {
      toast.error('Failed to remove from fleet');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading your fleet...</p>
        </div>
      </div>
    );
  }

  const fleetShipIds = new Set(fleet.map(f => f.ship_id));

  const fleetStats = fleet.reduce((stats, item) => {
    const shipData = ships.find(s => s.id === item.ship_id);
    if (shipData) {
      stats.totalCargo += shipData.cargo || 0;
      stats.totalCrew += (shipData.crew_max || parseInt(shipData.crew) || 0);
      stats.totalValue += shipData.price_auec || shipData.price || 0;
    }
    return stats;
  }, { totalCargo: 0, totalCrew: 0, totalValue: 0 });

  const statsCards = [
    { icon: SpaceshipIcon, label: 'Total Ships', value: fleet.length, color: '#00D4FF' },
    { icon: Package, label: 'Total Cargo (SCU)', value: fleetStats.totalCargo.toLocaleString(), color: '#D4AF37' },
    { icon: Users, label: 'Max Crew', value: fleetStats.totalCrew, color: '#00FF9D' },
    { icon: DollarSign, label: 'Fleet Value (aUEC)', value: fleetStats.totalValue.toLocaleString(), color: '#FFAE00' },
  ];

  return (
    <div className="space-y-8" data-testid="fleet-page">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            My Fleet
          </h1>
          <p className="text-gray-400">{fleet.length} ships in your collection</p>
        </div>
        <button
          onClick={() => setShowImport(true)}
          data-testid="quick-import-btn"
          className="btn-origin flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Quick Import
        </button>
      </div>

      {fleet.length > 0 && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {statsCards.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }}
                  className="glass-panel rounded-2xl p-6" data-testid={`fleet-stat-${stat.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <Icon className="w-8 h-8" style={{ color: stat.color }} />
                  </div>
                  <div className="text-3xl font-bold mb-1" style={{ fontFamily: 'Rajdhani, sans-serif', color: stat.color }}>
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-400">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>

          <div className="glass-panel rounded-2xl p-6">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search your fleet..." data-testid="search-input"
                className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all" />
            </div>
          </div>
        </>
      )}

      {fleet.length === 0 && (
        <div className="text-center py-16" data-testid="empty-fleet">
          <div className="glass-panel rounded-3xl p-12 max-w-2xl mx-auto">
            <SpaceshipIcon className="w-24 h-24 mx-auto mb-6 text-gray-600" />
            <h2 className="text-3xl font-bold mb-4" style={{ fontFamily: 'Rajdhani, sans-serif' }}>Your Fleet is Empty</h2>
            <p className="text-gray-400 mb-8">Use Quick Import to add multiple ships at once, or browse the ship database</p>
            <div className="flex gap-4 justify-center flex-wrap">
              <button onClick={() => setShowImport(true)} className="btn-origin">
                <Plus className="w-5 h-5 inline mr-2" />Quick Import
              </button>
              <Link to="/ships"><button className="px-6 py-3 border border-cyan-500/30 text-cyan-500 rounded-xl hover:bg-cyan-500/10 transition-all font-semibold">Browse Ships</button></Link>
            </div>
          </div>
        </div>
      )}

      {filteredFleet.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFleet.map((item, index) => {
            const shipData = ships.find(s => s.id === item.ship_id);
            return (
              <motion.div key={item.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}
                className="glass-panel rounded-2xl overflow-hidden ship-card group" data-testid={`fleet-item-${item.id}`}
              >
                <Link to={`/ships/${item.ship_id}`}>
                  <div className="h-48 relative overflow-hidden bg-gradient-to-br from-cyan-500/20 to-blue-600/20">
                    {shipData?.image ? (
                      <img src={shipData.image} alt={item.ship_name} className="w-full h-full object-cover" onError={e => { e.target.onerror = null; e.target.style.display = 'none'; }} />
                    ) : null}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                  </div>
                </Link>
                <div className="p-6">
                  <Link to={`/ships/${item.ship_id}`}>
                    <h3 className="text-xl font-bold text-white hover:text-cyan-500 transition-colors mb-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                      {item.ship_name}
                    </h3>
                  </Link>
                  <p className="text-sm text-gray-400 mb-2">{item.manufacturer}</p>
                  {shipData?.price_auec > 0 && (
                    <p className="text-sm text-yellow-400 font-semibold mb-2">{shipData.price_auec.toLocaleString()} aUEC</p>
                  )}
                  <div className="text-xs text-gray-600 mb-4">Added: {new Date(item.added_at).toLocaleDateString()}</div>
                  <button onClick={() => removeFromFleet(item.id)} data-testid={`remove-from-fleet-${item.id}`}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-full border border-red-500/30 text-red-500 hover:bg-red-500 hover:text-white transition-all"
                    style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600 }}
                  >
                    <Trash2 className="w-4 h-4" /><span>Remove</span>
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {fleet.length > 0 && filteredFleet.length === 0 && (
        <div className="text-center py-12" data-testid="no-results-message">
          <SpaceshipIcon className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <p className="text-gray-400">No ships found matching your search</p>
        </div>
      )}

      {/* Quick Import Modal */}
      <AnimatePresence>
        {showImport && (
          <QuickImportModal
            ships={ships}
            fleetShipIds={fleetShipIds}
            API={API}
            onClose={() => setShowImport(false)}
            onImported={fetchFleet}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

const QuickImportModal = ({ ships, fleetShipIds, API, onClose, onImported }) => {
  const [selected, setSelected] = useState(new Set());
  const [search, setSearch] = useState('');
  const [importing, setImporting] = useState(false);
  const [filterMfg, setFilterMfg] = useState('all');
  const [filterSize, setFilterSize] = useState('all');

  const manufacturers = useMemo(() => {
    const mfgs = [...new Set(ships.map(s => s.manufacturer))].filter(Boolean).sort();
    return ['all', ...mfgs];
  }, [ships]);

  const sizes = ['all', 'Snub', 'Small', 'Medium', 'Large', 'Capital'];

  const filtered = useMemo(() => {
    let result = ships;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(s => s.name.toLowerCase().includes(q) || s.manufacturer.toLowerCase().includes(q));
    }
    if (filterMfg !== 'all') result = result.filter(s => s.manufacturer === filterMfg);
    if (filterSize !== 'all') result = result.filter(s => s.size === filterSize);
    return result;
  }, [ships, search, filterMfg, filterSize]);

  const toggle = (shipId) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(shipId)) next.delete(shipId);
      else next.add(shipId);
      return next;
    });
  };

  const selectAll = () => {
    const ids = filtered.filter(s => !fleetShipIds.has(s.id)).map(s => s.id);
    setSelected(new Set(ids));
  };

  const importShips = async () => {
    if (selected.size === 0) {
      toast.error('Select at least one ship');
      return;
    }
    setImporting(true);
    try {
      const toAdd = ships.filter(s => selected.has(s.id));
      const res = await axios.post(`${API}/fleet/bulk-add`, {
        ships: toAdd.map(s => ({ id: s.id, name: s.name, manufacturer: s.manufacturer }))
      });
      toast.success(res.data.message);
      onClose();
      await onImported();
    } catch {
      toast.error('Import failed');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}
        className="glass-panel rounded-3xl max-w-5xl w-full max-h-[85vh] overflow-hidden flex flex-col" data-testid="quick-import-modal"
      >
        <div className="p-6 border-b border-white/10 space-y-4 shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
                Quick Fleet Import
              </h2>
              <p className="text-sm text-gray-400">Select the ships you own to add them all at once</p>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg"><X className="w-6 h-6 text-gray-400" /></button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search ships..."
                data-testid="import-search" className="w-full pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all" autoFocus />
            </div>
            <select value={filterMfg} onChange={e => setFilterMfg(e.target.value)} data-testid="import-mfg-filter"
              className="px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:outline-none focus:border-cyan-500 transition-all">
              {manufacturers.map(m => <option key={m} value={m} className="bg-gray-900">{m === 'all' ? 'All Manufacturers' : m}</option>)}
            </select>
            <select value={filterSize} onChange={e => setFilterSize(e.target.value)} data-testid="import-size-filter"
              className="px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:outline-none focus:border-cyan-500 transition-all">
              {sizes.map(s => <option key={s} value={s} className="bg-gray-900">{s === 'all' ? 'All Sizes' : s}</option>)}
            </select>
          </div>

          <div className="flex items-center justify-between">
            <button onClick={selectAll} data-testid="select-all-btn" className="text-sm text-cyan-500 hover:text-cyan-400 transition-colors">
              Select all visible ({filtered.filter(s => !fleetShipIds.has(s.id)).length})
            </button>
            <span className="text-sm text-gray-400">{selected.size} selected</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {filtered.map(ship => {
              const inFleet = fleetShipIds.has(ship.id);
              const isSelected = selected.has(ship.id);
              return (
                <button key={ship.id} onClick={() => !inFleet && toggle(ship.id)} disabled={inFleet}
                  data-testid={`import-ship-${ship.id}`}
                  className={`rounded-xl p-2 text-left transition-all border ${
                    inFleet ? 'opacity-40 cursor-not-allowed border-white/5 bg-white/[0.02]'
                    : isSelected ? 'border-cyan-500 bg-cyan-500/10' : 'border-white/10 bg-white/[0.02] hover:border-white/20'
                  }`}
                >
                  <div className="h-16 bg-gradient-to-br from-cyan-500/10 to-blue-600/10 rounded-lg overflow-hidden mb-2 relative">
                    {ship.image ? (
                      <img src={ship.image} alt={ship.name} className="w-full h-full object-cover" onError={e => { e.target.onerror = null; e.target.style.display = 'none'; }} />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center"><Ship className="w-6 h-6 text-cyan-500/20" /></div>
                    )}
                    {isSelected && (
                      <div className="absolute top-1 right-1 w-5 h-5 rounded-full bg-cyan-500 flex items-center justify-center">
                        <Check className="w-3 h-3 text-black" />
                      </div>
                    )}
                    {inFleet && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                        <span className="text-[10px] text-green-400 font-bold">IN FLEET</span>
                      </div>
                    )}
                  </div>
                  <div className="font-bold text-white text-xs truncate">{ship.name}</div>
                  <div className="text-[10px] text-gray-500 truncate">{ship.manufacturer}</div>
                </button>
              );
            })}
          </div>
          {filtered.length === 0 && <p className="text-center text-gray-500 py-8">No ships found</p>}
        </div>

        <div className="p-4 border-t border-white/10 flex items-center justify-between shrink-0">
          <span className="text-sm text-gray-400">{selected.size} ships selected</span>
          <div className="flex gap-3">
            <button onClick={onClose} className="px-6 py-2.5 bg-white/5 text-gray-400 rounded-xl hover:bg-white/10 transition-colors">Cancel</button>
            <button onClick={importShips} disabled={importing || selected.size === 0} data-testid="confirm-import-btn"
              className="px-6 py-2.5 rounded-xl font-bold text-black disabled:opacity-50 transition-all"
              style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}
            >
              {importing ? 'Importing...' : `Import ${selected.size} Ships`}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Fleet;
