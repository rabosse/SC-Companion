import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Search, ExternalLink, Loader2, Paintbrush, MapPin, DollarSign, SlidersHorizontal, ArrowUpDown, ChevronUp, ChevronDown, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API = process.env.REACT_APP_BACKEND_URL;

const ACQ_COLORS = {
  'In-Game': '#00FF9D', 'RSI Store': '#00D4FF', 'Event Reward': '#FFAE00',
  'Limited Edition': '#A855F7', 'Subscriber': '#FF6B9D', 'Special': '#888', 'Unknown': '#555',
};

/** A paint is purchasable in-game only if it has actual location data */
const isPurchasable = (paint) => paint.locations?.length > 0;

const SeriesDetailModal = ({ series, onClose }) => {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const paint = series.paints[selectedIdx];
  const acqColor = ACQ_COLORS[paint?.acquisition] || '#888';
  const locations = paint?.locations || [];
  const bestPrice = locations.filter(l => l.price > 0).sort((a, b) => a.price - b.price)[0];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={onClose} data-testid="paint-detail-modal">
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
        className="glass-panel rounded-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col"
        onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="flex items-start justify-between p-6 pb-0 shrink-0">
          <div>
            <h2 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}
              data-testid="modal-series-name">{series.series}</h2>
            <p className="text-sm text-gray-400">{series.paint_count} paints available</p>
          </div>
          <button onClick={onClose} data-testid="close-paint-detail"
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 pt-4 space-y-5">
          {/* Paint selector pills */}
          <div className="flex flex-wrap gap-1.5" data-testid="modal-paint-selector">
            {series.paints.map((p, idx) => {
              const pc = ACQ_COLORS[p.acquisition] || '#888';
              const isSelected = idx === selectedIdx;
              const hasBuyableLocation = p.locations?.some(l => l.price > 0);
              return (
                <button key={idx} onClick={() => setSelectedIdx(idx)}
                  data-testid={`modal-paint-btn-${idx}`}
                  className={`text-[11px] px-3 py-1.5 rounded-lg border font-semibold transition-all ${
                    isSelected
                      ? 'text-white ring-1 ring-offset-1 ring-offset-[#0d1117]'
                      : hasBuyableLocation
                        ? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-400 hover:bg-emerald-500/10'
                        : 'border-white/10 bg-white/[0.03] text-gray-500 hover:text-gray-300 hover:bg-white/[0.06]'
                  }`}
                  style={isSelected ? { borderColor: `${pc}50`, background: `${pc}15`, color: pc, ringColor: pc } : {}}>
                  {p.name}
                </button>
              );
            })}
          </div>

          {/* Selected paint badges */}
          <div className="flex flex-wrap gap-2">
            <span className="px-3 py-1 rounded-lg text-xs font-bold border"
              style={{ color: acqColor, background: `${acqColor}20`, borderColor: `${acqColor}30` }}>
              {paint?.acquisition}
            </span>
            {isPurchasable(paint) && bestPrice && (
              <span className="px-3 py-1 rounded-lg text-xs font-bold border text-emerald-400 bg-emerald-500/10 border-emerald-500/20">
                {bestPrice.price.toLocaleString()} aUEC
              </span>
            )}
            {paint?.price_usd && (
              <span className="px-3 py-1 rounded-lg text-xs font-bold border text-cyan-400 bg-cyan-500/10 border-cyan-500/20">
                ${paint.price_usd.toFixed(2)} USD
              </span>
            )}
          </div>

          {/* Image */}
          {paint?.image_url && (
            <div className="rounded-xl overflow-hidden bg-black/40 border border-white/5">
              <AnimatePresence mode="wait">
                <motion.img key={paint.image_url} src={paint.image_url} alt={paint.name}
                  className="w-full h-64 object-contain"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  data-testid="modal-paint-image"
                  onError={(e) => { e.target.onerror = null; e.target.parentElement.style.display = 'none'; }} />
              </AnimatePresence>
            </div>
          )}

          {/* Description */}
          {paint?.description && (
            <div>
              <h3 className="text-xs text-gray-500 uppercase font-bold mb-2">Description</h3>
              <p className="text-sm text-gray-300 leading-relaxed" data-testid="modal-description">{paint.description}</p>
            </div>
          )}

          {/* RSI Store link */}
          {paint?.store_url && (
            <a href={paint.store_url} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/20 transition-all text-sm font-semibold"
              data-testid="modal-store-link">
              <ExternalLink className="w-4 h-4" /> View on RSI Pledge Store
            </a>
          )}

          {/* Purchase Locations */}
          <div>
            <h3 className="text-xs text-gray-500 uppercase font-bold mb-3 flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5" /> In-Game Purchase Locations
            </h3>
            {isPurchasable(paint) ? (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {locations.map((loc, i) => (
                  <div key={i} className={`flex items-center justify-between text-sm p-2.5 rounded-lg ${bestPrice && loc.price === bestPrice.price ? 'bg-green-500/10 border border-green-500/20' : 'bg-white/5'}`}
                    data-testid={`paint-location-${i}`}>
                    <span className="text-gray-300 flex-1 mr-4">{loc.store || loc.location || loc.name}</span>
                    {loc.price > 0 && (
                      <span className={`font-bold whitespace-nowrap ${bestPrice && loc.price === bestPrice.price ? 'text-green-400' : 'text-yellow-400'}`}
                        style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                        {loc.price.toLocaleString()} aUEC
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 italic">Not purchasable in-game</p>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default function Liveries() {
  const { token } = useAuth();
  const [liveries, setLiveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [fleetOnly, setFleetOnly] = useState(false);
  const [fleetShipIds, setFleetShipIds] = useState([]);
  const [acqFilter, setAcqFilter] = useState('all');
  const [buyableOnly, setBuyableOnly] = useState(false);
  const [sortBy, setSortBy] = useState('series');
  const [sortAsc, setSortAsc] = useState(true);
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    let interval;
    const fetchData = async () => {
      try {
        const [livRes, fleetRes] = await Promise.all([
          axios.get(`${API}/api/liveries`),
          axios.get(`${API}/api/fleet/my`, { headers: { Authorization: `Bearer ${token}` } }),
        ]);
        if (livRes.data.loading) {
          if (!interval) {
            interval = setInterval(async () => {
              const r = await axios.get(`${API}/api/liveries`);
              if (!r.data.loading) {
                setLiveries(r.data.data || []);
                setLoading(false);
                clearInterval(interval);
              }
            }, 5000);
          }
        } else {
          setLiveries(livRes.data.data || []);
          setLoading(false);
        }
        setFleetShipIds((fleetRes.data.data || []).map(f => f.ship_id));
      } catch {
        setLoading(false);
      }
    };
    fetchData();
    return () => { if (interval) clearInterval(interval); };
  }, [token]);

  const fleetSet = useMemo(() => new Set(fleetShipIds.map(id => id.toLowerCase().replace(/-/g, ' '))), [fleetShipIds]);

  // Enrich series with summary info
  const enriched = useMemo(() => {
    return liveries.map(s => {
      const purchasablePaints = s.paints.filter(isPurchasable);
      const allLocations = purchasablePaints.flatMap(p => p.locations || []);
      const bestPrice = allLocations.filter(l => l.price > 0).sort((a, b) => a.price - b.price)[0];
      const acqSet = new Set(s.paints.map(p => p.acquisition));
      const firstImagePaint = s.paints.find(p => p.image_url) || s.paints[0];
      return { ...s, purchasablePaints, bestPrice, acqSet, firstImagePaint };
    });
  }, [liveries]);

  const filtered = useMemo(() => {
    let result = enriched;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(s =>
        s.series.toLowerCase().includes(q) ||
        s.paints.some(p => p.name.toLowerCase().includes(q))
      );
    }
    if (acqFilter !== 'all') {
      result = result.filter(s => s.acqSet.has(acqFilter));
    }
    if (buyableOnly) {
      result = result.filter(s => s.purchasablePaints.length > 0);
    }
    if (fleetOnly) {
      result = result.filter(s => {
        const sl = s.series.toLowerCase();
        return [...fleetSet].some(fid => fid.includes(sl) || sl.includes(fid.split(' ')[0]));
      });
    }
    const dir = sortAsc ? 1 : -1;
    const sortFns = {
      series: (a, b) => dir * a.series.localeCompare(b.series),
      paints: (a, b) => dir * (a.paint_count - b.paint_count),
      price: (a, b) => dir * ((a.bestPrice?.price || 999999) - (b.bestPrice?.price || 999999)),
    };
    if (sortFns[sortBy]) result = [...result].sort(sortFns[sortBy]);
    return result;
  }, [enriched, search, acqFilter, buyableOnly, fleetOnly, fleetSet, sortBy, sortAsc]);

  const acqTypes = useMemo(() => {
    const counts = {};
    for (const s of liveries) {
      for (const p of s.paints) {
        counts[p.acquisition] = (counts[p.acquisition] || 0) + 1;
      }
    }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [liveries]);

  const totalPaints = liveries.reduce((sum, s) => sum + s.paint_count, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="liveries-loading">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading livery data from starcitizen.tools...</p>
          <p className="text-xs text-gray-600 mt-1">This may take a moment on first load</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="liveries-page">
      <div>
        <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}
          data-testid="liveries-title">
          Livery Catalog
        </h1>
        <p className="text-gray-400 text-sm" data-testid="livery-count">
          {filtered.length} ships · {totalPaints} paints
        </p>
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-2xl p-5 space-y-4" data-testid="filters-section">
        <div className="flex items-center gap-2 text-sm font-bold text-gray-400 uppercase tracking-wider">
          <SlidersHorizontal className="w-4 h-4" /> Filters
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="relative sm:col-span-2 lg:col-span-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Search ship or paint..." data-testid="liveries-search"
              className="w-full pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all" />
          </div>
          <select value={acqFilter} onChange={e => setAcqFilter(e.target.value)} data-testid="acq-filter"
            className="px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500 transition-all">
            <option value="all" className="bg-gray-900">All Acquisition Types</option>
            {acqTypes.map(([type, count]) => (
              <option key={type} value={type} className="bg-gray-900">{type} ({count})</option>
            ))}
          </select>
          <div className="flex gap-1.5">
            <button onClick={() => setFleetOnly(false)} data-testid="fleet-toggle-all"
              className={`flex-1 px-3 py-2.5 rounded-lg text-xs font-bold uppercase transition-all ${!fleetOnly ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'}`}>
              All Ships
            </button>
            <button onClick={() => setFleetOnly(true)} data-testid="fleet-toggle-fleet"
              className={`flex-1 px-3 py-2.5 rounded-lg text-xs font-bold uppercase transition-all ${fleetOnly ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'}`}>
              Fleet Only
            </button>
          </div>
          <button onClick={() => setBuyableOnly(b => !b)} data-testid="buyable-toggle"
            className={`px-3 py-2.5 rounded-lg text-xs font-bold uppercase transition-all flex items-center gap-1.5 ${buyableOnly ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'}`}>
            <MapPin className="w-3.5 h-3.5" /> In-Game Buyable
          </button>
        </div>
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 font-semibold uppercase">Sort:</span>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} data-testid="sort-dropdown"
              className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-cyan-500 transition-all">
              <option value="series" className="bg-gray-900">Ship Name</option>
              <option value="paints" className="bg-gray-900">Paint Count</option>
              <option value="price" className="bg-gray-900">Best Price</option>
            </select>
            <button onClick={() => setSortAsc(!sortAsc)} data-testid="sort-direction-toggle"
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/5 border border-white/10 text-gray-400 hover:text-white transition-all">
              <ArrowUpDown className="w-3.5 h-3.5" />
              {sortAsc ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              <span>{sortAsc ? 'ASC' : 'DESC'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Ship Series Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5" data-testid="liveries-grid">
        {filtered.map((series, index) => {
          const hasInGame = series.purchasablePaints.length > 0;
          const previewPaint = series.firstImagePaint;

          return (
            <motion.div key={series.series}
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(index * 0.015, 0.5) }}
              className="glass-panel rounded-2xl p-5 hover:scale-[1.02] transition-transform duration-300 cursor-pointer"
              data-testid={`series-card-${series.series.toLowerCase().replace(/\s+/g, '-')}`}
              onClick={() => setDetail(series)}>

              {/* Top row: icon + paint count */}
              <div className="flex items-center justify-between mb-3">
                <Paintbrush className="w-6 h-6 text-cyan-500" />
                <span className="text-[10px] font-bold px-2 py-0.5 rounded border border-white/10 bg-white/5 text-gray-400">
                  {series.paint_count} {series.paint_count === 1 ? 'paint' : 'paints'}
                </span>
              </div>

              {/* Ship series name */}
              <h3 className="text-base font-bold text-white mb-1 truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}
                data-testid={`series-name-${index}`}>{series.series}</h3>

              {/* Acquisition types summary */}
              <div className="flex flex-wrap items-center gap-1 mb-3">
                {[...series.acqSet].map(acq => {
                  const c = ACQ_COLORS[acq] || '#888';
                  return (
                    <span key={acq} className="text-[9px] font-semibold px-1.5 py-0.5 rounded-full"
                      style={{ color: c, background: `${c}12` }}>
                      {acq}
                    </span>
                  );
                })}
              </div>

              {/* Image preview */}
              {previewPaint?.image_url && (
                <div className="mb-3 rounded-xl overflow-hidden bg-black/30 border border-white/5 h-32">
                  <img src={previewPaint.image_url} alt={series.series} className="w-full h-full object-cover"
                    onError={(e) => { e.target.onerror = null; e.target.parentElement.style.display = 'none'; }} />
                </div>
              )}

              {/* Purchase info */}
              <div className="border-t border-white/10 pt-3 space-y-1.5">
                {hasInGame ? (
                  <>
                    <div className="flex items-center gap-2 text-xs" data-testid={`series-available-${index}`}>
                      <MapPin className="w-3.5 h-3.5 shrink-0 text-green-400" />
                      <span className="text-green-400 font-medium">Available in-game</span>
                      {series.bestPrice && (
                        <span className="text-green-400 font-bold ml-auto whitespace-nowrap" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                          from {series.bestPrice.price.toLocaleString()} aUEC
                        </span>
                      )}
                    </div>
                    {/* Show top 2 locations from best-priced paint */}
                    {series.purchasablePaints[0]?.locations?.slice(0, 2).map((loc, li) => (
                      <div key={li} className="flex items-center gap-2 text-[10px] pl-5">
                        <span className="text-gray-500 truncate">{loc.store || loc.location || loc.name}</span>
                        {loc.price > 0 && (
                          <span className="text-gray-400 font-semibold whitespace-nowrap ml-auto">{loc.price.toLocaleString()} aUEC</span>
                        )}
                      </div>
                    ))}
                    {(series.purchasablePaints[0]?.locations?.length || 0) > 2 && (
                      <p className="text-[10px] text-gray-600 pl-5">+{series.purchasablePaints[0].locations.length - 2} more locations</p>
                    )}
                  </>
                ) : (
                  <div className="flex items-center gap-2 text-xs">
                    <DollarSign className="w-3.5 h-3.5 shrink-0 text-gray-600" />
                    <span className="text-gray-600">Not purchasable in-game</span>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12" data-testid="no-paints-message">
          <Paintbrush className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No ships found matching your criteria</p>
        </div>
      )}

      {/* Detail Modal */}
      <AnimatePresence>
        {detail && <SeriesDetailModal series={detail} onClose={() => setDetail(null)} />}
      </AnimatePresence>
    </div>
  );
}
