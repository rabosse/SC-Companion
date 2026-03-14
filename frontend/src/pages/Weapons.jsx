import { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Crosshair, Search, MapPin, DollarSign, X, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

const TYPE_COLORS = {
  BallisticCannon: '#FFAE00', BallisticGatling: '#FF8C00', BallisticRepeater: '#FFD700',
  LaserCannon: '#00D4FF', LaserRepeater: '#00BFFF', LaserGatling: '#00E5FF',
  NeutronCannon: '#A855F7', PlasmaCannon: '#FF6B6B', MassDriver: '#D4AF37',
  DistortionCannon: '#00FF9D', DistortionRepeater: '#00CC7A', DistortionScatterGun: '#00AA66',
  ScatterGun: '#FF9D00', MissilePDC: '#FF0055', Energy: '#00D4FF', Ballistic: '#FFAE00', Missile: '#FF0055',
};

const Weapons = () => {
  const { API } = useAuth();
  const [weapons, setWeapons] = useState([]);
  const [filteredWeapons, setFilteredWeapons] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedSize, setSelectedSize] = useState('all');
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const fetchWeapons = async () => {
      try {
        const response = await axios.get(`${API}/weapons`);
        setWeapons(response.data.data || []);
        setFilteredWeapons(response.data.data || []);
      } catch (error) {
        toast.error('Failed to load weapons');
      } finally {
        setLoading(false);
      }
    };
    fetchWeapons();
  }, [API]);

  useEffect(() => {
    let result = weapons;
    if (searchQuery) {
      result = result.filter((w) =>
        w.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        w.manufacturer.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    if (selectedType !== 'all') result = result.filter((w) => w.type === selectedType);
    if (selectedSize !== 'all') result = result.filter((w) => w.size === selectedSize);
    setFilteredWeapons(result);
  }, [searchQuery, selectedType, selectedSize, weapons]);

  const types = ['all', ...new Set(weapons.map((w) => w.type).filter(Boolean).sort())];
  const sizes = ['all', ...new Set(weapons.map((w) => w.size).filter(Boolean).sort((a, b) => Number(a) - Number(b)))];

  const openDetail = async (weapon) => {
    setDetail(weapon);
    setDetailLoading(true);
    try {
      const res = await axios.get(`${API}/weapons/${weapon.id}`);
      if (res.data.success) setDetail(res.data.data);
    } catch { /* keep base data */ }
    finally { setDetailLoading(false); }
  };

  const getTypeColor = (type) => TYPE_COLORS[type] || '#FFFFFF';

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading weapons...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8" data-testid="weapons-page">
      <div>
        <h1 className="text-4xl sm:text-5xl font-bold mb-4 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Weapons Arsenal
        </h1>
        <p className="text-gray-400" style={{ fontFamily: 'Inter, sans-serif' }}>
          Ship weapons, stock ordnance and tactical upgrades
        </p>
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search weapons..." data-testid="search-input"
              className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all" />
          </div>
          <select value={selectedType} onChange={(e) => setSelectedType(e.target.value)} data-testid="type-filter"
            className="px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all">
            {types.map((type) => (
              <option key={type} value={type} className="bg-gray-900">{type === 'all' ? 'All Types' : type}</option>
            ))}
          </select>
          <select value={selectedSize} onChange={(e) => setSelectedSize(e.target.value)} data-testid="size-filter"
            className="px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all">
            {sizes.map((size) => (
              <option key={size} value={size} className="bg-gray-900">{size === 'all' ? 'All Sizes' : `Size ${size}`}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Weapons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredWeapons.map((weapon, index) => {
          const color = getTypeColor(weapon.type);
          return (
            <motion.div key={weapon.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(index * 0.03, 0.5) }}
              className="glass-panel rounded-2xl p-6 hover:scale-[1.02] transition-transform duration-300 cursor-pointer"
              data-testid={`weapon-card-${weapon.id}`}
              onClick={() => openDetail(weapon)}>
              <div className="flex items-center justify-between mb-4">
                <Crosshair className="w-8 h-8" style={{ color }} />
                <span className="text-xs px-2 py-1 rounded-full border" style={{ backgroundColor: `${color}20`, color, borderColor: `${color}30` }}>
                  Size {weapon.size}
                </span>
              </div>
              <h3 className="text-lg font-bold text-white mb-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{weapon.name}</h3>
              <p className="text-sm text-gray-400 mb-2">{weapon.manufacturer}</p>
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: `${color}20`, color }}>{weapon.type}</span>
              </div>
              <div className="space-y-3 mb-4">
                {weapon.alpha_damage > 0 && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-500">Alpha Damage</span>
                      <span className="text-white font-semibold">{Number(weapon.alpha_damage).toFixed(1)}</span>
                    </div>
                    <div className="stat-bar"><div className="stat-bar-fill" style={{ width: `${Math.min((weapon.alpha_damage / 500) * 100, 100)}%` }}></div></div>
                  </div>
                )}
                {weapon.dps > 0 && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-500">DPS</span>
                      <span className="text-white font-semibold">{Number(weapon.dps).toFixed(1)}</span>
                    </div>
                    <div className="stat-bar"><div className="stat-bar-fill" style={{ width: `${Math.min((weapon.dps / 2000) * 100, 100)}%` }}></div></div>
                  </div>
                )}
                {weapon.fire_rate > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Fire Rate</span>
                    <span className="text-white font-semibold">{weapon.fire_rate} RPM</span>
                  </div>
                )}
              </div>
              <div className="border-t border-white/10 pt-3">
                <div className="flex items-center gap-2 text-xs">
                  <DollarSign className={`w-3.5 h-3.5 shrink-0 ${weapon.sold ? 'text-green-400' : 'text-gray-600'}`} />
                  <span className={weapon.sold ? 'text-green-400 font-medium' : 'text-gray-600'}>
                    {weapon.sold ? 'Available in-game' : 'Not sold in-game'}
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredWeapons.length === 0 && (
        <div className="text-center py-12" data-testid="no-weapons-message">
          <Crosshair className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No weapons found matching your criteria</p>
        </div>
      )}

      {/* Detail Modal */}
      <AnimatePresence>
        {detail && <WeaponDetailModal weapon={detail} loading={detailLoading} onClose={() => setDetail(null)} />}
      </AnimatePresence>
    </div>
  );
};

const WeaponDetailModal = ({ weapon, loading, onClose }) => {
  const color = TYPE_COLORS[weapon.type] || '#00D4FF';
  const locations = weapon.locations || [];
  const bestPrice = locations.filter(l => l.price > 0).sort((a, b) => a.price - b.price)[0];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={onClose} data-testid="weapon-detail-modal">
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
        className="glass-panel rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6"
        onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{weapon.name}</h2>
            <p className="text-sm text-gray-400">{weapon.manufacturer}</p>
          </div>
          <button onClick={onClose} data-testid="close-weapon-detail"
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mb-6">
          <span className="px-3 py-1 rounded-lg text-xs font-bold border" style={{ color, background: `${color}20`, borderColor: `${color}30` }}>
            {weapon.type}
          </span>
          <span className="px-3 py-1 rounded-lg text-xs font-bold border" style={{ color, background: `${color}20`, borderColor: `${color}30` }}>
            Size {weapon.size}
          </span>
          {weapon.grade && (
            <span className="px-3 py-1 rounded-lg text-xs font-bold border border-amber-500/30 bg-amber-500/20 text-amber-400">
              Grade {weapon.grade}
            </span>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
          {weapon.alpha_damage > 0 && <StatBox label="Alpha Damage" value={Number(weapon.alpha_damage).toFixed(1)} color={color} />}
          {weapon.dps > 0 && <StatBox label="DPS" value={Number(weapon.dps).toFixed(1)} color="#FF0055" />}
          {weapon.fire_rate > 0 && <StatBox label="Fire Rate" value={`${weapon.fire_rate} RPM`} color="#FFAE00" />}
          {weapon.range > 0 && <StatBox label="Range" value={`${Number(weapon.range).toLocaleString()} m`} color="#00FF9D" />}
          {weapon.ammo_speed > 0 && <StatBox label="Ammo Speed" value={`${Number(weapon.ammo_speed).toLocaleString()} m/s`} color="#D4AF37" />}
          {weapon.max_ammo > 0 && <StatBox label="Max Ammo" value={Number(weapon.max_ammo).toLocaleString()} color="#A855F7" />}
          {weapon.power_draw > 0 && <StatBox label="Power Draw" value={weapon.power_draw} color="#FF6B6B" />}
        </div>

        {/* Description */}
        {weapon.description && (
          <div className="mb-6">
            <h3 className="text-xs text-gray-500 uppercase font-bold mb-2">Description</h3>
            <p className="text-sm text-gray-300 leading-relaxed">{weapon.description.replace(/\\n/g, ' ').replace(/\n/g, ' ')}</p>
          </div>
        )}

        {/* Purchase Locations */}
        <div>
          <h3 className="text-xs text-gray-500 uppercase font-bold mb-3 flex items-center gap-2">
            <MapPin className="w-3.5 h-3.5" /> Purchase Locations
            {loading && <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />}
          </h3>
          {locations.length > 0 ? (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {locations.map((loc, i) => (
                <div key={i} className={`flex items-center justify-between text-sm p-2.5 rounded-lg ${bestPrice && loc.price === bestPrice.price ? 'bg-green-500/10 border border-green-500/20' : 'bg-white/5'}`}
                  data-testid={`weapon-location-${i}`}>
                  <span className="text-gray-300 flex-1 mr-4">{loc.location}</span>
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
            <p className="text-sm text-gray-500 italic">{loading ? 'Fetching locations...' : 'No purchase locations available'}</p>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

const StatBox = ({ label, value, color }) => (
  <div className="bg-white/5 rounded-xl p-3 text-center" data-testid={`stat-${label.toLowerCase().replace(/\s/g,'-')}`}>
    <div className="text-[10px] text-gray-500 uppercase font-semibold mb-1">{label}</div>
    <div className="text-lg font-bold" style={{ color, fontFamily: 'Rajdhani, sans-serif' }}>{value}</div>
  </div>
);

export default Weapons;
