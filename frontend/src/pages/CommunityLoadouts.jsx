import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Search, Ship, User, Clock, Copy, Wrench, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CommunityLoadouts = () => {
  const [loadouts, setLoadouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const LIMIT = 12;

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API}/community/loadouts`, { params: { page, limit: LIMIT, ship_name: search } });
        setLoadouts(res.data.data || []);
        setTotal(res.data.total || 0);
      } catch {
        toast.error('Failed to load community loadouts');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [page, search]);

  const totalPages = Math.ceil(total / LIMIT);

  const copyShareLink = (code) => {
    const url = `${window.location.origin}/shared/${code}`;
    navigator.clipboard.writeText(url);
    toast.success('Share link copied!');
  };

  return (
    <div className="space-y-8" data-testid="community-page">
      <div>
        <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Community Loadouts
        </h1>
        <p className="text-gray-400">Browse and clone loadouts shared by other pilots</p>
      </div>

      <div className="glass-panel rounded-2xl p-4">
        <div className="relative max-w-lg">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search by ship name..."
            data-testid="community-search"
            className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : loadouts.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-3xl">
          <Wrench className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <h2 className="text-2xl font-bold mb-2" style={{ fontFamily: 'Rajdhani, sans-serif' }}>No Loadouts Yet</h2>
          <p className="text-gray-400 mb-6">Be the first to share a loadout with the community!</p>
          <Link to="/loadout" className="btn-origin inline-block">Build a Loadout</Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {loadouts.map((lo, i) => (
              <LoadoutCard key={lo.id || i} loadout={lo} onCopyLink={copyShareLink} index={i} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 pt-4">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}
                data-testid="prev-page-btn"
                className="p-2 rounded-lg bg-white/5 text-gray-400 hover:text-white disabled:opacity-30 transition-all">
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-sm text-gray-400">Page {page} of {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page >= totalPages}
                data-testid="next-page-btn"
                className="p-2 rounded-lg bg-white/5 text-gray-400 hover:text-white disabled:opacity-30 transition-all">
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

const LoadoutCard = ({ loadout, onCopyLink, index }) => {
  const slotCount = Object.keys(loadout.slots || {}).length;
  const weaponSlots = Object.entries(loadout.slots || {}).filter(([k]) => k.startsWith('weapon_'));
  const componentSlots = Object.entries(loadout.slots || {}).filter(([k]) => !k.startsWith('weapon_'));
  const totalCost = Object.values(loadout.slots || {}).reduce((s, item) => s + (item.cost_auec || 0), 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="glass-panel rounded-2xl overflow-hidden group"
      data-testid={`community-loadout-${loadout.share_code}`}
    >
      <div className="p-6 space-y-4">
        <div className="flex items-start justify-between">
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-bold text-white truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
              {loadout.loadout_name}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <Ship className="w-4 h-4 text-cyan-500 shrink-0" />
              <span className="text-sm text-cyan-400 truncate">{loadout.ship_name}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-gray-500">
          <User className="w-3 h-3" />
          <span>{loadout.username || 'Unknown Pilot'}</span>
          <span className="mx-1">|</span>
          <Clock className="w-3 h-3" />
          <span>{loadout.updated_at ? new Date(loadout.updated_at).toLocaleDateString() : 'N/A'}</span>
        </div>

        <div className="space-y-1.5">
          {componentSlots.slice(0, 3).map(([key, item]) => (
            <div key={key} className="flex items-center justify-between text-xs">
              <span className="text-gray-400 truncate">{key.replace(/_\d+$/, '').replace(/_/g, ' ')}</span>
              <span className="text-white font-medium truncate ml-2">{item.name}</span>
            </div>
          ))}
          {weaponSlots.slice(0, 2).map(([key, item]) => (
            <div key={key} className="flex items-center justify-between text-xs">
              <span className="text-red-400 truncate">weapon</span>
              <span className="text-white font-medium truncate ml-2">{item.name}</span>
            </div>
          ))}
          {slotCount > 5 && <div className="text-xs text-gray-600">+{slotCount - 5} more items</div>}
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-white/5">
          <div className="text-xs">
            <span className="text-gray-500">{slotCount} items</span>
            {totalCost > 0 && <span className="text-yellow-400 ml-2">{totalCost.toLocaleString()} aUEC</span>}
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => onCopyLink(loadout.share_code)} data-testid={`copy-link-${loadout.share_code}`}
              className="p-1.5 rounded-lg hover:bg-white/10 transition-colors text-gray-400 hover:text-cyan-400" title="Copy share link">
              <Copy className="w-4 h-4" />
            </button>
            <Link to={`/shared/${loadout.share_code}`} data-testid={`view-loadout-${loadout.share_code}`}
              className="px-3 py-1.5 rounded-lg bg-cyan-500/10 text-cyan-500 hover:bg-cyan-500/20 transition-colors text-xs font-semibold">
              View
            </Link>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default CommunityLoadouts;
