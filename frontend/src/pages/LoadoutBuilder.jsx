import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Ship, Search, X, Check, Shield, Zap, Cpu, Box, Crosshair, AlertTriangle, Save, Copy, Share2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { Link } from 'react-router-dom';

const SLOT_TYPES = [
  { key: 'shield', label: 'Shields', icon: Shield, color: '#00D4FF', componentType: 'Shield' },
  { key: 'power_plant', label: 'Power Plant', icon: Zap, color: '#FFAE00', componentType: 'Power' },
  { key: 'cooler', label: 'Coolers', icon: Box, color: '#00FF9D', componentType: 'Cooler' },
  { key: 'quantum_drive', label: 'Quantum Drive', icon: Cpu, color: '#D4AF37', componentType: 'Quantum' },
];

const LoadoutBuilder = () => {
  const { API } = useAuth();
  const [ships, setShips] = useState([]);
  const [selectedShip, setSelectedShip] = useState(null);
  const [components, setComponents] = useState([]);
  const [weapons, setWeapons] = useState([]);
  const [loadout, setLoadout] = useState({});
  const [activeSlot, setActiveSlot] = useState(null);
  const [shipSearch, setShipSearch] = useState('');
  const [itemSearch, setItemSearch] = useState('');
  const [savedLoadouts, setSavedLoadouts] = useState([]);
  const [loadoutName, setLoadoutName] = useState('');
  const [showSaveDialog, setShowSaveDialog] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [shipsRes, compsRes, weaponsRes] = await Promise.all([
          axios.get(`${API}/ships`),
          axios.get(`${API}/components`),
          axios.get(`${API}/weapons`),
        ]);
        setShips(shipsRes.data.data || []);
        setComponents(compsRes.data.data || []);
        setWeapons(weaponsRes.data.data || []);
      } catch {
        toast.error('Failed to load data');
      }
    };
    fetchData();
  }, [API]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const hardpoints = useMemo(() => selectedShip?.hardpoints || {}, [selectedShip]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const weaponSlots = useMemo(() => hardpoints.weapons || [], [hardpoints]);

  // Build slot definitions from ship hardpoints
  const slotDefs = useMemo(() => {
    if (!selectedShip) return [];
    const defs = [];

    SLOT_TYPES.forEach(st => {
      const hp = hardpoints[st.key];
      if (hp && hp.count > 0) {
        for (let i = 0; i < hp.count; i++) {
          defs.push({
            id: `${st.key}_${i}`,
            type: 'component',
            componentType: st.componentType,
            maxSize: hp.size,
            label: `${st.label} ${hp.count > 1 ? i + 1 : ''}`.trim(),
            icon: st.icon,
            color: st.color,
          });
        }
      }
    });

    weaponSlots.forEach((maxSize, i) => {
      defs.push({
        id: `weapon_${i}`,
        type: 'weapon',
        maxSize,
        label: `Weapon Hardpoint ${i + 1}`,
        icon: Crosshair,
        color: '#FF0055',
      });
    });

    return defs;
  }, [selectedShip, hardpoints, weaponSlots]);

  // Get compatible items for a slot
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
    setLoadout(prev => {
      const copy = { ...prev };
      delete copy[slotId];
      return copy;
    });
  };

  const clearLoadout = () => {
    setLoadout({});
    toast.success('Loadout cleared');
  };

  const selectShip = async (ship) => {
    setSelectedShip(ship);
    setLoadout({});
    setActiveSlot(null);
    setShipSearch('');
    // Fetch saved loadouts for this ship
    try {
      const res = await axios.get(`${API}/loadouts/${ship.id}`);
      setSavedLoadouts(res.data.data || []);
    } catch {
      setSavedLoadouts([]);
    }
  };

  const saveLoadout = async () => {
    if (!loadoutName.trim()) {
      toast.error('Please enter a loadout name');
      return;
    }
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
      // Refresh saved loadouts
      const loadoutsRes = await axios.get(`${API}/loadouts/${selectedShip.id}`);
      setSavedLoadouts(loadoutsRes.data.data || []);
      if (shareCode) {
        toast.success(`Share code: ${shareCode}`, { duration: 5000 });
      }
    } catch {
      toast.error('Failed to save loadout');
    }
  };

  const loadSavedLoadout = (saved) => {
    setLoadout(saved.slots || {});
    toast.success(`Loaded "${saved.loadout_name}"`);
  };

  const deleteSavedLoadout = async (loadoutId, name) => {
    try {
      await axios.delete(`${API}/loadouts/${loadoutId}`);
      setSavedLoadouts(prev => prev.filter(l => l.id !== loadoutId));
      toast.success(`Deleted "${name}"`);
    } catch {
      toast.error('Failed to delete loadout');
    }
  };

  const filteredShips = useMemo(() => {
    if (!shipSearch) return ships;
    const q = shipSearch.toLowerCase();
    return ships.filter(s => s.name.toLowerCase().includes(q) || s.manufacturer.toLowerCase().includes(q));
  }, [ships, shipSearch]);

  // Calculate loadout total cost
  const totalCost = Object.values(loadout).reduce((sum, item) => sum + (item.cost_auec || 0), 0);

  // Ship selection view
  if (!selectedShip) {
    return (
      <div className="space-y-8" data-testid="loadout-ship-select">
        <div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Loadout Builder
          </h1>
          <p className="text-gray-400">Select a ship to customize its loadout. Only compatible parts will be shown.</p>
        </div>

        <div className="relative max-w-lg">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            value={shipSearch}
            onChange={e => setShipSearch(e.target.value)}
            placeholder="Search ships..."
            data-testid="ship-search-input"
            className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all"
          />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {filteredShips.map(ship => {
            const hp = ship.hardpoints || {};
            const wSlots = hp.weapons || [];
            const hasSlots = wSlots.length > 0 || (hp.shield?.count > 0);

            return (
              <button
                key={ship.id}
                onClick={() => hasSlots && selectShip(ship)}
                data-testid={`select-ship-${ship.id}`}
                className={`glass-panel rounded-xl p-3 text-left transition-all group ${hasSlots ? 'hover:border-cyan-500/50 cursor-pointer' : 'opacity-40 cursor-not-allowed'}`}
              >
                <div className="h-24 bg-gradient-to-br from-cyan-500/10 to-blue-600/10 rounded-lg overflow-hidden mb-2">
                  {ship.image ? (
                    <img src={ship.image} alt={ship.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform" onError={e => { e.target.onerror = null; e.target.style.display = 'none'; }} />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center"><Ship className="w-8 h-8 text-cyan-500/20" /></div>
                  )}
                </div>
                <div className="font-bold text-white text-sm truncate">{ship.name}</div>
                <div className="text-xs text-gray-500 truncate">{ship.manufacturer}</div>
                {hasSlots && (
                  <div className="flex items-center gap-1 mt-1 flex-wrap">
                    {wSlots.length > 0 && (
                      <span className="text-[10px] px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded">{wSlots.length}x wpn</span>
                    )}
                    {hp.shield?.count > 0 && (
                      <span className="text-[10px] px-1.5 py-0.5 bg-cyan-500/20 text-cyan-400 rounded">S{hp.shield.size} shld</span>
                    )}
                  </div>
                )}
                {!hasSlots && (
                  <div className="text-[10px] text-gray-600 mt-1">No slots</div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  // Loadout builder view
  return (
    <div className="space-y-6" data-testid="loadout-builder">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <button onClick={() => { setSelectedShip(null); setLoadout({}); }} data-testid="back-to-ships-btn" className="p-2 hover:bg-white/10 rounded-lg transition-colors">
            <X className="w-6 h-6 text-gray-400" />
          </button>
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
              {selectedShip.name}
            </h1>
            <p className="text-gray-400 text-sm">{selectedShip.manufacturer} - {selectedShip.size} class</p>
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
              <button onClick={() => setShowSaveDialog(true)} data-testid="save-loadout-btn" className="px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors text-sm font-semibold">
                Save Loadout
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

          {/* Saved Loadouts */}
          {savedLoadouts.length > 0 && (
            <div className="p-4 border-t border-white/10">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Saved Loadouts</h3>
              <div className="space-y-2">
                {savedLoadouts.map(saved => (
                  <div key={saved.id} className="flex items-center justify-between p-2 bg-white/5 rounded-lg">
                    <button
                      onClick={() => loadSavedLoadout(saved)}
                      data-testid={`load-loadout-${saved.id}`}
                      className="text-sm text-cyan-400 hover:text-cyan-300 font-medium truncate flex-1 text-left"
                    >
                      {saved.loadout_name}
                    </button>
                    <div className="flex items-center gap-1 shrink-0 ml-2">
                      {saved.share_code && (
                        <button
                          onClick={() => {
                            const url = `${window.location.origin}/shared/${saved.share_code}`;
                            navigator.clipboard.writeText(url);
                            toast.success('Share link copied!');
                          }}
                          data-testid={`share-loadout-${saved.id}`}
                          className="p-1 hover:bg-cyan-500/20 rounded text-cyan-500" title="Copy share link"
                        >
                          <Share2 className="w-3 h-3" />
                        </button>
                      )}
                      <button
                        onClick={() => deleteSavedLoadout(saved.id, saved.loadout_name)}
                        data-testid={`delete-loadout-${saved.id}`}
                        className="p-1 hover:bg-red-500/20 rounded text-red-500"
                      >
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

          {/* Component Slots */}
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
                    <SlotRow key={slot.id} slot={slot} item={loadout[slot.id]} onSelect={() => { setActiveSlot(slot); setItemSearch(''); }} onRemove={() => removeItem(slot.id)} />
                  ))}
                </div>
              </div>
            );
          })}

          {/* Weapon Slots */}
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
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="glass-panel rounded-2xl p-6 max-w-md w-full"
              data-testid="save-loadout-dialog"
            >
              <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
                Save Loadout
              </h2>
              <input
                type="text"
                value={loadoutName}
                onChange={e => setLoadoutName(e.target.value)}
                placeholder="Loadout name (e.g. PvP Build, Mining Setup)"
                data-testid="loadout-name-input"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all mb-4"
                autoFocus
                onKeyDown={e => e.key === 'Enter' && saveLoadout()}
              />
              <div className="flex gap-3">
                <button onClick={saveLoadout} data-testid="confirm-save-btn" className="flex-1 py-2.5 rounded-xl font-bold text-black" style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}>
                  Save
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
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="glass-panel rounded-3xl max-w-3xl w-full max-h-[80vh] overflow-hidden"
              data-testid="item-selector-modal"
            >
              <div className="p-6 border-b border-white/10 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color: activeSlot.color }}>
                      {activeSlot.label} - Max Size {activeSlot.maxSize}
                    </h2>
                    <p className="text-sm text-gray-400">
                      {activeSlot.type === 'weapon'
                        ? `Only weapons size ${activeSlot.maxSize} or smaller`
                        : `Only size ${activeSlot.maxSize} ${activeSlot.componentType} components`}
                    </p>
                  </div>
                  <button onClick={() => { setActiveSlot(null); setItemSearch(''); }} className="p-2 hover:bg-white/10 rounded-lg"><X className="w-6 h-6 text-gray-400" /></button>
                </div>
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    value={itemSearch}
                    onChange={e => setItemSearch(e.target.value)}
                    placeholder="Search compatible items..."
                    data-testid="item-search-input"
                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all"
                    autoFocus
                  />
                </div>
              </div>
              <div className="p-4 overflow-y-auto max-h-[55vh]">
                {(() => {
                  const items = getCompatibleItems(activeSlot);
                  if (items.length === 0) return <p className="text-center text-gray-500 py-8">No compatible items found for this slot</p>;
                  return (
                    <div className="space-y-2">
                      {items.map(item => (
                        <button
                          key={item.id}
                          onClick={() => assignItem(activeSlot.id, item)}
                          data-testid={`equip-item-${item.id}`}
                          className="w-full glass-panel rounded-xl p-4 hover:border-cyan-500/50 transition-all text-left flex items-center justify-between group"
                        >
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
                              {item.location && <span className="text-cyan-400">{item.location}</span>}
                            </div>
                          </div>
                          <div className="text-right shrink-0 ml-4">
                            {item.cost_auec > 0 && (
                              <div className="text-yellow-400 font-semibold text-sm">{item.cost_auec.toLocaleString()} aUEC</div>
                            )}
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
    </div>
  );
};

const SlotRow = ({ slot, item, onSelect, onRemove }) => (
  <div
    className="glass-panel rounded-xl p-4 flex items-center justify-between gap-3 group"
    data-testid={`slot-${slot.id}`}
  >
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
            <span className="text-sm text-white font-semibold truncate">{item.name}</span>
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

export default LoadoutBuilder;
