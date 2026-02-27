import { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Crosshair, Search, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const Weapons = () => {
  const { API } = useAuth();
  const [weapons, setWeapons] = useState([]);
  const [filteredWeapons, setFilteredWeapons] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [loading, setLoading] = useState(true);

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
      result = result.filter((weapon) =>
        weapon.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        weapon.manufacturer.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedType !== 'all') {
      result = result.filter((weapon) => weapon.type === selectedType);
    }

    setFilteredWeapons(result);
  }, [searchQuery, selectedType, weapons]);

  const types = ['all', ...new Set(weapons.map((w) => w.type))];

  const getTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'energy':
        return '#00D4FF';
      case 'ballistic':
        return '#FFAE00';
      case 'missile':
        return '#FF0055';
      default:
        return '#FFFFFF';
    }
  };

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
      {/* Header */}
      <div>
        <h1 className="text-5xl font-bold mb-4 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Weapons Arsenal
        </h1>
        <p className="text-gray-400" style={{ fontFamily: 'Inter, sans-serif' }}>
          Ship weapons, stock ordnance and tactical upgrades
        </p>
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search weapons..."
              data-testid="search-input"
              className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
            />
          </div>

          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            data-testid="type-filter"
            className="px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
          >
            {types.map((type) => (
              <option key={type} value={type} className="bg-gray-900">
                {type === 'all' ? 'All Types' : type}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Weapons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredWeapons.map((weapon, index) => {
          const color = getTypeColor(weapon.type);

          return (
            <motion.div
              key={weapon.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass-panel rounded-2xl p-6 hover:scale-105 transition-transform duration-300"
              data-testid={`weapon-card-${weapon.id}`}
            >
              <div className="flex items-center justify-between mb-4">
                <Crosshair className="w-8 h-8" style={{ color }} />
                <span className="text-xs px-2 py-1 rounded-full border" style={{ backgroundColor: `${color}20`, color, borderColor: `${color}30` }}>
                  Size {weapon.size}
                </span>
              </div>

              <h3 className="text-lg font-bold text-white mb-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                {weapon.name}
              </h3>
              <p className="text-sm text-gray-400 mb-2">{weapon.manufacturer}</p>

              <div className="flex items-center space-x-2 mb-4">
                <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: `${color}20`, color }}>
                  {weapon.type}
                </span>
              </div>

              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-500">Damage</span>
                    <span className="text-white font-semibold">{weapon.damage}</span>
                  </div>
                  <div className="stat-bar">
                    <div className="stat-bar-fill" style={{ width: `${Math.min((weapon.damage / 1000) * 100, 100)}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-500">Fire Rate</span>
                    <span className="text-white font-semibold">{weapon.rate} RPM</span>
                  </div>
                  <div className="stat-bar">
                    <div className="stat-bar-fill" style={{ width: `${Math.min((weapon.rate / 1000) * 100, 100)}%` }}></div>
                  </div>
                </div>

                {weapon.ammo_per_mag && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Ammo/Mag:</span>
                    <span className="text-white font-semibold">{weapon.ammo_per_mag}</span>
                  </div>
                )}
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
    </div>
  );
};

export default Weapons;