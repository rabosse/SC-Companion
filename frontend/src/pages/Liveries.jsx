import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Search, ExternalLink, Loader2, Paintbrush, Filter } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API = process.env.REACT_APP_BACKEND_URL;

const ACQUISITION_COLORS = {
  'In-Game': { border: 'border-emerald-500/40', bg: 'bg-emerald-500/15', text: 'text-emerald-400' },
  'RSI Store': { border: 'border-cyan-500/40', bg: 'bg-cyan-500/15', text: 'text-cyan-400' },
  'Event Reward': { border: 'border-amber-500/40', bg: 'bg-amber-500/15', text: 'text-amber-400' },
  'Limited Edition': { border: 'border-purple-500/40', bg: 'bg-purple-500/15', text: 'text-purple-400' },
  'Subscriber': { border: 'border-pink-500/40', bg: 'bg-pink-500/15', text: 'text-pink-400' },
  'Special': { border: 'border-white/20', bg: 'bg-white/5', text: 'text-gray-400' },
  'Unknown': { border: 'border-white/10', bg: 'bg-white/5', text: 'text-gray-500' },
};

const PaintViewer = ({ series, fleetShipIds, fleetOnly }) => {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const paint = series.paints[selectedIdx];
  const colors = ACQUISITION_COLORS[paint?.acquisition] || ACQUISITION_COLORS['Unknown'];

  // Check if this series matches any fleet ship (fuzzy match on series name)
  const seriesLower = series.series.toLowerCase();
  const inFleet = fleetShipIds.some(id => {
    const idLower = id.toLowerCase().replace(/-/g, ' ');
    return idLower.includes(seriesLower) || seriesLower.includes(idLower.split(' ')[0]);
  });

  if (fleetOnly && !inFleet) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-2xl overflow-hidden group"
      data-testid={`livery-card-${series.series.toLowerCase().replace(/\s+/g, '-')}`}
    >
      {/* Image area */}
      <div className="h-56 relative overflow-hidden bg-gradient-to-br from-slate-900 to-slate-800">
        <AnimatePresence mode="wait">
          {paint?.image_url ? (
            <motion.img
              key={paint.image_url}
              src={paint.image_url}
              alt={`${series.series} - ${paint.name}`}
              className="w-full h-full object-cover"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }}
              data-testid={`livery-image-${series.series.toLowerCase().replace(/\s+/g, '-')}`}
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <Paintbrush className="w-12 h-12 text-white/10" />
            </div>
          )}
        </AnimatePresence>
        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0e14] via-transparent to-transparent" />

        {/* Paint count badge */}
        <div className="absolute top-3 right-3">
          <span className="text-[10px] px-2 py-1 rounded-full bg-black/60 backdrop-blur-sm border border-white/10 text-gray-300 font-semibold">
            {series.paint_count} {series.paint_count === 1 ? 'paint' : 'paints'}
          </span>
        </div>

        {/* Fleet badge */}
        {inFleet && (
          <div className="absolute top-3 left-3">
            <span className="text-[10px] px-2 py-1 rounded-full bg-cyan-500/20 backdrop-blur-sm border border-cyan-500/30 text-cyan-400 font-bold uppercase">
              In Fleet
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Series title */}
        <h3 className="text-lg font-bold text-white mb-1 truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}
          data-testid={`livery-series-name-${series.series.toLowerCase().replace(/\s+/g, '-')}`}>
          {series.series}
        </h3>

        {/* Selected paint name and acquisition tag */}
        <div className="flex items-center gap-2 mb-3 min-h-[28px]">
          <span className="text-sm text-cyan-400 font-semibold truncate" data-testid="selected-paint-name">
            {paint?.name}
          </span>
          <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold shrink-0 ${colors.border} ${colors.bg} ${colors.text}`}
            data-testid="paint-acquisition-tag">
            {paint?.acquisition}
          </span>
        </div>

        {/* Description */}
        <p className="text-xs text-gray-500 mb-3 line-clamp-2 min-h-[32px]" data-testid="paint-description">
          {paint?.description || 'No description available.'}
        </p>

        {/* Price info */}
        <div className="flex items-center gap-3 mb-4 text-xs">
          {paint?.price_auec && (
            <span className="text-emerald-400 font-semibold" data-testid="paint-price-auec">
              {paint.price_auec.toLocaleString()} aUEC
            </span>
          )}
          {paint?.price_usd && (
            <span className="text-cyan-400 font-semibold" data-testid="paint-price-usd">
              ${paint.price_usd.toFixed(2)}
            </span>
          )}
          {paint?.store_url && (
            <a href={paint.store_url} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-cyan-500 hover:text-cyan-300 transition-colors"
              data-testid="paint-store-link">
              <ExternalLink className="w-3 h-3" /> RSI Store
            </a>
          )}
        </div>

        {/* Paint selector - horizontal scrollable pills */}
        <div className="flex gap-1.5 overflow-x-auto scrollbar-hide pb-1" data-testid="paint-selector">
          {series.paints.map((p, idx) => {
            const pc = ACQUISITION_COLORS[p.acquisition] || ACQUISITION_COLORS['Unknown'];
            return (
              <button
                key={idx}
                onClick={() => setSelectedIdx(idx)}
                data-testid={`paint-btn-${idx}`}
                className={`shrink-0 text-[10px] px-2.5 py-1.5 rounded-lg border font-semibold transition-all whitespace-nowrap ${
                  idx === selectedIdx
                    ? `${pc.border} ${pc.bg} ${pc.text} ring-1 ring-offset-1 ring-offset-[#0a0e14] ring-current`
                    : 'border-white/10 bg-white/[0.03] text-gray-500 hover:text-gray-300 hover:bg-white/[0.06]'
                }`}
              >
                {p.name}
              </button>
            );
          })}
        </div>
      </div>
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
  const [acqFilter, setAcqFilter] = useState('');

  useEffect(() => {
    let interval;
    const fetchData = async () => {
      try {
        const [livRes, fleetRes] = await Promise.all([
          axios.get(`${API}/api/liveries`),
          axios.get(`${API}/api/fleet/my`, { headers: { Authorization: `Bearer ${token}` } }),
        ]);

        if (livRes.data.loading) {
          // Data still loading, poll again
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

  const filteredLiveries = useMemo(() => {
    let result = liveries;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(s =>
        s.series.toLowerCase().includes(q) ||
        s.paints.some(p => p.name.toLowerCase().includes(q))
      );
    }
    if (acqFilter) {
      result = result.filter(s => s.paints.some(p => p.acquisition === acqFilter));
    }
    return result;
  }, [liveries, search, acqFilter]);

  const totalPaints = liveries.reduce((sum, s) => sum + s.paint_count, 0);

  const acqTypes = useMemo(() => {
    const counts = {};
    for (const s of liveries) {
      for (const p of s.paints) {
        counts[p.acquisition] = (counts[p.acquisition] || 0) + 1;
      }
    }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [liveries]);

  return (
    <div className="min-h-screen" data-testid="liveries-page">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Paintbrush className="w-8 h-8 text-cyan-500" />
          <h1 className="text-4xl font-black text-white tracking-tight" style={{ fontFamily: 'Rajdhani, sans-serif' }}
            data-testid="liveries-title">
            LIVERIES
          </h1>
        </div>
        {!loading && (
          <p className="text-sm text-gray-500">
            {liveries.length} ship series · {totalPaints} paints
          </p>
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search ship or paint name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            data-testid="liveries-search"
            className="w-full pl-9 pr-4 py-2.5 bg-white/[0.03] border border-white/10 rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/40 transition-colors"
          />
        </div>

        {/* Fleet toggle */}
        <div className="flex gap-1.5" data-testid="liveries-fleet-toggle">
          <button onClick={() => setFleetOnly(false)}
            data-testid="fleet-toggle-all"
            className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-all ${!fleetOnly ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'}`}>
            All Ships
          </button>
          <button onClick={() => setFleetOnly(true)}
            data-testid="fleet-toggle-fleet"
            className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-all ${fleetOnly ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'}`}>
            Fleet Only
          </button>
        </div>

        {/* Acquisition filter */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-hide" data-testid="acq-filter">
          <Filter className="w-3.5 h-3.5 text-gray-600 shrink-0" />
          {acqTypes.map(([type, count]) => {
            const c = ACQUISITION_COLORS[type] || ACQUISITION_COLORS['Unknown'];
            return (
              <button key={type}
                onClick={() => setAcqFilter(f => f === type ? '' : type)}
                data-testid={`acq-filter-${type.toLowerCase().replace(/\s+/g, '-')}`}
                className={`shrink-0 text-[10px] px-2.5 py-1.5 rounded-lg border font-semibold transition-all whitespace-nowrap ${
                  acqFilter === type
                    ? `${c.border} ${c.bg} ${c.text}`
                    : 'border-white/10 bg-white/[0.03] text-gray-500 hover:text-gray-300 hover:bg-white/[0.06]'
                }`}>
                {type} ({count})
              </button>
            );
          })}
          {acqFilter && (
            <button onClick={() => setAcqFilter('')}
              data-testid="acq-filter-clear"
              className="text-[10px] px-2 py-1.5 rounded-lg border border-white/10 text-gray-500 hover:text-white hover:bg-white/10 transition-all">
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-24 gap-4" data-testid="liveries-loading">
          <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
          <p className="text-sm text-gray-500">Loading livery data from starcitizen.tools...</p>
          <p className="text-xs text-gray-600">This may take a moment on first load</p>
        </div>
      )}

      {/* Grid */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5" data-testid="liveries-grid">
          {filteredLiveries.map((series) => (
            <PaintViewer key={series.series} series={series} fleetShipIds={fleetShipIds} fleetOnly={fleetOnly} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && filteredLiveries.length === 0 && (
        <div className="text-center py-16">
          <Paintbrush className="w-12 h-12 text-gray-700 mx-auto mb-4" />
          <p className="text-gray-500">No liveries found matching your search.</p>
        </div>
      )}
    </div>
  );
}
