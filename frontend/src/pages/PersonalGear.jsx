import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { Search, Shield, Crosshair, ChevronDown, ChevronUp, MapPin, Shirt, Zap, Target } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPE_COLORS = {
  Pistol: '#00D4FF', SMG: '#FFAE00', 'Assault Rifle': '#FF6B35', LMG: '#FF0055',
  Shotgun: '#A855F7', 'Sniper Rifle': '#00FF9D', Railgun: '#FFD700',
  'Grenade Launcher': '#FF4500', 'Missile Launcher': '#FF1493',
  'Medical Device': '#00CED1',
  Heavy: '#FF0055', Medium: '#FFAE00', Light: '#00D4FF', 'Flight Suit': '#8B9DAF',
};

const PersonalGear = () => {
  const [weapons, setWeapons] = useState([]);
  const [armor, setArmor] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('weapons');
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    const fetch = async () => {
      try {
        const [wRes, aRes] = await Promise.all([
          axios.get(`${API}/gear/weapons`),
          axios.get(`${API}/gear/armor`),
        ]);
        setWeapons(wRes.data.data || []);
        setArmor(aRes.data.data || []);
      } catch { toast.error('Failed to load gear data'); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const weaponTypes = useMemo(() => [...new Set(weapons.map(w => w.type))].sort(), [weapons]);
  const armorTypes = useMemo(() => [...new Set(armor.map(a => a.type))].sort(), [armor]);

  const filteredItems = useMemo(() => {
    const items = activeTab === 'weapons' ? weapons : armor;
    let result = items;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(i => i.name.toLowerCase().includes(q) || i.manufacturer.toLowerCase().includes(q));
    }
    if (filterType !== 'all') result = result.filter(i => i.type === filterType);
    return result;
  }, [activeTab, weapons, armor, search, filterType]);

  const types = activeTab === 'weapons' ? weaponTypes : armorTypes;

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="space-y-6" data-testid="gear-page">
      <div>
        <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Personal Gear
        </h1>
        <p className="text-gray-400">FPS weapons and armor sets with locations</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2" data-testid="gear-tabs">
        <button onClick={() => { setActiveTab('weapons'); setFilterType('all'); setSearch(''); }} data-testid="tab-weapons"
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all ${activeTab === 'weapons' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
          <Crosshair className="w-4 h-4" /> FPS Weapons ({weapons.length})
        </button>
        <button onClick={() => { setActiveTab('armor'); setFilterType('all'); setSearch(''); }} data-testid="tab-armor"
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all ${activeTab === 'armor' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
          <Shield className="w-4 h-4" /> Armor Sets ({armor.length})
        </button>
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-xl p-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} data-testid="gear-search"
            placeholder={`Search ${activeTab}...`}
            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-cyan-500" />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          <FilterBtn label="All" active={filterType === 'all'} onClick={() => setFilterType('all')} testId="filter-all" />
          {types.map(t => (
            <FilterBtn key={t} label={t} active={filterType === t} onClick={() => setFilterType(t)}
              color={TYPE_COLORS[t]} testId={`filter-${t.toLowerCase().replace(/ /g, '-')}`} />
          ))}
        </div>
      </div>

      {/* Results count */}
      <div className="text-sm text-gray-500">{filteredItems.length} {activeTab} found</div>

      {/* Items Grid */}
      <div className="space-y-3">
        {filteredItems.map((item, i) => (
          activeTab === 'weapons'
            ? <WeaponCard key={item.id} weapon={item} index={i} />
            : <ArmorCard key={item.id} armor={item} index={i} />
        ))}
        {filteredItems.length === 0 && (
          <div className="text-center py-16 glass-panel rounded-2xl">
            <Target className="w-12 h-12 mx-auto mb-3 text-gray-600" />
            <p className="text-gray-400">No {activeTab} match your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

const FilterBtn = ({ label, active, onClick, color, testId }) => (
  <button onClick={onClick} data-testid={testId}
    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${active ? 'bg-white/15 border' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-white'}`}
    style={active ? { color: color || '#fff', borderColor: `${color || '#fff'}40` } : {}}>
    {label}
  </button>
);

const WeaponCard = ({ weapon, index }) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(weapon.name);
  const color = TYPE_COLORS[weapon.type] || '#888';

  return (
    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.03 }}
      className="glass-panel rounded-xl overflow-hidden" data-testid={`weapon-${weapon.id}`}>
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3 mb-1">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase" style={{ background: `${color}20`, color, border: `1px solid ${color}30` }}>
                {weapon.type}
              </span>
              <span className="text-xs text-gray-500">S{weapon.size}</span>
            </div>
            <h3 className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{selectedVariant}</h3>
            <div className="text-sm text-gray-400">{weapon.manufacturer}</div>
          </div>

          {/* Variant dropdown */}
          {weapon.variants?.length > 0 && (
            <div className="shrink-0">
              <select value={selectedVariant} onChange={e => setSelectedVariant(e.target.value)} data-testid={`variant-select-${weapon.id}`}
                className="px-3 py-1.5 bg-[#0a0a10] border border-white/10 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500" style={{ colorScheme: 'dark' }}>
                <option value={weapon.name} className="bg-[#0a0a10]">{weapon.name} (Base)</option>
                {weapon.variants.map(v => <option key={v} value={v} className="bg-[#0a0a10]">{v}</option>)}
              </select>
            </div>
          )}
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
          {weapon.damage > 0 && <StatPill label="Damage" value={weapon.damage} icon={Zap} color="#FF0055" />}
          {weapon.ammo > 0 && <StatPill label="Ammo" value={weapon.ammo} color="#FFAE00" />}
          <StatPill label="Range" value={weapon.effective_range} color="#00FF9D" />
          <StatPill label="Fire Rate" value={weapon.fire_rate} color="#00D4FF" />
        </div>

        <p className="text-xs text-gray-500 mt-3">{weapon.description}</p>

        {/* Expand for locations */}
        <button onClick={() => setExpanded(!expanded)} data-testid={`expand-${weapon.id}`}
          className="flex items-center gap-1 mt-3 text-xs text-cyan-500 hover:text-cyan-400 transition-colors">
          <MapPin className="w-3 h-3" /> Where to find
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/5 bg-white/[0.02] px-5 py-3 overflow-hidden">
            <div className="space-y-1">
              {weapon.locations.map((loc, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-gray-300">
                  <MapPin className="w-3 h-3 text-cyan-500 shrink-0" /> {loc}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const ArmorCard = ({ armor, index }) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(armor.name);
  const color = TYPE_COLORS[armor.type] || '#888';

  return (
    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.03 }}
      className="glass-panel rounded-xl overflow-hidden" data-testid={`armor-${armor.id}`}>
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3 mb-1">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase" style={{ background: `${color}20`, color, border: `1px solid ${color}30` }}>
                {armor.type}
              </span>
            </div>
            <h3 className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{selectedVariant}</h3>
            <div className="text-sm text-gray-400">{armor.manufacturer}</div>
          </div>

          {/* Variant dropdown */}
          {armor.variants?.length > 0 && (
            <div className="shrink-0">
              <select value={selectedVariant} onChange={e => setSelectedVariant(e.target.value)} data-testid={`variant-select-${armor.id}`}
                className="px-3 py-1.5 bg-[#0a0a10] border border-white/10 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500" style={{ colorScheme: 'dark' }}>
                <option value={armor.name} className="bg-[#0a0a10]">{armor.name} (Base)</option>
                {armor.variants.map(v => <option key={v} value={v} className="bg-[#0a0a10]">{v}</option>)}
              </select>
            </div>
          )}
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-3 mt-4">
          <StatPill label="Max Temp" value={`${armor.temp_max}°C`} color="#FF4500" />
          <StatPill label="Min Temp" value={`${armor.temp_min}°C`} color="#00D4FF" />
          <StatPill label="Rad Protection" value={armor.radiation?.toLocaleString()} color="#00FF9D" />
        </div>

        <p className="text-xs text-gray-500 mt-3">{armor.description}</p>

        {/* Expand for locations */}
        <button onClick={() => setExpanded(!expanded)} data-testid={`expand-${armor.id}`}
          className="flex items-center gap-1 mt-3 text-xs text-cyan-500 hover:text-cyan-400 transition-colors">
          <MapPin className="w-3 h-3" /> Where to find
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/5 bg-white/[0.02] px-5 py-3 overflow-hidden">
            <div className="space-y-2">
              {armor.locations?.length > 0 && (
                <div>
                  <div className="text-[10px] text-gray-500 uppercase font-semibold mb-1">Buy</div>
                  {armor.locations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-gray-300">
                      <Shirt className="w-3 h-3 text-green-500 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
              {armor.loot_locations?.length > 0 && (
                <div>
                  <div className="text-[10px] text-gray-500 uppercase font-semibold mb-1">Loot / Farm</div>
                  {armor.loot_locations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-yellow-400">
                      <MapPin className="w-3 h-3 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const StatPill = ({ label, value, icon: Icon, color }) => (
  <div className="bg-white/[0.03] rounded-lg p-2 text-center">
    {Icon && <Icon className="w-3 h-3 mx-auto mb-0.5" style={{ color }} />}
    <div className="text-sm font-bold" style={{ color, fontFamily: 'Rajdhani, sans-serif' }}>{value}</div>
    <div className="text-[10px] text-gray-600">{label}</div>
  </div>
);

export default PersonalGear;
