import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { Search, Shield, Crosshair, ChevronDown, ChevronUp, MapPin, Shirt, Target, Package, X } from 'lucide-react';
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
  const [rareItems, setRareItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('weapons');
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const [wRes, aRes, eRes, rRes] = await Promise.all([
          axios.get(`${API}/gear/weapons`),
          axios.get(`${API}/gear/armor`),
          axios.get(`${API}/gear/equipment`),
          axios.get(`${API}/gear/rare-items`).catch(() => ({ data: { data: [] } })),
        ]);
        setWeapons(wRes.data.data || []);
        setArmor(aRes.data.data || []);
        setEquipment(eRes.data.data || []);
        setRareItems(rRes.data.data || []);
      } catch { toast.error('Failed to load gear data'); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const weaponTypes = useMemo(() => [...new Set(weapons.map(w => w.type))].sort(), [weapons]);
  const armorTypes = useMemo(() => [...new Set(armor.map(a => a.type))].sort(), [armor]);
  const equipTypes = useMemo(() => [...new Set(equipment.map(e => e.type))].sort(), [equipment]);

  const rareTypes = useMemo(() => [...new Set(rareItems.map(r => r.type))].sort(), [rareItems]);

  const filteredItems = useMemo(() => {
    if (activeTab === 'rare') {
      let result = rareItems;
      if (search) {
        const q = search.toLowerCase();
        result = result.filter(i => i.name.toLowerCase().includes(q) || i.manufacturer.toLowerCase().includes(q) || i.loot_locations?.some(l => l.toLowerCase().includes(q)));
      }
      if (filterType !== 'all') result = result.filter(i => i.type === filterType || i.category === filterType);
      return result;
    }
    const items = activeTab === 'weapons' ? weapons : activeTab === 'armor' ? armor : equipment;
    let result = items;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(i => i.name.toLowerCase().includes(q) || i.manufacturer.toLowerCase().includes(q));
    }
    if (filterType !== 'all') result = result.filter(i => i.type === filterType);
    return result;
  }, [activeTab, weapons, armor, equipment, rareItems, search, filterType]);

  const types = activeTab === 'weapons' ? weaponTypes : activeTab === 'armor' ? armorTypes : activeTab === 'rare' ? rareTypes : equipTypes;

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
        <button onClick={() => { setActiveTab('rare'); setFilterType('all'); setSearch(''); }} data-testid="tab-rare"
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all ${activeTab === 'rare' ? 'bg-red-500/20 text-red-400 border border-red-500/30 ring-1 ring-red-500/20' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
          <MapPin className="w-4 h-4" /> Rare Items ({rareItems.filter(r => r.loot_only).length})
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredItems.map((item, i) => (
          activeTab === 'rare'
            ? <RareItemCard key={item.id} item={item} index={i} onClick={() => setSelectedItem({ ...item, _kind: item.category })} />
            : activeTab === 'armor'
            ? <ArmorCard key={item.id} armor={item} index={i} onClick={() => setSelectedItem({ ...item, _kind: 'armor' })} />
            : activeTab === 'weapons'
            ? <WeaponCard key={item.id} weapon={item} index={i} onClick={() => setSelectedItem({ ...item, _kind: 'weapon' })} />
            : <EquipmentCard key={item.id} item={item} index={i} onClick={() => setSelectedItem({ ...item, _kind: 'equipment' })} />
        ))}
        {filteredItems.length === 0 && (
          <div className="col-span-full text-center py-16 glass-panel rounded-2xl">
            <Target className="w-12 h-12 mx-auto mb-3 text-gray-600" />
            <p className="text-gray-400">No {activeTab} match your filters</p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedItem && (
          <GearDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />
        )}
      </AnimatePresence>
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

const WeaponCard = ({ weapon, index, onClick }) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(weapon.name);
  const color = TYPE_COLORS[weapon.type] || '#888';

  // Determine current image: variant image if available, else base image
  const currentImage = selectedVariant !== weapon.name && weapon.variant_images?.[selectedVariant]
    ? weapon.variant_images[selectedVariant]
    : weapon.image;
  const hasImage = !!currentImage;

  // Per-variant acquisition data
  const vd = selectedVariant !== weapon.name ? weapon.variant_data?.[selectedVariant] : null;
  const currentPrice = vd ? vd.price_auec : weapon.price_auec;
  const currentLocations = vd ? vd.locations : weapon.locations;
  const currentLootLocations = vd ? vd.loot_locations : (weapon.loot_locations || []);
  const isLootOnly = vd && !vd.sold;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}
      className="glass-panel rounded-2xl overflow-hidden group cursor-pointer" data-testid={`weapon-${weapon.id}`}
      onClick={(e) => { if (!e.target.closest('select') && !e.target.closest('button')) onClick?.(); }}>
      {/* Image section */}
      <div className="relative h-44 overflow-hidden bg-[#0c0c16]">
        {hasImage ? (
          <img src={currentImage} alt={selectedVariant} loading="lazy"
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
            {isLootOnly ? (
              <div className="text-xs font-bold text-red-400 mt-0.5" style={{ fontFamily: 'Rajdhani, sans-serif' }}>LOOT ONLY</div>
            ) : currentPrice > 0 ? (
              <div className="text-xs font-bold text-amber-400 mt-0.5" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{currentPrice.toLocaleString()} aUEC</div>
            ) : null}
          </div>
          {weapon.variants?.length > 0 && (
            <select value={selectedVariant} onChange={e => { e.stopPropagation(); setSelectedVariant(e.target.value); }}
              data-testid={`variant-select-${weapon.id}`}
              className="px-2 py-1 bg-[#0a0a10] border border-white/10 rounded-lg text-[10px] text-white focus:outline-none focus:border-cyan-500 max-w-[130px]"
              style={{ colorScheme: 'dark' }}>
              <option value={weapon.name} className="bg-[#0a0a10]">{weapon.name} (Base)</option>
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

        {/* Locations toggle */}
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
            <div className="space-y-1.5">
              {currentLocations?.length > 0 && (
                <div>
                  <div className="text-[9px] text-gray-500 uppercase font-semibold mb-1">Buy</div>
                  {currentLocations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px] text-gray-300">
                      <Crosshair className="w-3 h-3 text-green-500 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
              {currentLootLocations?.length > 0 && (
                <div>
                  <div className="text-[9px] text-gray-500 uppercase font-semibold mb-1">Loot / Farm</div>
                  {currentLootLocations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px] text-yellow-400">
                      <MapPin className="w-3 h-3 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
              {(!currentLocations?.length && !currentLootLocations?.length) && (
                <div className="text-[11px] text-gray-500 italic">Acquisition data unavailable</div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const ArmorCard = ({ armor, index, onClick }) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(armor.name);
  const color = TYPE_COLORS[armor.type] || '#888';

  // Determine current image: variant image if available, else base image
  const currentImage = selectedVariant !== armor.name && armor.variant_images?.[selectedVariant]
    ? armor.variant_images[selectedVariant]
    : armor.image;
  const hasImage = !!currentImage;

  // Per-variant acquisition data
  const vd = selectedVariant !== armor.name ? armor.variant_data?.[selectedVariant] : null;
  const currentPrice = vd ? vd.price_auec : armor.price_auec;
  const currentLocations = vd ? vd.locations : armor.locations;
  const currentLootLocations = vd ? vd.loot_locations : armor.loot_locations;
  const isLootOnly = vd && !vd.sold;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}
      className="glass-panel rounded-2xl overflow-hidden group cursor-pointer" data-testid={`armor-${armor.id}`}
      onClick={(e) => { if (!e.target.closest('select') && !e.target.closest('button')) onClick?.(); }}>
      {/* Image section */}
      <div className="relative h-52 overflow-hidden bg-[#0c0c16]">
        {hasImage ? (
          <img src={currentImage} alt={selectedVariant} loading="lazy"
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
            {isLootOnly ? (
              <div className="text-xs font-bold text-red-400 mt-0.5" style={{ fontFamily: 'Rajdhani, sans-serif' }}>LOOT ONLY</div>
            ) : currentPrice > 0 ? (
              <div className="text-xs font-bold text-amber-400 mt-0.5" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{currentPrice.toLocaleString()} aUEC</div>
            ) : null}
          </div>
          {armor.variants?.length > 0 && (
            <select value={selectedVariant} onChange={e => { e.stopPropagation(); setSelectedVariant(e.target.value); }}
              data-testid={`variant-select-${armor.id}`}
              className="px-2 py-1 bg-[#0a0a10] border border-white/10 rounded-lg text-[10px] text-white focus:outline-none focus:border-cyan-500 max-w-[130px]"
              style={{ colorScheme: 'dark' }}>
              <option value={armor.name} className="bg-[#0a0a10]">{armor.name} (Base)</option>
              {armor.variants.map(v => <option key={v} value={v} className="bg-[#0a0a10]">{v}</option>)}
            </select>
          )}
        </div>

        {/* Stats */}
        {armor.type !== 'Backpack' && (
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
        )}

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
              {currentLocations?.length > 0 && (
                <div>
                  <div className="text-[9px] text-gray-500 uppercase font-semibold mb-1">Buy</div>
                  {currentLocations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px] text-gray-300">
                      <Shirt className="w-3 h-3 text-green-500 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
              {currentLootLocations?.length > 0 && (
                <div>
                  <div className="text-[9px] text-gray-500 uppercase font-semibold mb-1">Loot / Farm</div>
                  {currentLootLocations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px] text-yellow-400">
                      <MapPin className="w-3 h-3 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
              {(!currentLocations?.length && !currentLootLocations?.length) && (
                <div className="text-[11px] text-gray-500 italic">Acquisition data unavailable</div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const EquipmentCard = ({ item, index, onClick }) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(item.name);
  const color = TYPE_COLORS[item.type] || '#888';

  const currentImage = selectedVariant !== item.name && item.variant_images?.[selectedVariant]
    ? item.variant_images[selectedVariant]
    : item.image;
  const hasImage = !!currentImage;

  const vd = selectedVariant !== item.name ? item.variant_data?.[selectedVariant] : null;
  const currentPrice = vd ? vd.price_auec : item.price_auec;
  const currentLocations = vd ? vd.locations : item.locations;
  const currentLootLocations = vd ? vd.loot_locations : (item.loot_locations || []);
  const isLootOnly = vd && !vd.sold;

  const statEntries = item.stats ? Object.entries(item.stats).slice(0, 4) : [];

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}
      className="glass-panel rounded-2xl overflow-hidden group cursor-pointer" data-testid={`equip-${item.id}`}
      onClick={(e) => { if (!e.target.closest('button') && !e.target.closest('select')) onClick?.(); }}>
      {/* Image section - matching armor layout */}
      <div className="relative h-52 overflow-hidden bg-[#0c0c16]">
        {hasImage ? (
          <img src={currentImage} alt={selectedVariant} loading="lazy"
            className="w-full h-full object-contain transition-transform duration-500 group-hover:scale-105" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Package className="w-16 h-16 text-gray-700" />
          </div>
        )}
        {/* Type badge overlay */}
        <div className="absolute top-3 left-3 flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase backdrop-blur-md"
            style={{ background: `${color}30`, color, border: `1px solid ${color}40` }}>
            {item.type}
          </span>
          {item.subtype && (
            <span className="px-2 py-1 rounded-lg text-[10px] font-bold backdrop-blur-md bg-white/10 text-gray-300 border border-white/10">
              {item.subtype}
            </span>
          )}
        </div>
        <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-[#0a0a12] to-transparent" />
      </div>

      {/* Content */}
      <div className="p-4 -mt-2 relative">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-bold text-white truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
              {selectedVariant}
            </h3>
            <div className="text-xs text-gray-400">{item.manufacturer}</div>
            {isLootOnly ? (
              <div className="text-xs font-bold text-red-400 mt-0.5" style={{ fontFamily: 'Rajdhani, sans-serif' }}>LOOT ONLY</div>
            ) : currentPrice > 0 ? (
              <div className="text-xs font-bold text-amber-400 mt-0.5" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{currentPrice.toLocaleString()} aUEC</div>
            ) : null}
          </div>
          {item.variants?.length > 0 && (
            <select value={selectedVariant} onChange={e => { e.stopPropagation(); setSelectedVariant(e.target.value); }}
              data-testid={`variant-select-${item.id}`}
              className="px-2 py-1 bg-[#0a0a10] border border-white/10 rounded-lg text-[10px] text-white focus:outline-none focus:border-cyan-500 max-w-[130px]"
              style={{ colorScheme: 'dark' }}>
              <option value={item.name} className="bg-[#0a0a10]">{item.name} (Base)</option>
              {item.variants.map(v => <option key={v} value={v} className="bg-[#0a0a10]">{v}</option>)}
            </select>
          )}
        </div>

        {/* Stats - matching armor/weapon grid style */}
        {statEntries.length > 0 && (
          <div className={`grid grid-cols-${Math.min(statEntries.length, 4)} gap-1.5 mt-3`}>
            {statEntries.map(([key, val]) => (
              <div key={key} className="bg-white/[0.04] rounded-lg p-1.5 text-center">
                <div className="text-xs font-bold truncate" style={{ color, fontFamily: 'Rajdhani, sans-serif' }}>{String(val)}</div>
                <div className="text-[8px] text-gray-600 uppercase truncate">{key.replace(/_/g, ' ')}</div>
              </div>
            ))}
          </div>
        )}

        <p className="text-[11px] text-gray-500 mt-2 line-clamp-2">{item.description}</p>

        {/* Locations toggle - matching armor */}
        <button onClick={() => setExpanded(!expanded)} data-testid={`expand-${item.id}`}
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
              {currentLocations?.length > 0 && (
                <div>
                  <div className="text-[9px] text-gray-500 uppercase font-semibold mb-1">Buy</div>
                  {currentLocations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px] text-gray-300">
                      <Package className="w-3 h-3 text-green-500 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
              {currentLootLocations?.length > 0 && (
                <div>
                  <div className="text-[9px] text-gray-500 uppercase font-semibold mb-1">Loot / Farm</div>
                  {currentLootLocations.map((loc, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px] text-yellow-400">
                      <MapPin className="w-3 h-3 shrink-0" /> {loc}
                    </div>
                  ))}
                </div>
              )}
              {(!currentLocations?.length && !currentLootLocations?.length) && (
                <div className="text-[11px] text-gray-500 italic">Acquisition data unavailable</div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};


const RareItemCard = ({ item, index, onClick }) => {
  const color = TYPE_COLORS[item.type] || '#888';
  const catColor = item.category === 'weapon' ? '#FF0055' : item.category === 'armor' ? '#00D4FF' : '#F59E0B';
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(index * 0.04, 0.5) }}
      className="glass-panel rounded-2xl overflow-hidden group cursor-pointer" data-testid={`rare-${item.id}`}
      onClick={onClick}>
      <div className="relative h-44 overflow-hidden bg-[#0c0c16]">
        {item.image ? (
          <img src={item.image} alt={item.name} loading="lazy"
            className="w-full h-full object-contain transition-transform duration-500 group-hover:scale-105" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <MapPin className="w-14 h-14 text-gray-700" />
          </div>
        )}
        <div className="absolute top-3 left-3 flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase backdrop-blur-md"
            style={{ background: `${color}30`, color, border: `1px solid ${color}40` }}>
            {item.type}
          </span>
          <span className="px-2 py-1 rounded-lg text-[10px] font-bold uppercase backdrop-blur-md"
            style={{ background: `${catColor}20`, color: catColor, border: `1px solid ${catColor}30` }}>
            {item.category}
          </span>
        </div>
        {item.loot_only && (
          <div className="absolute top-3 right-3">
            <span className="px-2 py-1 rounded-lg text-[10px] font-bold uppercase backdrop-blur-md bg-red-500/30 text-red-400 border border-red-500/40">
              Loot Only
            </span>
          </div>
        )}
        <div className="absolute inset-x-0 bottom-0 h-14 bg-gradient-to-t from-[#0a0a12] to-transparent" />
      </div>
      <div className="p-4 -mt-2 relative">
        <h3 className="text-lg font-bold text-white truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{item.name}</h3>
        <div className="text-xs text-gray-400">{item.manufacturer}</div>
        {item.price_auec > 0 && (
          <div className="text-xs font-bold text-amber-400 mt-0.5" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{item.price_auec.toLocaleString()} aUEC</div>
        )}
        <p className="text-[11px] text-gray-500 mt-2 line-clamp-2">{item.description}</p>
        <div className="mt-3 space-y-1.5">
          {item.loot_locations?.map((loc, i) => (
            <div key={i} className="flex items-center gap-1.5 text-[11px] text-yellow-400">
              <MapPin className="w-3 h-3 shrink-0" /> {loc}
            </div>
          ))}
          {item.buy_locations?.length > 0 && item.buy_locations.map((loc, i) => (
            <div key={`b${i}`} className="flex items-center gap-1.5 text-[11px] text-gray-300">
              <Crosshair className="w-3 h-3 text-green-500 shrink-0" /> {loc}
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};


const GearDetailModal = ({ item, onClose }) => {
  const isWeapon = item._kind === 'weapon';
  const isArmor = item._kind === 'armor';
  const isEquipment = item._kind === 'equipment';
  const hasVariantData = true;
  const color = TYPE_COLORS[item.type] || '#888';
  const [selectedVariant, setSelectedVariant] = useState(null);

  // Determine current image based on selected variant
  const currentImage = selectedVariant && item.variant_images?.[selectedVariant]
    ? item.variant_images[selectedVariant]
    : item.image;
  const hasImage = !!currentImage;

  // Per-variant acquisition data
  const vd = selectedVariant ? item.variant_data?.[selectedVariant] : null;
  const currentPrice = vd ? vd.price_auec : item.price_auec;
  const currentLocations = vd ? vd.locations : item.locations;
  const currentLootLocations = vd ? vd.loot_locations : (item.loot_locations || []);
  const isLootOnly = vd && !vd.sold;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-[60] flex items-center justify-center p-4"
      onClick={onClose} data-testid="gear-detail-modal">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      {/* Modal */}
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
        transition={{ type: 'spring', damping: 25 }}
        className="relative w-full max-w-lg glass-panel rounded-2xl overflow-hidden max-h-[85vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}>
        {/* Close button */}
        <button onClick={onClose} data-testid="modal-close-btn"
          className="absolute top-3 right-3 z-10 w-8 h-8 flex items-center justify-center rounded-full bg-black/50 text-gray-400 hover:text-white backdrop-blur-md border border-white/10 transition-colors">
          <X className="w-4 h-4" />
        </button>

        {/* Image */}
        <div className="relative h-56 bg-[#0c0c16]">
          {hasImage ? (
            <img src={currentImage} alt={selectedVariant || item.name} className="w-full h-full object-contain" />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              {isWeapon ? <Crosshair className="w-20 h-20 text-gray-700" /> : isArmor ? <Shield className="w-20 h-20 text-gray-700" /> : <Package className="w-20 h-20 text-gray-700" />}
            </div>
          )}
          <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-[#0a0a12] to-transparent" />
          <div className="absolute top-3 left-3 flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase backdrop-blur-md"
              style={{ background: `${color}30`, color, border: `1px solid ${color}40` }}>
              {item.type}
            </span>
            {isWeapon && (
              <span className="px-2 py-1 rounded-lg text-[10px] font-bold backdrop-blur-md bg-white/10 text-gray-300 border border-white/10">
                S{item.size}
              </span>
            )}
            {isEquipment && item.subtype && (
              <span className="px-2 py-1 rounded-lg text-[10px] font-bold backdrop-blur-md bg-white/10 text-gray-300 border border-white/10">
                {item.subtype}
              </span>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-5 -mt-4 relative">
          <h2 className="text-2xl font-bold text-white mb-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{selectedVariant || item.name}</h2>
          <div className="text-sm text-gray-400">{item.manufacturer}</div>
          {isLootOnly ? (
            <div className="text-base font-bold text-red-400 mt-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>LOOT ONLY</div>
          ) : currentPrice > 0 ? (
            <div className="text-base font-bold text-amber-400 mt-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{currentPrice.toLocaleString()} aUEC</div>
          ) : null}
          <div className="mb-4" />

          <p className="text-sm text-gray-300 leading-relaxed mb-5">{item.description}</p>

          {/* Stats */}
          {isWeapon ? (
            <div className="grid grid-cols-2 gap-3 mb-5">
              <DetailStat label="Damage" value={item.damage} color="#FF0055" />
              <DetailStat label="Ammo" value={item.ammo} color="#FFAE00" />
              <DetailStat label="Fire Rate" value={item.fire_rate} color="#00D4FF" />
              <DetailStat label="Range" value={item.effective_range} color="#00FF9D" />
            </div>
          ) : isArmor && item.type !== 'Backpack' ? (
            <div className="grid grid-cols-3 gap-3 mb-5">
              <DetailStat label="Max Temp" value={`${item.temp_max}°C`} color="#FF4500" />
              <DetailStat label="Min Temp" value={`${item.temp_min}°C`} color="#00D4FF" />
              <DetailStat label="Radiation" value={item.radiation?.toLocaleString()} color="#00FF9D" />
            </div>
          ) : item.stats ? (
            <div className="grid grid-cols-2 gap-3 mb-5">
              {Object.entries(item.stats).map(([key, val]) => (
                <DetailStat key={key} label={key.replace(/_/g, ' ')} value={String(val)} color={color} />
              ))}
            </div>
          ) : null}

          {/* Variants - clickable for both armor and weapons */}
          {item.variants?.length > 0 && (
            <div className="mb-5">
              <div className="text-xs text-gray-500 uppercase font-semibold mb-2">Variants ({item.variants.length}){hasVariantData && ' — click to preview'}</div>
              <div className="flex flex-wrap gap-1.5">
                <button onClick={() => setSelectedVariant(null)} data-testid="variant-btn-base"
                  className={`px-2.5 py-1 rounded-lg text-[11px] border transition-all cursor-pointer ${!selectedVariant ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-white/[0.06] text-gray-300 border-white/10 hover:bg-white/10'}`}>
                  {item.name} (Base)
                </button>
                {item.variants.map(v => {
                  const hasVarImg = hasVariantData && item.variant_images?.[v] && item.variant_images[v] !== item.image;
                  const varData = hasVariantData ? item.variant_data?.[v] : null;
                  const varLootOnly = varData && !varData.sold;
                  return (
                    <button key={v} onClick={() => setSelectedVariant(v)} data-testid={`variant-btn-${v.replace(/[\s/]/g, '-').toLowerCase()}`}
                      className={`px-2.5 py-1 rounded-lg text-[11px] border transition-all cursor-pointer ${selectedVariant === v ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : varLootOnly ? 'bg-red-500/[0.06] text-gray-300 border-red-500/20 hover:bg-red-500/10' : 'bg-white/[0.06] text-gray-300 border-white/10 hover:bg-white/10'}`}>
                      {v.replace(item.name + ' ', '')}{hasVarImg ? ' *' : ''}{varLootOnly ? ' ⚠' : ''}
                    </button>
                  );
                })}
              </div>
              {hasVariantData && <div className="text-[10px] text-gray-600 mt-1">* = unique image | ⚠ = loot only</div>}
            </div>
          )}

          {/* Locations - dynamic based on selected variant */}
          {currentLocations?.length > 0 && (
            <div className="mb-3">
              <div className="text-xs text-gray-500 uppercase font-semibold mb-2">Purchase Locations</div>
              <div className="space-y-1.5">
                {currentLocations.map((loc, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-gray-300">
                    {isWeapon ? <Crosshair className="w-3.5 h-3.5 text-green-500 shrink-0" /> : isEquipment ? <Package className="w-3.5 h-3.5 text-green-500 shrink-0" /> : <Shirt className="w-3.5 h-3.5 text-green-500 shrink-0" />} {loc}
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentLootLocations?.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 uppercase font-semibold mb-2">Loot / Farm Locations</div>
              <div className="space-y-1.5">
                {currentLootLocations.map((loc, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-yellow-400">
                    <MapPin className="w-3.5 h-3.5 shrink-0" /> {loc}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

const DetailStat = ({ label, value, color }) => (
  <div className="bg-white/[0.04] rounded-xl p-3 text-center">
    <div className="text-lg font-bold" style={{ color, fontFamily: 'Rajdhani, sans-serif' }}>{value}</div>
    <div className="text-[10px] text-gray-500 uppercase">{label}</div>
  </div>
);


export default PersonalGear;
