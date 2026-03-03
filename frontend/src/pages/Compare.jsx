import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Ship, X, Plus, ArrowLeft, Search } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';

const MAX_COMPARE = 5;

const Compare = () => {
  const { API } = useAuth();
  const [ships, setShips] = useState([]);
  const [compareList, setCompareList] = useState([]);
  const [showSelector, setShowSelector] = useState(false);
  const [selectorSearch, setSelectorSearch] = useState('');

  useEffect(() => {
    fetchShips();
    const saved = localStorage.getItem('compareShips');
    if (saved) {
      try { setCompareList(JSON.parse(saved)); } catch { /* ignore */ }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchShips = async () => {
    try {
      const response = await axios.get(`${API}/ships`);
      setShips(response.data.data || []);
    } catch {
      toast.error('Failed to load ships');
    }
  };

  const addToCompare = (ship) => {
    if (compareList.length >= MAX_COMPARE) {
      toast.error(`Maximum ${MAX_COMPARE} ships can be compared`);
      return;
    }
    if (compareList.find(s => s.id === ship.id)) {
      toast.error('Ship already in comparison');
      return;
    }
    const newList = [...compareList, ship];
    setCompareList(newList);
    localStorage.setItem('compareShips', JSON.stringify(newList));
    setShowSelector(false);
    setSelectorSearch('');
    toast.success(`${ship.name} added`);
  };

  const removeFromCompare = (shipId) => {
    const newList = compareList.filter(s => s.id !== shipId);
    setCompareList(newList);
    localStorage.setItem('compareShips', JSON.stringify(newList));
  };

  const clearAll = () => {
    setCompareList([]);
    localStorage.removeItem('compareShips');
  };

  const filteredShips = useMemo(() => {
    const available = ships.filter(s => !compareList.find(c => c.id === s.id));
    if (!selectorSearch) return available;
    const q = selectorSearch.toLowerCase();
    return available.filter(s =>
      s.name.toLowerCase().includes(q) || s.manufacturer.toLowerCase().includes(q)
    );
  }, [ships, compareList, selectorSearch]);

  // Get crew display value
  const crewVal = (ship) => {
    if (ship.crew_max) return `${ship.crew_min}-${ship.crew_max}`;
    return ship.crew || 'N/A';
  };

  const specs = [
    { label: 'Manufacturer', get: s => s.manufacturer },
    { label: 'Size Class', get: s => s.size },
    { label: 'Role', get: s => s.role || 'Multi-role' },
    { label: 'Crew', get: s => crewVal(s) },
    { label: 'Cargo (SCU)', get: s => s.cargo ?? 'N/A', numeric: true },
    { label: 'Length (m)', get: s => s.length || 'N/A', numeric: true },
    { label: 'Beam (m)', get: s => s.beam || 'N/A', numeric: true },
    { label: 'Height (m)', get: s => s.height || 'N/A', numeric: true },
    { label: 'Mass (kg)', get: s => s.mass ? s.mass.toLocaleString() : 'N/A', raw: s => s.mass || 0 },
    { label: 'SCM Speed (m/s)', get: s => s.max_speed || 'N/A', numeric: true, highlight: 'high' },
    { label: 'Boost Speed (m/s)', get: s => s.max_speed_boost || 'N/A', numeric: true, highlight: 'high' },
    { label: 'Health', get: s => s.health ? s.health.toLocaleString() : 'N/A', raw: s => s.health || 0, highlight: 'high' },
    { label: 'Shield HP', get: s => s.shield_hp ? s.shield_hp.toLocaleString() : 'N/A', raw: s => s.shield_hp || 0, highlight: 'high' },
    { label: 'Est. Price (UEC)', get: s => s.price ? s.price.toLocaleString() : 'TBD', raw: s => s.price || 0 },
  ];

  // Find the best value for highlighting in a row
  const getBestIndex = (spec) => {
    if (!spec.highlight || compareList.length < 2) return -1;
    const rawFn = spec.raw || (s => {
      const v = spec.get(s);
      return typeof v === 'number' ? v : parseFloat(v) || 0;
    });
    let bestIdx = 0;
    let bestVal = rawFn(compareList[0]);
    for (let i = 1; i < compareList.length; i++) {
      const v = rawFn(compareList[i]);
      if (spec.highlight === 'high' && v > bestVal) { bestVal = v; bestIdx = i; }
      if (spec.highlight === 'low' && v < bestVal) { bestVal = v; bestIdx = i; }
    }
    return bestVal > 0 ? bestIdx : -1;
  };

  // Stat bar for numeric comparisons
  const StatBar = ({ value, maxVal, color = '#00D4FF' }) => {
    const pct = maxVal > 0 ? Math.min((value / maxVal) * 100, 100) : 0;
    return (
      <div className="w-full h-1.5 bg-white/10 rounded-full mt-1">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    );
  };

  return (
    <div className="space-y-8" data-testid="compare-page">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Ship Comparison
          </h1>
          <p className="text-gray-400">Compare up to {MAX_COMPARE} ships side by side</p>
        </div>
        <div className="flex items-center gap-3">
          {compareList.length > 0 && (
            <button onClick={clearAll} data-testid="clear-all-btn" className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors text-sm">
              Clear All
            </button>
          )}
          <Link to="/ships" className="text-gray-400 hover:text-cyan-500 transition-colors flex items-center gap-1">
            <ArrowLeft className="w-5 h-5" /> Ships
          </Link>
        </div>
      </div>

      {compareList.length === 0 ? (
        <div className="text-center py-16">
          <div className="glass-panel rounded-3xl p-12 max-w-2xl mx-auto">
            <Ship className="w-24 h-24 text-gray-600 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
              No Ships Selected
            </h2>
            <p className="text-gray-400 mb-8">Add ships to compare their specifications</p>
            <button onClick={() => setShowSelector(true)} data-testid="add-ship-btn" className="btn-origin">
              <Plus className="w-5 h-5 inline mr-2" />Add Ship
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="flex justify-end mb-4">
            {compareList.length < MAX_COMPARE && (
              <button onClick={() => setShowSelector(true)} data-testid="add-ship-btn" className="btn-origin">
                <Plus className="w-5 h-5 inline mr-2" />
                Add Ship ({compareList.length}/{MAX_COMPARE})
              </button>
            )}
          </div>

          <div className="glass-panel rounded-3xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="compare-table">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="p-4 md:p-6 text-left text-gray-400 font-semibold min-w-[150px]">Specification</th>
                    {compareList.map(ship => (
                      <th key={ship.id} className="p-4 md:p-6 text-center relative min-w-[180px]" data-testid={`compare-ship-${ship.id}`}>
                        <button
                          onClick={() => removeFromCompare(ship.id)}
                          data-testid={`remove-ship-${ship.id}`}
                          className="absolute top-2 right-2 p-1 rounded-full bg-red-500/20 hover:bg-red-500 text-red-500 hover:text-white transition-all z-10"
                        >
                          <X className="w-4 h-4" />
                        </button>
                        <div className="mb-3 h-28 bg-gradient-to-br from-cyan-500/10 to-blue-600/10 rounded-xl overflow-hidden">
                          {ship.image ? (
                            <img src={ship.image} alt={ship.name} className="w-full h-full object-cover" onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }} />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center"><Ship className="w-10 h-10 text-cyan-500/30" /></div>
                          )}
                        </div>
                        <Link to={`/ships/${ship.id}`} className="text-lg font-bold text-cyan-500 hover:text-cyan-400 transition-colors" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                          {ship.name}
                        </Link>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {specs.map((spec, idx) => {
                    const bestIdx = getBestIndex(spec);
                    // For stat bars, get max value in row
                    const rawFn = spec.raw || (s => { const v = spec.get(s); return typeof v === 'number' ? v : parseFloat(v) || 0; });
                    const maxVal = spec.numeric || spec.raw ? Math.max(...compareList.map(s => rawFn(s)), 1) : 0;

                    return (
                      <tr key={spec.label} className={idx % 2 === 0 ? 'bg-white/[0.02]' : ''}>
                        <td className="p-3 md:p-4 text-gray-400 font-medium text-sm">{spec.label}</td>
                        {compareList.map((ship, i) => {
                          const val = spec.get(ship);
                          const isBest = i === bestIdx;
                          const numVal = rawFn(ship);
                          return (
                            <td key={ship.id} className="p-3 md:p-4 text-center">
                              <span className={`font-semibold text-sm ${isBest ? 'text-green-400' : 'text-white'}`}>
                                {val}
                              </span>
                              {(spec.numeric || spec.raw) && numVal > 0 && (
                                <StatBar value={numVal} maxVal={maxVal} color={isBest ? '#00FF9D' : '#00D4FF'} />
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Ship Selector Modal */}
      {showSelector && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={(e) => { if (e.target === e.currentTarget) { setShowSelector(false); setSelectorSearch(''); }}}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel rounded-3xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
            data-testid="ship-selector-modal"
          >
            <div className="p-6 border-b border-white/10 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
                  Select Ship to Compare
                </h2>
                <button onClick={() => { setShowSelector(false); setSelectorSearch(''); }} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                  <X className="w-6 h-6 text-gray-400" />
                </button>
              </div>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  value={selectorSearch}
                  onChange={e => setSelectorSearch(e.target.value)}
                  placeholder="Search ships by name or manufacturer..."
                  data-testid="compare-search-input"
                  className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all"
                  autoFocus
                />
              </div>
            </div>
            <div className="p-6 overflow-y-auto max-h-[55vh]">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {filteredShips.map(ship => (
                  <button
                    key={ship.id}
                    onClick={() => addToCompare(ship)}
                    data-testid={`select-ship-${ship.id}`}
                    className="glass-panel rounded-xl p-3 hover:border-cyan-500/50 transition-all text-left group"
                  >
                    <div className="h-20 bg-gradient-to-br from-cyan-500/10 to-blue-600/10 rounded-lg overflow-hidden mb-2">
                      {ship.image ? (
                        <img src={ship.image} alt={ship.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform" onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }} />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center"><Ship className="w-8 h-8 text-cyan-500/20" /></div>
                      )}
                    </div>
                    <div className="font-bold text-white text-sm truncate">{ship.name}</div>
                    <div className="text-xs text-gray-500 truncate">{ship.manufacturer}</div>
                  </button>
                ))}
              </div>
              {filteredShips.length === 0 && (
                <p className="text-center text-gray-500 py-8">No ships found</p>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Compare;
