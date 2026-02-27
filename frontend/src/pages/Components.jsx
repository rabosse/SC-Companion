import { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Box, Search, Zap, Shield, Cpu } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const Components = () => {
  const { API } = useAuth();
  const [components, setComponents] = useState([]);
  const [filteredComponents, setFilteredComponents] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const response = await axios.get(`${API}/components`);
        setComponents(response.data.data || []);
        setFilteredComponents(response.data.data || []);
      } catch (error) {
        toast.error('Failed to load components');
      } finally {
        setLoading(false);
      }
    };
    fetchComponents();
  }, [API]);

  useEffect(() => {
    let result = components;

    if (searchQuery) {
      result = result.filter((component) =>
        component.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        component.manufacturer.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedType !== 'all') {
      result = result.filter((component) => component.type === selectedType);
    }

    setFilteredComponents(result);
  }, [searchQuery, selectedType, components]);

  const types = ['all', ...new Set(components.map((c) => c.type))];

  const getTypeIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'shield':
        return Shield;
      case 'power':
        return Zap;
      case 'quantum':
      case 'cooler':
        return Cpu;
      default:
        return Box;
    }
  };

  const getTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'shield':
        return '#00D4FF';
      case 'power':
        return '#FFAE00';
      case 'quantum':
        return '#D4AF37';
      case 'cooler':
        return '#00FF9D';
      default:
        return '#FFFFFF';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading components...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8" data-testid="components-page">
      {/* Header */}
      <div>
        <h1 className="text-5xl font-bold mb-4 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Component Catalog
        </h1>
        <p className="text-gray-400" style={{ fontFamily: 'Inter, sans-serif' }}>
          Ship components, stock items and premium upgrades
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
              placeholder="Search components..."
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

      {/* Components Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredComponents.map((component, index) => {
          const Icon = getTypeIcon(component.type);
          const color = getTypeColor(component.type);

          return (
            <motion.div
              key={component.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass-panel rounded-2xl p-6 hover:scale-105 transition-transform duration-300"
              data-testid={`component-card-${component.id}`}
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className="w-8 h-8" style={{ color }} />
                <span className="text-xs px-2 py-1 rounded-full border" style={{ backgroundColor: `${color}20`, color, borderColor: `${color}30` }}>
                  Size {component.size}
                </span>
              </div>

              <h3 className="text-lg font-bold text-white mb-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                {component.name}
              </h3>
              <p className="text-sm text-gray-400 mb-2">{component.manufacturer}</p>

              <div className="flex items-center space-x-2 mb-4">
                <span className="text-xs px-2 py-1 bg-white/5 text-gray-300 rounded">{component.type}</span>
                <span className="text-xs px-2 py-1 bg-white/5 text-gray-300 rounded">Grade {component.grade}</span>
              </div>

              <div className="text-sm space-y-1">
                {component.power && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Power Draw:</span>
                    <span className="text-white font-semibold">{component.power} MW</span>
                  </div>
                )}
                {component.output && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Output:</span>
                    <span className="text-white font-semibold">{component.output} W</span>
                  </div>
                )}
                {component.rate && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Rate:</span>
                    <span className="text-white font-semibold">{component.rate}</span>
                  </div>
                )}
                {component.speed && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Speed:</span>
                    <span className="text-white font-semibold">{component.speed} km/s</span>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredComponents.length === 0 && (
        <div className="text-center py-12" data-testid="no-components-message">
          <Box className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No components found matching your criteria</p>
        </div>
      )}
    </div>
  );
};

export default Components;