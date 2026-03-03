import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { Search, Shield, Crosshair, ChevronDown, ChevronUp, MapPin, Shirt, Zap, Target, Package, Pickaxe, DollarSign } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPE_COLORS = {
  Pistol: '#00D4FF', SMG: '#FFAE00', 'Assault Rifle': '#FF6B35', LMG: '#FF0055',
  Shotgun: '#A855F7', 'Sniper Rifle': '#00FF9D', Railgun: '#FFD700',
  'Grenade Launcher': '#FF4500', 'Missile Launcher': '#FF1493',
  'Medical Device': '#00CED1', Grenade: '#FF8C00', Utility: '#7CB342',
  Heavy: '#FF0055', Medium: '#FFAE00', Light: '#00D4FF', 'Flight Suit': '#8B9DAF',
  'Mining Head': '#F59E0B', 'Mining Attachment': '#D97706', 'Mining Module': '#B45309',
  Backpack: '#8B5CF6', Undersuit: '#6366F1',
  'Salvage Tool': '#10B981', Scanner: '#38BDF8', 'Hacking Tool': '#F43F5E',
};

const PersonalGear = () => {
  const [weapons, setWeapons] = useState([]);
  const [armor, setArmor] = useState([]);
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('weapons');
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    const fetch = async () => {
      try {
        const [wRes, aRes, eRes] = await Promise.all([
          axios.get(`${API}/gear/weapons`),
          axios.get(`${API}/gear/armor`),
          axios.get(`${API}/gear/equipment`),
        ]);
        setWeapons(wRes.data.data || []);
        setArmor(aRes.data.data || []);
        setEquipment(eRes.data.data || []);
      } catch { toast.error('Failed to load gear data'); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const weaponTypes = useMemo(() => [...new Set(weapons.map(w => w.type))].sort(), [weapons]);
  const armorTypes = useMemo(() => [...new Set(armor.map(a => a.type))].sort(), [armor]);
  const equipTypes = useMemo(() => [...new Set(equipment.map(e => e.type))].sort(), [equipment]);

  const filteredItems = useMemo(() => {
    const items = activeTab === 'weapons' ? weapons : activeTab === 'armor' ? armor : equipment;
    let result = items;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(i => i.name.toLowerCase().includes(q) || i.manufacturer.toLowerCase().includes(q));
    }
    if (filterType !== 'all') result = result.filter(i => i.type === filterType);
    return result;
  }, [activeTab, weapons, armor, equipment, search, filterType]);

  const types = activeTab === 'weapons' ? weaponTypes : activeTab === 'armor' ? armorTypes : equipTypes;

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
        <p className="text-gray-400">FPS weapons, armor sets, and equipment with locations</p>
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
        <button onClick={() => { setActiveTab('equipment'); setFilterType('all'); setSearch(''); }} data-testid="tab-equipment"
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all ${activeTab === 'equipment' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
          <Package className="w-4 h-4" /> Equipment ({equipment.length})
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
      {(activeTab === 'armor' || activeTab === 'weapons') ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredItems.map((item, i) => (
            activeTab === 'armor'
              ? <ArmorCard key={item.id} armor={item} index={i} />
              : <WeaponCard key={item.id} weapon={item} index={i} />
          ))}
          {filteredItems.length === 0 && (
            <div className="col-span-full text-center py-16 glass-panel rounded-2xl">
              <Target className="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <p className="text-gray-400">No {activeTab} match your filters</p>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredItems.map((item, i) => (
            activeTab === 'weapons'
              ? <WeaponCard key={item.id} weapon={item} index={i} />
              : <EquipmentCard key={item.id} item={item} index={i} />
          ))}
          {filteredItems.length === 0 && (
            <div className="text-center py-16 glass-panel rounded-2xl">
              <Target className="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <p className="text-gray-400">No {activeTab} match your filters</p>
            </div>
          )}
        </div>
      )}
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
  const hasImage = !!weapon.image;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}
      className="glass-panel rounded-2xl overflow-hidden group" data-testid={`weapon-${weapon.id}`}>
      {/* Image section */}
      <div className="relative h-44 overflow-hidden bg-[#0c0c16]">
        {hasImage ? (
          <img src={weapon.image} alt={selectedVariant} loading="lazy"
            className="w-full h-full object-contain transition-transform duration-500 group-hover:scale-105" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Crosshair className="w-14 h-14 text-gray-700" />
          </div>
        )}
        <div className="absolute top-3 left-3 flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase backdrop-blur-md"
            style={{ background: `${color}30`, color, border: `1px solid ${color}40` }}>
            {weapon.type}
          </span>
          <span className="px-2 py-1 rounded-lg text-[10px] font-bold backdrop-blur-md bg-white/10 text-gray-300 border border-white/10">
            S{weapon.size}
          </span>
        </div>
        <div className="absolute inset-x-0 bottom-0 h-14 bg-gradient-to-t from-[#0a0a12] to-transparent" />
      </div>

      {/* Content */}
      <div className="p-4 -mt-2 relative">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-bold text-white truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
              {selectedVariant}
            </h3>
            <div className="text-xs text-gray-400">{weapon.manufacturer}</div>
          </div>
          {weapon.variants?.length > 0 && (
            <select value={selectedVariant} onChange={e => setSelectedVariant(e.target.value)}
              data-testid={`variant-select-${weapon.id}`}
              className="px-2 py-1 bg-[#0a0a10] border border-white/10 rounded-lg text-[10px] text-white focus:outline-none focus:border-cyan-500 max-w-[130px]"
              style={{ colorScheme: 'dark' }}>
              <option value={weapon.name} className="bg-[#0a0a10]">{weapon.name}</option>
              {weapon.variants.map(v => <option key={v} value={v} className="bg-[#0a0a10]">{v}</option>)}
            </select>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-1.5 mt-3">
          <div className="bg-white/[0.04] rounded-lg p-1.5 text-center">
            <div className="text-xs font-bold text-red-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{weapon.damage}</div>
            <div className="text-[8px] text-gray-600">DMG</div>
          </div>
          <div className="bg-white/[0.04] rounded-lg p-1.5 text-center">
            <div className="text-xs font-bold text-amber-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{weapon.ammo}</div>
            <div className="text-[8px] text-gray-600">AMMO</div>
          </div>
          <div className="bg-white/[0.04] rounded-lg p-1.5 text-center">
            <div className="text-xs font-bold text-cyan-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{weapon.fire_rate}</div>
            <div className="text-[8px] text-gray-600">ROF</div>
          </div>
          <div className="bg-white/[0.04] rounded-lg p-1.5 text-center">
            <div className="text-xs font-bold text-green-400 truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{weapon.effective_range}</div>
            <div className="text-[8px] text-gray-600">RNG</div>
          </div>
        </div>

        <p className="text-[11px] text-gray-500 mt-2 line-clamp-2">{weapon.description}</p>

        <button onClick={() => setExpanded(!expanded)} data-testid={`expand-${weapon.id}`}
          className="flex items-center gap-1 mt-2 text-[11px] text-cyan-500 hover:text-cyan-400 transition-colors w-full">
          <MapPin className="w-3 h-3" /> Where to find
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/5 bg-white/[0.02] px-4 py-3 overflow-hidden">
            <div className="space-y-1">
              {weapon.locations.map((loc, i) => (
                <div key={i} className="flex items-center gap-1.5 text-[11px] text-gray-300">
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
  const hasImage = !!armor.image;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}
      className="glass-panel rounded-2xl overflow-hidden group" data-testid={`armor-${armor.id}`}>
      {/* Image section */}
      <div className="relative h-52 overflow-hidden bg-[#0c0c16]">
        {hasImage ? (
          <img src={armor.image} alt={selectedVariant} loading="lazy"
            className="w-full h-full object-contain transition-transform duration-500 group-hover:scale-105" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Shield className="w-16 h-16 text-gray-700" />
          </div>
        )}
        {/* Type badge overlay */}
        <div className="absolute top-3 left-3">
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase backdrop-blur-md"
            style={{ background: `${color}30`, color, border: `1px solid ${color}40` }}>
            {armor.type}
          </span>
        </div>
        {/* Gradient fade at bottom */}
        <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-[#0a0a12] to-transparent" />
      </div>

      {/* Content */}
      <div className="p-4 -mt-2 relative">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-bold text-white truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
              {selectedVariant}
            </h3>
            <div className="text-xs text-gray-400">{armor.manufacturer}</div>
          </div>
          {armor.variants?.length > 0 && (
            <select value={selectedVariant} onChange={e => setSelectedVariant(e.target.value)}
              data-testid={`variant-select-${armor.id}`}
              className="px-2 py-1 bg-[#0a0a10] border border-white/10 rounded-lg text-[10px] text-white focus:outline-none focus:border-cyan-500 max-w-[130px]"
              style={{ colorScheme: 'dark' }}>
              <option value={armor.name} className="bg-[#0a0a10]">{armor.name}</option>
              {armor.variants.map(v => <option key={v} value={v} className="bg-[#0a0a10]">{v}</option>)}
            </select>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-2 mt-3">
          <div className="bg-white/[0.04] rounded-lg p-2 text-center">
            <div className="text-xs font-bold text-orange-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{armor.temp_max}°C</div>
            <div className="text-[9px] text-gray-600">Max Temp</div>
          </div>
          <div className="bg-white/[0.04] rounded-lg p-2 text-center">
            <div className="text-xs font-bold text-cyan-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{armor.temp_min}°C</div>
            <div className="text-[9px] text-gray-600">Min Temp</div>
          </div>
          <div className="bg-white/[0.04] rounded-lg p-2 text-center">
            <div className="text-xs font-bold text-green-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{armor.radiation?.toLocaleString()}</div>
            <div className="text-[9px] text-gray-600">Radiation</div>
          </div>
        </div>

        <p className="text-[11px] text-gray-500 mt-2 line-clamp-2">{armor.description}</p>

        {/* Locations toggle */}
        <button onClick={() => setExpanded(!expanded)} data-testid={`expand-${armor.id}`}
          className="flex items-center gap-1 mt-2 text-[11px] text-cyan-500 hover:text-cyan-400 transition-colors w-full">
          <MapPin className="w-3 h-3" /> Where to find
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/5 bg-white/[0.02] px-4 py-3 overflow-hidden">
            <div className="space-y-1.5">
              {armor.locations?.length > 0 && (
                <div>
                  <div className="text-[9px] text-gray-500 uppercase font-semibold mb-1">Buy</div>
                  {armor.locations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px] text-gray-300">
                      <Shirt className="w-3 h-3 text-green-500 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
              {armor.loot_locations?.length > 0 && (
                <div>
                  <div className="text-[9px] text-gray-500 uppercase font-semibold mb-1">Loot / Farm</div>
                  {armor.loot_locations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px] text-yellow-400">
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

const EquipmentCard = ({ item, index }) => {
  const [expanded, setExpanded] = useState(false);
  const color = TYPE_COLORS[item.type] || '#888';

  const statEntries = item.stats ? Object.entries(item.stats) : [];

  return (
    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.03 }}
      className="glass-panel rounded-xl overflow-hidden" data-testid={`equip-${item.id}`}>
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3 mb-1">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase" style={{ background: `${color}20`, color, border: `1px solid ${color}30` }}>
                {item.type}
              </span>
              {item.subtype && <span className="text-xs text-gray-500">{item.subtype}</span>}
            </div>
            <h3 className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{item.name}</h3>
            <div className="text-sm text-gray-400">{item.manufacturer}</div>
          </div>
          {item.price_auec > 0 && (
            <div className="text-right shrink-0">
              <div className="flex items-center gap-1 text-sm font-bold text-amber-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                <DollarSign className="w-3 h-3" /> {item.price_auec.toLocaleString()} aUEC
              </div>
            </div>
          )}
        </div>

        {statEntries.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
            {statEntries.map(([key, val]) => (
              <StatPill key={key} label={key.replace(/_/g, ' ')} value={String(val)} color={color} />
            ))}
          </div>
        )}

        <p className="text-xs text-gray-500 mt-3">{item.description}</p>

        <button onClick={() => setExpanded(!expanded)} data-testid={`expand-${item.id}`}
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
              {item.locations.map((loc, i) => (
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

const StatPill = ({ label, value, icon: Icon, color }) => (
  <div className="bg-white/[0.03] rounded-lg p-2 text-center">
    {Icon && <Icon className="w-3 h-3 mx-auto mb-0.5" style={{ color }} />}
    <div className="text-sm font-bold" style={{ color, fontFamily: 'Rajdhani, sans-serif' }}>{value}</div>
    <div className="text-[10px] text-gray-600">{label}</div>
  </div>
);

export default PersonalGear;
