import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Search, X, Check, Shield, Zap, Cpu, Box, Crosshair, AlertTriangle, Save, Share2, List, PlusCircle, Trash2, Edit3, Loader2, MapPin, ShoppingCart, DollarSign } from 'lucide-react';
import SpaceshipIcon from '../components/SpaceshipIcon';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

const SLOT_TYPES = [
  { key: 'shield', label: 'Shields', icon: Shield, color: '#00D4FF', componentType: 'Shield' },
  { key: 'power_plant', label: 'Power Plant', icon: Zap, color: '#FFAE00', componentType: 'Power' },
  { key: 'cooler', label: 'Coolers', icon: Box, color: '#00FF9D', componentType: 'Cooler' },
  { key: 'quantum_drive', label: 'Quantum Drive', icon: Cpu, color: '#D4AF37', componentType: 'Quantum' },
];

const LoadoutBuilder = () => {
  const { API } = useAuth();
  const [tab, setTab] = useState('my-loadouts');
  const [ships, setShips] = useState([]);
  const [fleetShipIds, setFleetShipIds] = useState(new Set());
  const [selectedShip, setSelectedShip] = useState(null);
  const [components, setComponents] = useState([]);
  const [weapons, setWeapons] = useState([]);
  const [loadout, setLoadout] = useState({});
  const [activeSlot, setActiveSlot] = useState(null);
  const [shipSearch, setShipSearch] = useState('');
  const [itemSearch, setItemSearch] = useState('');
  const [savedLoadouts, setSavedLoadouts] = useState([]);
  const [allLoadouts, setAllLoadouts] = useState([]);
  const [loadoutName, setLoadoutName] = useState('');
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [fleetOnly, setFleetOnly] = useState(false);
  const [editingLoadoutId, setEditingLoadoutId] = useState(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [inspectItem, setInspectItem] = useState(null);
  const [inspectLoading, setInspectLoading] = useState(false);
  const [shoppingList, setShoppingList] = useState(null);
  const [shoppingLoading, setShoppingLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [shipsRes, compsRes, weaponsRes, fleetRes, allLoadoutsRes] = await Promise.all([
          axios.get(`${API}/ships`),
          axios.get(`${API}/components`),
          axios.get(`${API}/weapons`),
          axios.get(`${API}/fleet/my`),
          axios.get(`${API}/loadouts/my/all`),
        ]);
        setShips(shipsRes.data.data || []);
        setComponents(compsRes.data.data || []);
        setWeapons(weaponsRes.data.data || []);
        const fleet = fleetRes.data.data || [];
        setFleetShipIds(new Set(fleet.map(f => f.ship_id)));
        setAllLoadouts(allLoadoutsRes.data.data || []);
      } catch {
        toast.error('Failed to load data');
      } finally { setDataLoading(false); }
    };
    fetchData();
  }, [API]);

  const refreshAllLoadouts = async () => {
    try {
      const res = await axios.get(`${API}/loadouts/my/all`);
      setAllLoadouts(res.data.data || []);
    } catch { /* ignore */ }
  };

  const inspectSlotItem = async (slotId, item) => {
    setInspectItem(item);
    setInspectLoading(true);
    const isWeapon = slotId.startsWith('weapon_');
    const endpoint = isWeapon ? `${API}/weapons/${item.id}` : `${API}/components/${item.id}`;
    try {
      const res = await axios.get(endpoint);
      if (res.data.success && res.data.data) setInspectItem(res.data.data);
    } catch { /* keep base item data */ }
    finally { setInspectLoading(false); }
  };

  const buildShoppingList = async (slots, shipName) => {
    if (!slots || Object.keys(slots).length === 0) { toast.error('No items to shop for'); return; }
    setShoppingLoading(true);
    setShoppingList({ shipName, items: [], byStore: {}, total: 0, loading: true });

    const entries = Object.entries(slots);
    const results = [];

    // Fetch locations for each item in parallel (batched)
    const fetches = entries.map(async ([slotId, item]) => {
      const isWeapon = slotId.startsWith('weapon_');
      const endpoint = isWeapon ? `${API}/weapons/${item.id}` : `${API}/components/${item.id}`;
      try {
        const res = await axios.get(endpoint);
        const data = res.data.success ? res.data.data : null;
        const locations = data?.locations || [];
        const cheapest = locations.filter(l => l.price > 0).sort((a, b) => a.price - b.price)[0] || null;
        return { slotId, item: data || item, name: item.name, cheapest, allLocations: locations };
      } catch {
        return { slotId, item, name: item.name, cheapest: null, allLocations: [] };
      }
    });

    const settled = await Promise.all(fetches);

    // Build by-store grouping
    const byStore = {};
    let total = 0;
    settled.forEach(r => {
      results.push(r);
      if (r.cheapest) {
        total += r.cheapest.price;
        const store = r.cheapest.location;
        if (!byStore[store]) byStore[store] = { location: store, items: [], subtotal: 0 };
        byStore[store].items.push({ name: r.name, price: r.cheapest.price });
        byStore[store].subtotal += r.cheapest.price;
      }
    });

    // Sort stores by number of items (most items first = fewest stops)
    const sortedStores = Object.values(byStore).sort((a, b) => b.items.length - a.items.length);

    setShoppingList({ shipName, items: results, byStore: sortedStores, total, loading: false });
    setShoppingLoading(false);
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const hardpoints = useMemo(() => selectedShip?.hardpoints || {}, [selectedShip]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const weaponSlots = useMemo(() => hardpoints.weapons || [], [hardpoints]);

  const slotDefs = useMemo(() => {
    if (!selectedShip) return [];
    const defs = [];
    SLOT_TYPES.forEach(st => {
      const hp = hardpoints[st.key];
      if (hp && hp.count > 0) {
        for (let i = 0; i < hp.count; i++) {
          defs.push({ id: `${st.key}_${i}`, type: 'component', componentType: st.componentType, maxSize: hp.size, label: `${st.label} ${hp.count > 1 ? i + 1 : ''}`.trim(), icon: st.icon, color: st.color });
        }
      }
    });
    weaponSlots.forEach((maxSize, i) => {
      defs.push({ id: `weapon_${i}`, type: 'weapon', maxSize, label: `Weapon Hardpoint ${i + 1}`, icon: Crosshair, color: '#FF0055' });
    });
    return defs;
  }, [selectedShip, hardpoints, weaponSlots]);

  const getCompatibleItems = (slot) => {
    const q = itemSearch.toLowerCase();
    if (slot.type === 'weapon') {
      return weapons.filter(w => {
        const wSize = parseInt(w.size) || 0;
        if (wSize > slot.maxSize || wSize <= 0) return false;
        if (q && !w.name.toLowerCase().includes(q) && !w.manufacturer.toLowerCase().includes(q)) return false;
        return true;
      });
    } else {
      return components.filter(c => {
        const cSize = parseInt(c.size) || 0;
        if (cSize !== slot.maxSize) return false;
        if (c.type !== slot.componentType) return false;
        if (q && !c.name.toLowerCase().includes(q) && !c.manufacturer.toLowerCase().includes(q)) return false;
        return true;
      });
    }
  };

  const assignItem = (slotId, item) => {
    setLoadout(prev => ({ ...prev, [slotId]: item }));
    setActiveSlot(null);
    setItemSearch('');
    toast.success(`${item.name} equipped`);
  };

  const removeItem = (slotId) => {
    setLoadout(prev => { const copy = { ...prev }; delete copy[slotId]; return copy; });
  };

  const clearLoadout = () => { setLoadout({}); toast.success('Loadout cleared'); };

  const selectShip = async (ship) => {
    setSelectedShip(ship);
    setLoadout({});
    setActiveSlot(null);
    setShipSearch('');
    setEditingLoadoutId(null);
    try {
      const res = await axios.get(`${API}/loadouts/${ship.id}`);
      setSavedLoadouts(res.data.data || []);
    } catch { setSavedLoadouts([]); }
  };

  const openLoadoutForEdit = (saved) => {
    const ship = ships.find(s => s.id === saved.ship_id);
    if (!ship) { toast.error('Ship not found'); return; }
    setSelectedShip(ship);
    setLoadout(saved.slots || {});
    setLoadoutName(saved.loadout_name);
    setEditingLoadoutId(saved.id);
    setTab('builder');
    // Also refresh that ship's loadouts
    axios.get(`${API}/loadouts/${ship.id}`).then(r => setSavedLoadouts(r.data.data || [])).catch(() => {});
  };

  const saveLoadout = async () => {
    if (!loadoutName.trim()) { toast.error('Please enter a loadout name'); return; }
    try {
      const res = await axios.post(`${API}/loadouts/save`, {
        ship_id: selectedShip.id,
        ship_name: selectedShip.name,
        loadout_name: loadoutName.trim(),
        slots: loadout,
      });
      const shareCode = res.data.share_code;
      toast.success(`Loadout "${loadoutName}" saved!`);
      setShowSaveDialog(false);
      setLoadoutName('');
      setEditingLoadoutId(null);
      const loadoutsRes = await axios.get(`${API}/loadouts/${selectedShip.id}`);
      setSavedLoadouts(loadoutsRes.data.data || []);
      await refreshAllLoadouts();
      if (shareCode) toast.success(`Share code: ${shareCode}`, { duration: 5000 });
    } catch { toast.error('Failed to save loadout'); }
  };

  const loadSavedLoadout = (saved) => {
    setLoadout(saved.slots || {});
    setLoadoutName(saved.loadout_name);
    setEditingLoadoutId(saved.id);
    toast.success(`Loaded "${saved.loadout_name}"`);
  };

  const deleteSavedLoadout = async (loadoutId, name) => {
    try {
      await axios.delete(`${API}/loadouts/${loadoutId}`);
      setSavedLoadouts(prev => prev.filter(l => l.id !== loadoutId));
      setAllLoadouts(prev => prev.filter(l => l.id !== loadoutId));
      if (editingLoadoutId === loadoutId) setEditingLoadoutId(null);
      toast.success(`Deleted "${name}"`);
    } catch { toast.error('Failed to delete loadout'); }
  };

  const filteredShips = useMemo(() => {
    let result = ships;
    if (fleetOnly) result = result.filter(s => fleetShipIds.has(s.id));
    if (!shipSearch) return result;
    const q = shipSearch.toLowerCase();
    return result.filter(s => s.name.toLowerCase().includes(q) || s.manufacturer.toLowerCase().includes(q));
  }, [ships, shipSearch, fleetOnly, fleetShipIds]);

  const totalCost = Object.values(loadout).reduce((sum, item) => sum + (item.cost_auec || 0), 0);

  if (dataLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading loadout data...</p>
        </div>
      </div>
    );
  }

  // ========================
  // TAB: MY LOADOUTS
  // ========================
  if (tab === 'my-loadouts' && !selectedShip) {
    const grouped = {};
    allLoadouts.forEach(l => {
      if (!grouped[l.ship_id]) grouped[l.ship_id] = { ship_name: l.ship_name, ship_id: l.ship_id, loadouts: [] };
      grouped[l.ship_id].loadouts.push(l);
    });

    return (
      <div className="space-y-8" data-testid="loadout-my-loadouts">
        <div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Loadout Builder
          </h1>
          <p className="text-gray-400 text-sm">View, edit, and create ship loadouts</p>
        </div>

        {/* Tab Nav */}
        <div className="flex gap-2" data-testid="loadout-tabs">
          <button onClick={() => setTab('my-loadouts')} data-testid="tab-my-loadouts"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
            <List className="w-4 h-4" /> My Loadouts ({allLoadouts.length})
          </button>
          <button onClick={() => setTab('builder')} data-testid="tab-new-loadout"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10">
            <PlusCircle className="w-4 h-4" /> New Loadout
          </button>
        </div>

        {/* Loadouts List */}
        {allLoadouts.length === 0 ? (
          <div className="glass-panel rounded-2xl p-12 text-center">
            <Save className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-400 mb-2" style={{ fontFamily: 'Rajdhani, sans-serif' }}>No Saved Loadouts</h3>
            <p className="text-gray-500 text-sm mb-6">Create your first loadout by selecting a ship and equipping components</p>
            <button onClick={() => setTab('builder')} data-testid="create-first-loadout-btn"
              className="px-6 py-3 rounded-xl font-bold text-black" style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}>
              Create Loadout
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.values(grouped).map(group => {
              const ship = ships.find(s => s.id === group.ship_id);
              return (
                <div key={group.ship_id} className="glass-panel rounded-2xl overflow-hidden" data-testid={`loadout-group-${group.ship_id}`}>
                  {/* Ship Header */}
                  <div className="flex items-center gap-4 p-4 border-b border-white/10 bg-white/[0.02]">
                    <div className="w-16 h-12 rounded-lg overflow-hidden bg-gradient-to-br from-cyan-500/10 to-blue-600/10 shrink-0">
                      {ship?.image ? (
                        <img src={ship.image} alt={group.ship_name} className="w-full h-full object-cover" onError={e => { e.target.style.display = 'none'; }} />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center"><SpaceshipIcon className="w-6 h-6 text-cyan-500/30" /></div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{group.ship_name}</h3>
                      <p className="text-xs text-gray-500">{ship?.manufacturer} - {group.loadouts.length} loadout{group.loadouts.length !== 1 ? 's' : ''}</p>
                    </div>
                  </div>
                  {/* Loadout Rows */}
                  <div className="divide-y divide-white/5">
                    {group.loadouts.map(saved => {
                      const slotCount = Object.keys(saved.slots || {}).length;
                      const cost = Object.values(saved.slots || {}).reduce((s, item) => s + (item.cost_auec || 0), 0);
                      return (
                        <div key={saved.id} className="flex items-center gap-4 p-4 hover:bg-white/[0.03] transition-colors" data-testid={`loadout-row-${saved.id}`}>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3">
                              <span className="font-bold text-white text-sm">{saved.loadout_name}</span>
                              {slotCount > 0 && (
                                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 font-semibold">{slotCount} items</span>
                              )}
                              {cost > 0 && (
                                <span className="text-[10px] px-2 py-0.5 rounded-full bg-yellow-500/15 text-yellow-400 font-semibold">{cost.toLocaleString()} aUEC</span>
                              )}
                            </div>
                            <div className="flex flex-wrap gap-1.5 mt-1.5">
                              {Object.entries(saved.slots || {}).map(([slotId, item]) => (
                                <button key={slotId} onClick={(e) => { e.stopPropagation(); inspectSlotItem(slotId, item); }}
                                  data-testid={`inspect-${saved.id}-${slotId}`}
                                  className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400 hover:bg-cyan-500/15 hover:text-cyan-400 transition-colors cursor-pointer">
                                  {item.name}
                                </button>
                              ))}
                            </div>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            <button onClick={() => buildShoppingList(saved.slots, saved.loadout_name)} data-testid={`shopping-list-${saved.id}`}
                              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-yellow-500/10 text-yellow-400 hover:bg-yellow-500/20 transition-colors">
                              <ShoppingCart className="w-3 h-3" /> Cost
                            </button>
                            <button onClick={() => openLoadoutForEdit(saved)} data-testid={`edit-loadout-${saved.id}`}
                              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 transition-colors">
                              <Edit3 className="w-3 h-3" /> Edit
                            </button>
                            {saved.share_code && (
                              <button onClick={() => { navigator.clipboard.writeText(`${window.location.origin}/shared/${saved.share_code}`); toast.success('Share link copied!'); }}
                                data-testid={`share-loadout-${saved.id}`}
                                className="p-1.5 rounded-lg hover:bg-cyan-500/20 text-cyan-500 transition-colors" title="Copy share link">
                                <Share2 className="w-3.5 h-3.5" />
                              </button>
                            )}
                            <button onClick={() => deleteSavedLoadout(saved.id, saved.loadout_name)} data-testid={`delete-loadout-${saved.id}`}
                              className="p-1.5 rounded-lg hover:bg-red-500/20 text-red-500 transition-colors" title="Delete">
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Item Inspect Popup */}
        <AnimatePresence>
          {inspectItem && <ItemDetailPopup item={inspectItem} loading={inspectLoading} onClose={() => setInspectItem(null)} />}
        </AnimatePresence>

        {/* Shopping List Modal */}
        <AnimatePresence>
          {shoppingList && <ShoppingListModal data={shoppingList} onClose={() => setShoppingList(null)} />}
        </AnimatePresence>
      </div>
    );
  }

  // ========================
  // TAB: BUILDER - Ship Selection
  // ========================
  if (!selectedShip) {
    return (
      <div className="space-y-8" data-testid="loadout-ship-select">
        <div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Loadout Builder
          </h1>
          <p className="text-gray-400 text-sm">Select a ship to customize its loadout</p>
        </div>

        {/* Tab Nav */}
        <div className="flex gap-2" data-testid="loadout-tabs">
          <button onClick={() => setTab('my-loadouts')} data-testid="tab-my-loadouts"
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all ${tab === 'my-loadouts' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
            <List className="w-4 h-4" /> My Loadouts ({allLoadouts.length})
          </button>
          <button onClick={() => setTab('builder')} data-testid="tab-new-loadout"
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm uppercase transition-all ${tab === 'builder' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
            <PlusCircle className="w-4 h-4" /> New Loadout
          </button>
        </div>

        <div className="flex items-center gap-4 max-w-lg">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input type="text" value={shipSearch} onChange={e => setShipSearch(e.target.value)}
              placeholder="Search ships..." data-testid="ship-search-input"
              className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all" />
          </div>
        </div>

        {/* Fleet Toggle */}
        <div className="flex gap-1.5" data-testid="fleet-toggle">
          <button onClick={() => setFleetOnly(false)} data-testid="toggle-all-ships"
            className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${!fleetOnly ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'}`}>
            All Ships
          </button>
          <button onClick={() => setFleetOnly(true)} data-testid="toggle-fleet-only"
            className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${fleetOnly ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'}`}>
            My Fleet ({fleetShipIds.size})
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {filteredShips.map(ship => {
            const hp = ship.hardpoints || {};
            const wSlots = hp.weapons || [];
            const hasSlots = wSlots.length > 0 || (hp.shield?.count > 0);
            const shipLoadoutCount = allLoadouts.filter(l => l.ship_id === ship.id).length;

            return (
              <button key={ship.id} onClick={() => hasSlots && selectShip(ship)} data-testid={`select-ship-${ship.id}`}
                className={`glass-panel rounded-xl p-3 text-left transition-all group ${hasSlots ? 'hover:border-cyan-500/50 cursor-pointer' : 'opacity-40 cursor-not-allowed'}`}>
                <div className="h-24 bg-gradient-to-br from-cyan-500/10 to-blue-600/10 rounded-lg overflow-hidden mb-2">
                  {ship.image ? (
                    <img src={ship.image} alt={ship.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform" onError={e => { e.target.onerror = null; e.target.style.display = 'none'; }} />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center"><SpaceshipIcon className="w-8 h-8 text-cyan-500/20" /></div>
                  )}
                </div>
                <div className="font-bold text-white text-sm truncate">{ship.name}</div>
                <div className="text-xs text-gray-500 truncate">{ship.manufacturer}</div>
                <div className="flex items-center gap-1 mt-1 flex-wrap">
                  {wSlots.length > 0 && <span className="text-[10px] px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded">{wSlots.length}x wpn</span>}
                  {hp.shield?.count > 0 && <span className="text-[10px] px-1.5 py-0.5 bg-cyan-500/20 text-cyan-400 rounded">S{hp.shield.size} shld</span>}
                  {shipLoadoutCount > 0 && <span className="text-[10px] px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded">{shipLoadoutCount} saved</span>}
                </div>
                {!hasSlots && <div className="text-[10px] text-gray-600 mt-1">No slots</div>}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  // ========================
  // BUILDER VIEW (ship selected)
  // ========================
  return (
    <div className="space-y-6" data-testid="loadout-builder">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <button onClick={() => { setSelectedShip(null); setLoadout({}); setEditingLoadoutId(null); setLoadoutName(''); }}
            data-testid="back-to-ships-btn" className="p-2 hover:bg-white/10 rounded-lg transition-colors">
            <X className="w-6 h-6 text-gray-400" />
          </button>
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
              {selectedShip.name}
            </h1>
            <p className="text-gray-400 text-sm">
              {selectedShip.manufacturer} - {selectedShip.size} class
              {editingLoadoutId && <span className="text-cyan-400 ml-2">Editing: {loadoutName}</span>}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {totalCost > 0 && (
            <div className="text-sm text-yellow-400 font-semibold" data-testid="total-cost">
              Total: {totalCost.toLocaleString()} aUEC
            </div>
          )}
          {Object.keys(loadout).length > 0 && (
            <>
              <button onClick={() => buildShoppingList(loadout, selectedShip.name)} data-testid="shopping-list-btn"
                className="px-3 py-1.5 bg-yellow-500/20 text-yellow-400 rounded-lg hover:bg-yellow-500/30 transition-colors text-sm font-semibold flex items-center gap-1.5">
                <ShoppingCart className="w-3.5 h-3.5" /> Shopping List
              </button>
              <button onClick={() => setShowSaveDialog(true)} data-testid="save-loadout-btn"
                className="px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors text-sm font-semibold flex items-center gap-1.5">
                <Save className="w-3.5 h-3.5" /> {editingLoadoutId ? 'Update' : 'Save'}
              </button>
              <button onClick={clearLoadout} data-testid="clear-loadout-btn" className="px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors text-sm">
                Clear All
              </button>
            </>
          )}
        </div>
      </div>

      {/* Ship image + slots */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ship preview */}
        <div className="glass-panel rounded-2xl overflow-hidden">
          <div className="h-48 bg-gradient-to-br from-cyan-500/10 to-blue-600/10">
            {selectedShip.image && (
              <img src={selectedShip.image} alt={selectedShip.name} className="w-full h-full object-cover" onError={e => { e.target.onerror = null; e.target.style.display = 'none'; }} />
            )}
          </div>
          <div className="p-4 space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">Size Class</span><span className="text-white">{selectedShip.size}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Weapon Hardpoints</span><span className="text-white">{weaponSlots.length}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Component Slots</span><span className="text-white">{slotDefs.filter(s => s.type === 'component').length}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Loadout Filled</span><span className="text-white">{Object.keys(loadout).length}/{slotDefs.length}</span></div>
          </div>

          {/* Saved Loadouts for this ship */}
          {savedLoadouts.length > 0 && (
            <div className="p-4 border-t border-white/10">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Saved Loadouts for {selectedShip.name}</h3>
              <div className="space-y-2">
                {savedLoadouts.map(saved => (
                  <div key={saved.id} className={`flex items-center justify-between p-2 rounded-lg transition-colors ${editingLoadoutId === saved.id ? 'bg-cyan-500/10 border border-cyan-500/20' : 'bg-white/5'}`}>
                    <button onClick={() => loadSavedLoadout(saved)} data-testid={`load-loadout-${saved.id}`}
                      className="text-sm text-cyan-400 hover:text-cyan-300 font-medium truncate flex-1 text-left">
                      {saved.loadout_name}
                    </button>
                    <div className="flex items-center gap-1 shrink-0 ml-2">
                      {saved.share_code && (
                        <button onClick={() => { navigator.clipboard.writeText(`${window.location.origin}/shared/${saved.share_code}`); toast.success('Share link copied!'); }}
                          data-testid={`share-loadout-${saved.id}`} className="p-1 hover:bg-cyan-500/20 rounded text-cyan-500" title="Copy share link">
                          <Share2 className="w-3 h-3" />
                        </button>
                      )}
                      <button onClick={() => deleteSavedLoadout(saved.id, saved.loadout_name)} data-testid={`delete-loadout-${saved.id}`}
                        className="p-1 hover:bg-red-500/20 rounded text-red-500">
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Slot list */}
        <div className="lg:col-span-2 space-y-3">
          {slotDefs.length === 0 && (
            <div className="glass-panel rounded-2xl p-8 text-center">
              <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
              <p className="text-gray-400">This ship has no customizable hardpoints.</p>
            </div>
          )}

          {SLOT_TYPES.map(st => {
            const slots = slotDefs.filter(s => s.type === 'component' && s.componentType === st.componentType);
            if (slots.length === 0) return null;
            return (
              <div key={st.key}>
                <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                  <st.icon className="w-4 h-4" style={{ color: st.color }} />
                  {st.label} (Size {slots[0].maxSize})
                </h3>
                <div className="space-y-2">
                  {slots.map(slot => (
                    <SlotRow key={slot.id} slot={slot} item={loadout[slot.id]} onSelect={() => { setActiveSlot(slot); setItemSearch(''); }} onRemove={() => removeItem(slot.id)} onInspect={() => loadout[slot.id] && inspectSlotItem(slot.id, loadout[slot.id])} />
                  ))}
                </div>
              </div>
            );
          })}

          {weaponSlots.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                <Crosshair className="w-4 h-4 text-red-500" />
                Weapon Hardpoints
              </h3>
              <div className="space-y-2">
                {slotDefs.filter(s => s.type === 'weapon').map(slot => (
                  <SlotRow key={slot.id} slot={slot} item={loadout[slot.id]} onSelect={() => { setActiveSlot(slot); setItemSearch(''); }} onRemove={() => removeItem(slot.id)} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Save Loadout Dialog */}
      <AnimatePresence>
        {showSaveDialog && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) setShowSaveDialog(false); }}>
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}
              className="glass-panel rounded-2xl p-6 max-w-md w-full" data-testid="save-loadout-dialog">
              <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
                {editingLoadoutId ? 'Update Loadout' : 'Save Loadout'}
              </h2>
              <input type="text" value={loadoutName} onChange={e => setLoadoutName(e.target.value)}
                placeholder="Loadout name (e.g. PvP Build, Mining Setup)" data-testid="loadout-name-input"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all mb-4"
                autoFocus onKeyDown={e => e.key === 'Enter' && saveLoadout()} />
              <div className="flex gap-3">
                <button onClick={saveLoadout} data-testid="confirm-save-btn"
                  className="flex-1 py-2.5 rounded-xl font-bold text-black" style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}>
                  {editingLoadoutId ? 'Update' : 'Save'}
                </button>
                <button onClick={() => setShowSaveDialog(false)} className="px-6 py-2.5 bg-white/5 text-gray-400 rounded-xl hover:bg-white/10 transition-colors">
                  Cancel
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Item Selector Modal */}
      <AnimatePresence>
        {activeSlot && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={e => { if (e.target === e.currentTarget) { setActiveSlot(null); setItemSearch(''); } }}>
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}
              className="glass-panel rounded-3xl max-w-3xl w-full max-h-[80vh] overflow-hidden" data-testid="item-selector-modal">
              <div className="p-6 border-b border-white/10 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color: activeSlot.color }}>
                      {activeSlot.label} - Max Size {activeSlot.maxSize}
                    </h2>
                    <p className="text-sm text-gray-400">
                      {activeSlot.type === 'weapon' ? `Only weapons size ${activeSlot.maxSize} or smaller` : `Only size ${activeSlot.maxSize} ${activeSlot.componentType} components`}
                    </p>
                  </div>
                  <button onClick={() => { setActiveSlot(null); setItemSearch(''); }} className="p-2 hover:bg-white/10 rounded-lg"><X className="w-6 h-6 text-gray-400" /></button>
                </div>
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input type="text" value={itemSearch} onChange={e => setItemSearch(e.target.value)}
                    placeholder="Search compatible items..." data-testid="item-search-input"
                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all"
                    autoFocus />
                </div>
              </div>
              <div className="p-4 overflow-y-auto max-h-[55vh]">
                {(() => {
                  const items = getCompatibleItems(activeSlot);
                  if (items.length === 0) return <p className="text-center text-gray-500 py-8">No compatible items found for this slot</p>;
                  return (
                    <div className="space-y-2">
                      {items.map(item => (
                        <button key={item.id} onClick={() => assignItem(activeSlot.id, item)} data-testid={`equip-item-${item.id}`}
                          className="w-full glass-panel rounded-xl p-4 hover:border-cyan-500/50 transition-all text-left flex items-center justify-between group">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-bold text-white text-sm">{item.name}</span>
                              <span className="text-[10px] px-1.5 py-0.5 rounded border" style={{ color: activeSlot.color, borderColor: `${activeSlot.color}40`, backgroundColor: `${activeSlot.color}15` }}>
                                S{item.size}
                              </span>
                            </div>
                            <div className="text-xs text-gray-500">{item.manufacturer}</div>
                            <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
                              {item.damage > 0 && <span>DMG: {item.damage}</span>}
                              {item.rate > 0 && <span>Rate: {item.rate}</span>}
                              {item.output > 0 && <span>Output: {item.output}</span>}
                              {item.speed > 0 && <span>Speed: {item.speed.toLocaleString()}</span>}
                            </div>
                          </div>
                          <div className="text-right shrink-0 ml-4">
                            {item.cost_auec > 0 && <div className="text-yellow-400 font-semibold text-sm">{item.cost_auec.toLocaleString()} aUEC</div>}
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity text-cyan-500 text-xs mt-1">Equip</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  );
                })()}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Item Inspect Popup */}
      <AnimatePresence>
        {inspectItem && <ItemDetailPopup item={inspectItem} loading={inspectLoading} onClose={() => setInspectItem(null)} />}
      </AnimatePresence>

      {/* Shopping List Modal */}
      <AnimatePresence>
        {shoppingList && <ShoppingListModal data={shoppingList} onClose={() => setShoppingList(null)} />}
      </AnimatePresence>
    </div>
  );
};

const SlotRow = ({ slot, item, onSelect, onRemove, onInspect }) => (
  <div className="glass-panel rounded-xl p-4 flex items-center justify-between gap-3 group" data-testid={`slot-${slot.id}`}>
    <div className="flex items-center gap-3 min-w-0 flex-1">
      <slot.icon className="w-5 h-5 shrink-0" style={{ color: slot.color }} />
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-300">{slot.label}</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-500">
            {slot.type === 'weapon' ? `Max S${slot.maxSize}` : `S${slot.maxSize}`}
          </span>
        </div>
        {item ? (
          <div className="flex items-center gap-2 mt-0.5">
            <Check className="w-3 h-3 text-green-500 shrink-0" />
            <button onClick={onInspect} data-testid={`inspect-slot-${slot.id}`}
              className="text-sm text-white font-semibold truncate hover:text-cyan-400 transition-colors cursor-pointer">{item.name}</button>
            {item.cost_auec > 0 && <span className="text-xs text-yellow-400 shrink-0">{item.cost_auec.toLocaleString()} aUEC</span>}
          </div>
        ) : (
          <span className="text-xs text-gray-600">Empty - click to equip</span>
        )}
      </div>
    </div>
    <div className="flex items-center gap-2 shrink-0">
      {item && (
        <button onClick={onRemove} data-testid={`remove-${slot.id}`} className="p-1.5 hover:bg-red-500/20 rounded-lg transition-colors">
          <X className="w-4 h-4 text-red-500" />
        </button>
      )}
      <button onClick={onSelect} data-testid={`equip-${slot.id}`} className="px-3 py-1.5 bg-cyan-500/10 text-cyan-500 rounded-lg hover:bg-cyan-500/20 transition-colors text-xs font-semibold">
        {item ? 'Change' : 'Equip'}
      </button>
    </div>
  </div>
);

const ItemDetailPopup = ({ item, loading, onClose }) => {
  const locations = item.locations || [];
  const bestPrice = locations.filter(l => l.price > 0).sort((a, b) => a.price - b.price)[0];
  const isWeapon = item.type && (item.alpha_damage > 0 || item.dps > 0 || item.fire_rate > 0);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={onClose} data-testid="item-detail-popup">
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
        className="glass-panel rounded-2xl max-w-xl w-full max-h-[80vh] overflow-y-auto p-6"
        onClick={e => e.stopPropagation()}>
        <div className="flex items-start justify-between mb-5">
          <div>
            <h2 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{item.name}</h2>
            <p className="text-sm text-gray-400">{item.manufacturer}</p>
          </div>
          <button onClick={onClose} data-testid="close-item-detail"
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mb-5">
          {item.type && <span className="px-3 py-1 rounded-lg text-xs font-bold border border-cyan-500/30 bg-cyan-500/20 text-cyan-400">{item.type}</span>}
          {item.size && <span className="px-3 py-1 rounded-lg text-xs font-bold border border-cyan-500/30 bg-cyan-500/20 text-cyan-400">Size {item.size}</span>}
          {item.grade && <span className="px-3 py-1 rounded-lg text-xs font-bold border border-amber-500/30 bg-amber-500/20 text-amber-400">Grade {item.grade}</span>}
          {item.item_class && <span className="px-3 py-1 rounded-lg text-xs font-bold border border-purple-500/30 bg-purple-500/20 text-purple-400">{item.item_class}</span>}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 mb-5">
          {isWeapon ? (
            <>
              {item.alpha_damage > 0 && <MiniStat label="Alpha DMG" value={Number(item.alpha_damage).toFixed(1)} />}
              {item.dps > 0 && <MiniStat label="DPS" value={Number(item.dps).toFixed(1)} />}
              {item.fire_rate > 0 && <MiniStat label="Fire Rate" value={`${item.fire_rate} RPM`} />}
              {item.range > 0 && <MiniStat label="Range" value={`${Number(item.range).toLocaleString()} m`} />}
              {item.ammo_speed > 0 && <MiniStat label="Ammo Speed" value={`${Number(item.ammo_speed).toLocaleString()} m/s`} />}
              {item.max_ammo > 0 && <MiniStat label="Max Ammo" value={Number(item.max_ammo).toLocaleString()} />}
            </>
          ) : (
            <>
              {item.output > 0 && <MiniStat label={item.type === 'Shield' ? 'Shield HP' : item.type === 'Power' ? 'Power Gen' : item.type === 'Cooler' ? 'Cooling' : 'Output'} value={Number(item.output).toLocaleString()} />}
              {item.rate > 0 && <MiniStat label={item.type === 'Shield' ? 'Regen Rate' : 'Rate'} value={Number(item.rate).toLocaleString()} />}
              {item.speed > 0 && <MiniStat label="QT Speed" value={`${Number(item.speed).toLocaleString()} m/s`} />}
              {item.durability > 0 && <MiniStat label="Durability" value={`${Number(item.durability).toLocaleString()} HP`} />}
              {item.power_draw > 0 && <MiniStat label="Power Draw" value={item.power_draw} />}
            </>
          )}
        </div>

        {item.description && (
          <div className="mb-5">
            <h3 className="text-xs text-gray-500 uppercase font-bold mb-1.5">Description</h3>
            <p className="text-sm text-gray-300 leading-relaxed">{item.description.replace(/\\n/g, ' ').replace(/\n/g, ' ')}</p>
          </div>
        )}

        <div>
          <h3 className="text-xs text-gray-500 uppercase font-bold mb-2.5 flex items-center gap-2">
            <MapPin className="w-3.5 h-3.5" /> Purchase Locations
            {loading && <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />}
          </h3>
          {locations.length > 0 ? (
            <div className="space-y-1.5 max-h-48 overflow-y-auto">
              {locations.map((loc, i) => (
                <div key={i} className={`flex items-center justify-between text-sm p-2 rounded-lg ${bestPrice && loc.price === bestPrice.price ? 'bg-green-500/10 border border-green-500/20' : 'bg-white/5'}`}>
                  <span className="text-gray-300 flex-1 mr-3 text-xs">{loc.location}</span>
                  {loc.price > 0 && (
                    <span className={`font-bold text-xs whitespace-nowrap ${bestPrice && loc.price === bestPrice.price ? 'text-green-400' : 'text-yellow-400'}`}
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

const MiniStat = ({ label, value }) => (
  <div className="bg-white/5 rounded-lg p-2.5 text-center">
    <div className="text-[10px] text-gray-500 uppercase font-semibold mb-0.5">{label}</div>
    <div className="text-sm font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{value}</div>
  </div>
);

const ShoppingListModal = ({ data, onClose }) => {
  const { shipName, items, byStore, total, loading } = data;
  const itemsWithPrice = items.filter(i => i.cheapest);
  const itemsNoPrice = items.filter(i => !i.cheapest);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={onClose} data-testid="shopping-list-modal">
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
        className="glass-panel rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6"
        onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-3" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
              <ShoppingCart className="w-6 h-6 text-yellow-400" /> Shopping List
            </h2>
            <p className="text-sm text-gray-400">{shipName} - {items.length} items</p>
          </div>
          <button onClick={onClose} data-testid="close-shopping-list"
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            <span className="ml-3 text-gray-400">Fetching best prices...</span>
          </div>
        ) : (
          <>
            {/* Total Cost Banner */}
            <div className="rounded-xl p-4 mb-6 border border-yellow-500/20" style={{ background: 'linear-gradient(135deg, rgba(255,174,0,0.1), rgba(255,215,0,0.05))' }}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs text-gray-400 uppercase font-semibold">Total Estimated Cost</div>
                  <div className="text-3xl font-bold text-yellow-400" style={{ fontFamily: 'Rajdhani, sans-serif' }} data-testid="shopping-total">
                    {total > 0 ? `${total.toLocaleString()} aUEC` : 'Price unavailable'}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-400">{itemsWithPrice.length} priced / {itemsNoPrice.length} unknown</div>
                  <div className="text-xs text-gray-500">{byStore.length} store{byStore.length !== 1 ? 's' : ''} to visit</div>
                </div>
              </div>
            </div>

            {/* By Store - Shopping Route */}
            {byStore.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xs text-gray-500 uppercase font-bold mb-3 flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5" /> Shopping Route (fewest stops)
                </h3>
                <div className="space-y-3">
                  {byStore.map((store, si) => (
                    <div key={si} className="rounded-xl border border-white/10 overflow-hidden" data-testid={`store-${si}`}>
                      <div className="flex items-center justify-between px-4 py-2.5 bg-white/[0.03]">
                        <div className="flex items-center gap-2">
                          <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs font-bold">{si + 1}</span>
                          <span className="text-sm font-semibold text-white">{store.location}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 font-semibold">{store.items.length} item{store.items.length !== 1 ? 's' : ''}</span>
                        </div>
                        <span className="text-sm font-bold text-yellow-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                          {store.subtotal.toLocaleString()} aUEC
                        </span>
                      </div>
                      <div className="divide-y divide-white/5">
                        {store.items.map((item, ii) => (
                          <div key={ii} className="flex items-center justify-between px-4 py-2 text-sm">
                            <span className="text-gray-300">{item.name}</span>
                            <span className="text-yellow-400 font-semibold text-xs" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{item.price.toLocaleString()} aUEC</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Full Item Breakdown */}
            <div>
              <h3 className="text-xs text-gray-500 uppercase font-bold mb-3 flex items-center gap-2">
                <DollarSign className="w-3.5 h-3.5" /> Full Breakdown
              </h3>
              <div className="space-y-1.5">
                {items.map((r, i) => (
                  <div key={i} className="flex items-center justify-between text-sm p-2.5 rounded-lg bg-white/[0.03]" data-testid={`breakdown-item-${i}`}>
                    <div className="flex-1 min-w-0 mr-3">
                      <div className="text-white font-medium text-sm truncate">{r.name}</div>
                      {r.cheapest ? (
                        <div className="text-[10px] text-gray-500 truncate">{r.cheapest.location}</div>
                      ) : (
                        <div className="text-[10px] text-gray-600 italic">No price data</div>
                      )}
                    </div>
                    {r.cheapest ? (
                      <span className="text-yellow-400 font-bold text-sm whitespace-nowrap" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                        {r.cheapest.price.toLocaleString()} aUEC
                      </span>
                    ) : (
                      <span className="text-gray-600 text-xs">--</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </motion.div>
    </motion.div>
  );
};

export default LoadoutBuilder;
