import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../App';
import axios from 'axios';
import { ArrowLeft, Save, RotateCcw } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const LoadoutBuilder = () => {
  const { shipId } = useParams();
  const { API } = useAuth();
  const [ship, setShip] = useState(null);
  const [components, setComponents] = useState([]);
  const [weapons, setWeapons] = useState([]);
  const [loadout, setLoadout] = useState({
    shields: [],
    power: null,
    coolers: [],
    quantum: null,
    weapons: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [shipId]);

  const fetchData = async () => {
    try {
      const [shipsRes, componentsRes, weaponsRes] = await Promise.all([
        axios.get(`${API}/ships`),
        axios.get(`${API}/components`),
        axios.get(`${API}/weapons`),
      ]);

      const foundShip = shipsRes.data.data.find((s) => s.id === shipId);
      setShip(foundShip);
      setComponents(componentsRes.data.data || []);
      setWeapons(weaponsRes.data.data || []);

      // Load saved loadout
      const saved = localStorage.getItem(`loadout_${shipId}`);
      if (saved) {
        setLoadout(JSON.parse(saved));
      }
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const saveLoadout = () => {
    localStorage.setItem(`loadout_${shipId}`, JSON.stringify(loadout));
    toast.success('Loadout saved successfully!');
  };

  const resetLoadout = () => {
    setLoadout({
      shields: [],
      power: null,
      coolers: [],
      quantum: null,
      weapons: [],
    });
    localStorage.removeItem(`loadout_${shipId}`);
    toast.success('Loadout reset to default');
  };

  const selectComponent = (type, component) => {
    if (type === 'power' || type === 'quantum') {
      setLoadout({ ...loadout, [type]: component });
    } else {
      // For arrays (shields, coolers, weapons)
      const maxSlots = type === 'shields' ? 2 : type === 'coolers' ? 2 : 4;
      if (loadout[type].length < maxSlots) {
        setLoadout({ ...loadout, [type]: [...loadout[type], component] });
      } else {
        toast.error(`Maximum ${maxSlots} ${type} slots`);
      }
    }
  };

  const removeComponent = (type, index) => {
    if (type === 'power' || type === 'quantum') {
      setLoadout({ ...loadout, [type]: null });
    } else {
      const newArray = loadout[type].filter((_, i) => i !== index);
      setLoadout({ ...loadout, [type]: newArray });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading loadout builder...</p>
        </div>
      </div>
    );
  }

  if (!ship) return <div>Ship not found</div>;

  const componentsByType = {
    shields: components.filter(c => c.type === 'Shield'),
    power: components.filter(c => c.type === 'Power'),
    coolers: components.filter(c => c.type === 'Cooler'),
    quantum: components.filter(c => c.type === 'Quantum'),
  };

  return (
    <div className="space-y-8" data-testid="loadout-builder-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link to={`/ships/${shipId}`} className="inline-flex items-center space-x-2 text-gray-400 hover:text-cyan-500 transition-colors mb-4">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to {ship.name}</span>
          </Link>
          <h1 className="text-5xl font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Loadout Builder
          </h1>
          <p className="text-gray-400 mt-2">Customize components and weapons for {ship.name}</p>
        </div>
        <div className="flex space-x-3">
          <button onClick={resetLoadout} className="px-6 py-3 rounded-full border border-red-500/30 text-red-500 hover:bg-red-500 hover:text-white transition-all" style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600 }}>
            <RotateCcw className="w-5 h-5 inline mr-2" />
            Reset
          </button>
          <button onClick={saveLoadout} className="btn-origin">
            <Save className="w-5 h-5 inline mr-2" />
            Save Loadout
          </button>
        </div>
      </div>

      {/* Ship Preview */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center space-x-6">
          <img src={ship.image} alt={ship.name} className="w-48 h-32 object-cover rounded-xl" />
          <div>
            <h2 className="text-3xl font-bold mb-2" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#FFFFFF' }}>
              {ship.name}
            </h2>
            <p className="text-gray-400">{ship.manufacturer} • {ship.size} Class</p>
          </div>
        </div>
      </div>

      {/* Loadout Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Shields */}
        <LoadoutSection
          title="Shields"
          slots={loadout.shields}
          maxSlots={2}
          availableComponents={componentsByType.shields}
          onSelect={(comp) => selectComponent('shields', comp)}
          onRemove={(index) => removeComponent('shields', index)}
          color="#00D4FF"
        />

        {/* Power Plant */}
        <LoadoutSection
          title="Power Plant"
          slots={loadout.power ? [loadout.power] : []}
          maxSlots={1}
          availableComponents={componentsByType.power}
          onSelect={(comp) => selectComponent('power', comp)}
          onRemove={() => removeComponent('power')}
          color="#FFAE00"
        />

        {/* Coolers */}
        <LoadoutSection
          title="Coolers"
          slots={loadout.coolers}
          maxSlots={2}
          availableComponents={componentsByType.coolers}
          onSelect={(comp) => selectComponent('coolers', comp)}
          onRemove={(index) => removeComponent('coolers', index)}
          color="#00FF9D"
        />

        {/* Quantum Drive */}
        <LoadoutSection
          title="Quantum Drive"
          slots={loadout.quantum ? [loadout.quantum] : []}
          maxSlots={1}
          availableComponents={componentsByType.quantum}
          onSelect={(comp) => selectComponent('quantum', comp)}
          onRemove={() => removeComponent('quantum')}
          color="#D4AF37"
        />

        {/* Weapons */}
        <div className="lg:col-span-2">
          <LoadoutSection
            title="Weapons"
            slots={loadout.weapons}
            maxSlots={4}
            availableComponents={weapons}
            onSelect={(comp) => selectComponent('weapons', comp)}
            onRemove={(index) => removeComponent('weapons', index)}
            color="#FF0055"
          />
        </div>
      </div>
    </div>
  );
};

const LoadoutSection = ({ title, slots, maxSlots, availableComponents, onSelect, onRemove, color }) => {
  const [showSelector, setShowSelector] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-2xl p-6"
    >
      <h3 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Rajdhani, sans-serif', color }}>
        {title} ({slots.length}/{maxSlots})
      </h3>

      {/* Installed Slots */}
      <div className="space-y-3 mb-4">
        {slots.map((component, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/10">
            <div>
              <div className="font-semibold text-white">{component.name}</div>
              <div className="text-sm text-gray-400">{component.manufacturer} • Size {component.size}</div>
            </div>
            <button
              onClick={() => onRemove(index)}
              className="px-3 py-1 rounded-full bg-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition-all text-sm"
            >
              Remove
            </button>
          </div>
        ))}
        {Array.from({ length: maxSlots - slots.length }).map((_, i) => (
          <div key={`empty-${i}`} className="p-3 border-2 border-dashed border-white/10 rounded-xl text-center text-gray-500">
            Empty Slot
          </div>
        ))}
      </div>

      {/* Add Component Button */}
      {slots.length < maxSlots && (
        <button
          onClick={() => setShowSelector(true)}
          className="w-full py-2 rounded-full border border-cyan-500/30 text-cyan-500 hover:bg-cyan-500 hover:text-black transition-all"
          style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600 }}
        >
          Add {title}
        </button>
      )}

      {/* Component Selector */}
      {showSelector && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel rounded-3xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
          >
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <h3 className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color }}>
                Select {title}
              </h3>
              <button onClick={() => setShowSelector(false)} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                <ArrowLeft className="w-6 h-6 text-gray-400" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableComponents.map(component => (
                  <button
                    key={component.id}
                    onClick={() => {
                      onSelect(component);
                      setShowSelector(false);
                    }}
                    className="glass-panel rounded-xl p-4 hover:border-cyan-500/50 transition-all text-left"
                  >
                    <div className="font-bold text-white mb-1">{component.name}</div>
                    <div className="text-sm text-gray-400 mb-2">{component.manufacturer}</div>
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="px-2 py-1 bg-white/10 rounded">Size {component.size}</span>
                      <span className="px-2 py-1 bg-white/10 rounded">Grade {component.grade || 'A'}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </motion.div>
  );
};

export default LoadoutBuilder;