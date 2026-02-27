import { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Package, Search } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const Vehicles = () => {
  const { API } = useAuth();
  const [vehicles, setVehicles] = useState([]);
  const [filteredVehicles, setFilteredVehicles] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const response = await axios.get(`${API}/vehicles`);
        setVehicles(response.data.data || []);
        setFilteredVehicles(response.data.data || []);
      } catch (error) {
        toast.error('Failed to load vehicles');
      } finally {
        setLoading(false);
      }
    };
    fetchVehicles();
  }, [API]);

  useEffect(() => {
    if (searchQuery) {
      const result = vehicles.filter((vehicle) =>
        vehicle.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        vehicle.manufacturer.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredVehicles(result);
    } else {
      setFilteredVehicles(vehicles);
    }
  }, [searchQuery, vehicles]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading vehicles...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8" data-testid="vehicles-page">
      {/* Header */}
      <div>
        <h1 className="text-5xl font-bold mb-4 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Ground Vehicles
        </h1>
        <p className="text-gray-400" style={{ fontFamily: 'Inter, sans-serif' }}>
          Surface transportation and tactical vehicles
        </p>
      </div>

      {/* Search */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search vehicles..."
            data-testid="search-input"
            className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
          />
        </div>
      </div>

      {/* Vehicles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredVehicles.map((vehicle, index) => (
          <motion.div
            key={vehicle.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="glass-panel rounded-2xl overflow-hidden hover:scale-105 transition-transform duration-300"
            data-testid={`vehicle-card-${vehicle.id}`}
          >
            <div className="h-48 bg-gradient-to-br from-yellow-500/20 to-orange-600/20 flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 radial-glow opacity-50"></div>
              <Package className="w-20 h-20 text-yellow-500 relative z-10" />
            </div>

            <div className="p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  {vehicle.name}
                </h3>
                <span className="text-xs px-2 py-1 bg-yellow-500/20 text-yellow-500 rounded-full border border-yellow-500/30">
                  {vehicle.type}
                </span>
              </div>
              <p className="text-sm text-gray-400 mb-4">{vehicle.manufacturer}</p>

              <div className="text-sm">
                <span className="text-gray-500 block">Crew Capacity</span>
                <span className="text-white font-semibold">{vehicle.crew}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredVehicles.length === 0 && (
        <div className="text-center py-12" data-testid="no-vehicles-message">
          <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No vehicles found matching your criteria</p>
        </div>
      )}
    </div>
  );
};

export default Vehicles;