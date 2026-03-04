import { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Ship, Plus, Search, Scale } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

const Ships = () => {
  const { API } = useAuth();
  const navigate = useNavigate();
  const [ships, setShips] = useState([]);
  const [filteredShips, setFilteredShips] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedManufacturer, setSelectedManufacturer] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchShips = async () => {
      try {
        const response = await axios.get(`${API}/ships`);
        setShips(response.data.data || []);
        setFilteredShips(response.data.data || []);
      } catch (error) {
        toast.error('Failed to load ships');
      } finally {
        setLoading(false);
      }
    };
    fetchShips();
  }, [API]);

  useEffect(() => {
    let result = ships;

    if (searchQuery) {
      result = result.filter((ship) =>
        ship.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ship.manufacturer.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedManufacturer !== 'all') {
      result = result.filter((ship) => ship.manufacturer === selectedManufacturer);
    }

    setFilteredShips(result);
  }, [searchQuery, selectedManufacturer, ships]);

  const manufacturers = ['all', ...new Set(ships.map((s) => s.manufacturer))];

  const addToFleet = async (ship) => {
    try {
      await axios.post(`${API}/fleet/add`, ship);
      toast.success(`${ship.name} added to your fleet`);
    } catch (error) {
      toast.error('Failed to add ship to fleet');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading ships...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8" data-testid="ships-page">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-5xl font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Ship Database
          </h1>
          <button
            onClick={() => navigate('/compare')}
            className="px-6 py-3 rounded-full border border-cyan-500/30 text-cyan-500 hover:bg-cyan-500 hover:text-black transition-all"
            style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600 }}
          >
            <Scale className="w-5 h-5 inline mr-2" />
            Compare Ships
          </button>
        </div>
        <p className="text-gray-400" style={{ fontFamily: 'Inter, sans-serif' }}>
          Explore and manage your spacecraft collection
        </p>
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search ships..."
              data-testid="search-input"
              className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
            />
          </div>

          {/* Manufacturer Filter */}
          <select
            value={selectedManufacturer}
            onChange={(e) => setSelectedManufacturer(e.target.value)}
            data-testid="manufacturer-filter"
            className="px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
          >
            {manufacturers.map((manufacturer) => (
              <option key={manufacturer} value={manufacturer} className="bg-gray-900">
                {manufacturer === 'all' ? 'All Manufacturers' : manufacturer}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Ships Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredShips.map((ship, index) => (
          <ShipCard key={`${ship.id}-${index}`} ship={ship} index={index} onAddToFleet={addToFleet} />
        ))}
      </div>

      {filteredShips.length === 0 && (
        <div className="text-center py-12" data-testid="no-ships-message">
          <Ship className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No ships found matching your criteria</p>
        </div>
      )}
    </div>
  );
};

export default Ships;