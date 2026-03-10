import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Minus, Search, RefreshCw, DollarSign, BarChart3, History } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPE_LABELS = { ship: 'Ships', weapon: 'Weapons', component: 'Components' };
const TYPE_COLORS = { ship: '#00D4FF', weapon: '#FF0055', component: '#FFAE00' };

const PriceTracker = () => {
  const [summary, setSummary] = useState(null);
  const [changes, setChanges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');
  const [filterType, setFilterType] = useState('all');
  const [search, setSearch] = useState('');
  const [snapshotCount, setSnapshotCount] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [sumRes, chgRes] = await Promise.all([
          axios.get(`${API}/prices/summary`),
          axios.get(`${API}/prices/changes`),
        ]);
        setSummary(sumRes.data.data);
        setSnapshotCount(sumRes.data.snapshot_count);
        setChanges(chgRes.data.data || []);
      } catch {
        toast.error('Failed to load price data');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await axios.get(`${API}/prices/snapshot`);
      const [sumRes, chgRes] = await Promise.all([
        axios.get(`${API}/prices/summary`),
        axios.get(`${API}/prices/changes`),
      ]);
      setSummary(sumRes.data.data);
      setSnapshotCount(sumRes.data.snapshot_count);
      setChanges(chgRes.data.data || []);
      toast.success('Price snapshot captured');
    } catch {
      toast.error('Failed to refresh prices');
    } finally {
      setRefreshing(false);
    }
  };

  const allItems = useMemo(() => {
    if (!summary) return [];
    return [
      ...summary.ships.map(s => ({ ...s, category: 'ship' })),
      ...summary.weapons.map(w => ({ ...w, category: 'weapon' })),
      ...summary.components.map(c => ({ ...c, category: 'component' })),
    ];
  }, [summary]);

  const filteredItems = useMemo(() => {
    let items = activeTab === 'changes' ? changes : allItems;
    if (filterType !== 'all') {
      items = items.filter(i => (i.item_type || i.category) === filterType);
    }
    if (search) {
      const q = search.toLowerCase();
      items = items.filter(i => i.item_name.toLowerCase().includes(q));
    }
    return items;
  }, [activeTab, allItems, changes, filterType, search]);

  const stats = useMemo(() => {
    if (!summary) return { ships: 0, weapons: 0, components: 0, total: 0 };
    return {
      ships: summary.ships.length,
      weapons: summary.weapons.length,
      components: summary.components.length,
      total: summary.ships.length + summary.weapons.length + summary.components.length,
    };
  }, [summary]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="space-y-6" data-testid="price-tracker-page">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Price Tracker
          </h1>
          <p className="text-gray-400">Real-time aUEC prices from CStone Finder &amp; Star Citizen data</p>
        </div>
        <button onClick={handleRefresh} disabled={refreshing} data-testid="refresh-snapshot-btn"
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/25 transition-all disabled:opacity-50">
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Capturing...' : 'New Snapshot'}
        </button>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="Tracked Items" value={stats.total} icon={BarChart3} color="#00D4FF" testId="stat-total" />
        <StatCard label="Ships" value={stats.ships} icon={DollarSign} color="#00D4FF" testId="stat-ships" />
        <StatCard label="Weapons" value={stats.weapons} icon={DollarSign} color="#FF0055" testId="stat-weapons" />
        <StatCard label="Snapshots" value={snapshotCount} icon={History} color="#FFAE00" testId="stat-snapshots" />
      </div>

      {/* Tabs */}
      <div className="flex gap-2" data-testid="price-tabs">
        <button onClick={() => { setActiveTab('summary'); setSearch(''); }}
          data-testid="tab-summary"
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all ${activeTab === 'summary' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
          <DollarSign className="w-4 h-4" /> Current Prices
        </button>
        <button onClick={() => { setActiveTab('changes'); setSearch(''); }}
          data-testid="tab-changes"
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all ${activeTab === 'changes' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
          <TrendingUp className="w-4 h-4" /> Price Changes ({changes.length})
        </button>
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-xl p-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} data-testid="price-search"
            placeholder="Search items..."
            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-cyan-500" />
        </div>
        <div className="flex gap-1.5">
          <FilterBtn label="All" active={filterType === 'all'} onClick={() => setFilterType('all')} testId="filter-all" />
          <FilterBtn label="Ships" active={filterType === 'ship'} onClick={() => setFilterType('ship')} color="#00D4FF" testId="filter-ship" />
          <FilterBtn label="Weapons" active={filterType === 'weapon'} onClick={() => setFilterType('weapon')} color="#FF0055" testId="filter-weapon" />
          <FilterBtn label="Components" active={filterType === 'component'} onClick={() => setFilterType('component')} color="#FFAE00" testId="filter-component" />
        </div>
      </div>

      <div className="text-sm text-gray-500">{filteredItems.length} items</div>

      {/* Content */}
      {activeTab === 'summary' ? (
        <div className="space-y-2">
          {filteredItems.map((item, i) => (
            <PriceRow key={`${item.item_name}-${i}`} item={item} index={i} />
          ))}
          {filteredItems.length === 0 && <EmptyState />}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredItems.length > 0 ? filteredItems.map((item, i) => (
            <ChangeRow key={`${item.item_name}-${i}`} item={item} index={i} />
          )) : (
            <div className="text-center py-16 glass-panel rounded-2xl">
              <Minus className="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <p className="text-gray-400">No price changes detected between snapshots</p>
              <p className="text-xs text-gray-600 mt-1">Take a new snapshot after a game patch to see changes</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const StatCard = ({ label, value, icon: Icon, color, testId }) => (
  <div className="glass-panel rounded-xl p-4 text-center" data-testid={testId}>
    <Icon className="w-5 h-5 mx-auto mb-2" style={{ color }} />
    <div className="text-2xl font-bold" style={{ color, fontFamily: 'Rajdhani, sans-serif' }}>{value.toLocaleString()}</div>
    <div className="text-xs text-gray-500 mt-1">{label}</div>
  </div>
);

const FilterBtn = ({ label, active, onClick, color, testId }) => (
  <button onClick={onClick} data-testid={testId}
    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${active ? 'bg-white/15 border' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-white'}`}
    style={active ? { color: color || '#fff', borderColor: `${color || '#fff'}40` } : {}}>
    {label}
  </button>
);

const PriceRow = ({ item, index }) => {
  const color = TYPE_COLORS[item.category || item.item_type] || '#888';
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.015 }}
      className="glass-panel rounded-xl px-5 py-3 flex items-center justify-between gap-4" data-testid={`price-row-${index}`}>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase" style={{ background: `${color}20`, color, border: `1px solid ${color}30` }}>
            {item.item_type || item.category}
          </span>
          <span className="text-sm font-bold text-white truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{item.item_name}</span>
        </div>
        {item.location && <div className="text-xs text-gray-500 truncate">{item.location}</div>}
        {item.dealers && item.dealers.length > 0 && <div className="text-xs text-gray-500 truncate">{item.dealers.join(', ')}</div>}
      </div>
      <div className="text-right shrink-0">
        <div className="text-sm font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
          {item.price_auec?.toLocaleString()} aUEC
        </div>
        {item.price_usd > 0 && <div className="text-xs text-gray-500">${item.price_usd}</div>}
      </div>
    </motion.div>
  );
};

const ChangeRow = ({ item, index }) => {
  const isUp = item.direction === 'up';
  const isNew = item.direction === 'new';
  const color = isNew ? '#00D4FF' : (isUp ? '#FF0055' : '#00FF9D');
  const typeColor = TYPE_COLORS[item.item_type] || '#888';

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.015 }}
      className="glass-panel rounded-xl px-5 py-3 flex items-center justify-between gap-4" data-testid={`change-row-${index}`}>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase" style={{ background: `${typeColor}20`, color: typeColor, border: `1px solid ${typeColor}30` }}>
            {item.item_type}
          </span>
          <span className="text-sm font-bold text-white truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{item.item_name}</span>
        </div>
        <div className="text-xs text-gray-500">
          {item.old_price.toLocaleString()} → {item.new_price.toLocaleString()} aUEC
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <div className="text-right">
          <div className="flex items-center gap-1 text-sm font-bold" style={{ color, fontFamily: 'Rajdhani, sans-serif' }}>
            {isNew ? 'NEW' : (isUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />)}
            {!isNew && <span>{isUp ? '+' : ''}{item.change_pct}%</span>}
          </div>
          <div className="text-xs" style={{ color: `${color}99` }}>
            {isUp ? '+' : ''}{item.change.toLocaleString()} aUEC
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const EmptyState = () => (
  <div className="text-center py-16 glass-panel rounded-2xl">
    <DollarSign className="w-12 h-12 mx-auto mb-3 text-gray-600" />
    <p className="text-gray-400">No price data found</p>
  </div>
);

export default PriceTracker;
