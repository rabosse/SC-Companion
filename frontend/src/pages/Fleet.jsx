import { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Trash2, Search, TrendingUp, Package, Users, DollarSign } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import SpaceshipIcon from '../components/SpaceshipIcon';

const Fleet = () => {
  const { API } = useAuth();
  const [fleet, setFleet] = useState([]);
  const [filteredFleet, setFilteredFleet] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [ships, setShips] = useState([]);

  const fetchFleet = async () => {
    try {
      const [fleetRes, shipsRes] = await Promise.all([
        axios.get(`${API}/fleet/my`),
        axios.get(`${API}/ships`)
      ]);
      setFleet(fleetRes.data.data || []);
      setFilteredFleet(fleetRes.data.data || []);
      setShips(shipsRes.data.data || []);
    } catch (error) {
      toast.error('Failed to load your fleet');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFleet();
  }, [API]);

  useEffect(() => {
    if (searchQuery) {
      const result = fleet.filter((item) =>
        item.ship_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.manufacturer.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredFleet(result);
    } else {
      setFilteredFleet(fleet);
    }
  }, [searchQuery, fleet]);

  const removeFromFleet = async (fleetId) => {
    try {
      await axios.delete(`${API}/fleet/${fleetId}`);
      toast.success('Removed from your fleet');
      await fetchFleet();
    } catch (error) {
      toast.error('Failed to remove from fleet');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading your fleet...</p>
        </div>
      </div>
    );
  }

  // Calculate fleet statistics
  const fleetStats = fleet.reduce((stats, item) => {
    const shipData = ships.find(s => s.id === item.ship_id);
    if (shipData) {
      stats.totalCargo += shipData.cargo || 0;
      stats.totalCrew += parseInt(shipData.crew) || 0;
      stats.totalValue += shipData.price || 0;
    }
    return stats;
  }, { totalCargo: 0, totalCrew: 0, totalValue: 0 });

  const statsCards = [
    { icon: SpaceshipIcon, label: 'Total Ships', value: fleet.length, color: '#00D4FF' },
    { icon: Package, label: 'Total Cargo (SCU)', value: fleetStats.totalCargo, color: '#D4AF37' },
    { icon: Users, label: 'Total Crew', value: fleetStats.totalCrew, color: '#00FF9D' },
    { icon: DollarSign, label: 'Fleet Value (UEC)', value: fleetStats.totalValue.toLocaleString(), color: '#FFAE00' },
  ];

  return (
    <div className="space-y-8" data-testid="fleet-page">
      {/* Header */}
      <div>
        <h1 className="text-5xl font-bold mb-4 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          My Fleet
        </h1>
        <p className="text-gray-400" style={{ fontFamily: 'Inter, sans-serif' }}>
          Your personal collection of ships and vehicles ({fleet.length} total)
        </p>
      </div>

      {/* Search */}
      {fleet.length > 0 && (
        <>
          {/* Fleet Statistics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {statsCards.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="glass-panel rounded-2xl p-6"
                  data-testid={`fleet-stat-${stat.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <Icon className="w-8 h-8" style={{ color: stat.color }} />
                  </div>
                  <div className="text-3xl font-bold mb-1" style={{ fontFamily: 'Rajdhani, sans-serif', color: stat.color }}>
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-400">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>

          {/* Search Bar */}
          <div className="glass-panel rounded-2xl p-6">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search your fleet..."
                data-testid="search-input"
                className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
              />
            </div>
          </div>
        </>
      )}

      {/* Empty State */}
      {fleet.length === 0 && (
        <div className="text-center py-16" data-testid="empty-fleet">
          <div className="glass-panel rounded-3xl p-12 max-w-2xl mx-auto">
            <Ship className="w-24 h-24 text-gray-600 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#FFFFFF' }}>
              Your Fleet is Empty
            </h2>
            <p className="text-gray-400 mb-8">
              Start building your collection by adding ships from the Ship Database
            </p>
            <Link to="/ships">
              <button className="btn-origin">
                Browse Ships
              </button>
            </Link>
          </div>
        </div>
      )}

      {/* Fleet Grid */}
      {filteredFleet.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFleet.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass-panel rounded-2xl overflow-hidden ship-card group"
              data-testid={`fleet-item-${item.id}`}
            >
              <Link to={`/ships/${item.ship_id}`}>
                <div className="h-48 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 radial-glow opacity-50"></div>
                  <Ship className="w-20 h-20 text-cyan-500 relative z-10" />
                </div>
              </Link>

              <div className="p-6">
                <Link to={`/ships/${item.ship_id}`}>
                  <h3 className="text-xl font-bold text-white hover:text-cyan-500 transition-colors mb-2" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                    {item.ship_name}
                  </h3>
                </Link>
                <p className="text-sm text-gray-400 mb-4">{item.manufacturer}</p>

                <div className="text-xs text-gray-500 mb-4">
                  Added: {new Date(item.added_at).toLocaleDateString()}
                </div>

                <button
                  onClick={() => removeFromFleet(item.id)}
                  data-testid={`remove-from-fleet-${item.id}`}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-full border border-red-500/30 text-red-500 hover:bg-red-500 hover:text-white transition-all duration-300"
                  style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600 }}
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Remove</span>
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* No Results */}
      {fleet.length > 0 && filteredFleet.length === 0 && (
        <div className="text-center py-12" data-testid="no-results-message">
          <Ship className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No ships found matching your search</p>
        </div>
      )}
    </div>
  );
};

export default Fleet;