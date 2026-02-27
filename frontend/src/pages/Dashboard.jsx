import { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Ship, Package, Crosshair, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const { API } = useAuth();
  const [ships, setShips] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [components, setComponents] = useState([]);
  const [weapons, setWeapons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [shipsRes, vehiclesRes, componentsRes, weaponsRes] = await Promise.all([
          axios.get(`${API}/ships`),
          axios.get(`${API}/vehicles`),
          axios.get(`${API}/components`),
          axios.get(`${API}/weapons`),
        ]);
        setShips(shipsRes.data.data || []);
        setVehicles(vehiclesRes.data.data || []);
        setComponents(componentsRes.data.data || []);
        setWeapons(weaponsRes.data.data || []);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [API]);

  const stats = [
    { label: 'Ships Available', value: ships.length, icon: Ship, color: '#00D4FF' },
    { label: 'Ground Vehicles', value: vehicles.length, icon: Package, color: '#D4AF37' },
    { label: 'Components', value: components.length, icon: TrendingUp, color: '#00FF9D' },
    { label: 'Weapons', value: weapons.length, icon: Crosshair, color: '#FFAE00' },
  ];

  const featuredShips = ships.slice(0, 3);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading fleet data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8" data-testid="dashboard-page">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12"
      >
        <h1 className="text-5xl sm:text-6xl font-bold mb-4 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Fleet Command Center
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto" style={{ fontFamily: 'Inter, sans-serif' }}>
          Precision management for the discerning star citizen
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-panel rounded-2xl p-6 hover:scale-105 transition-transform duration-300"
              data-testid={`stat-${stat.label.toLowerCase().replace(' ', '-')}`}
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className="w-8 h-8" style={{ color: stat.color }} />
                <span className="text-xs font-mono uppercase tracking-widest" style={{ color: stat.color, opacity: 0.7 }}>
                  Total
                </span>
              </div>
              <div className="text-4xl font-bold mb-1" style={{ fontFamily: 'Rajdhani, sans-serif', color: stat.color }}>
                {stat.value}
              </div>
              <div className="text-sm text-gray-400">{stat.label}</div>
            </motion.div>
          );
        })}
      </div>

      {/* Featured Ships */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#FFFFFF' }}>
            Featured Ships
          </h2>
          <Link
            to="/ships"
            data-testid="view-all-ships-link"
            className="text-cyan-500 hover:text-cyan-400 transition-colors"
            style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600 }}
          >
            View All →
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredShips.map((ship, index) => (
            <motion.div
              key={ship.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Link to={`/ships/${ship.id}`}>
                <div className="glass-panel rounded-2xl overflow-hidden ship-card group" data-testid={`featured-ship-${ship.id}`}>
                  <div className="h-48 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 flex items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 radial-glow opacity-50"></div>
                    <Ship className="w-20 h-20 text-cyan-500 relative z-10" />
                  </div>
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                        {ship.name}
                      </h3>
                      <span className="text-xs px-2 py-1 bg-cyan-500/20 text-cyan-500 rounded-full border border-cyan-500/30">
                        {ship.size}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 mb-4">{ship.manufacturer}</p>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500 block">Crew</span>
                        <span className="text-white font-semibold">{ship.crew}</span>
                      </div>
                      <div>
                        <span className="text-gray-500 block">Cargo</span>
                        <span className="text-white font-semibold">{ship.cargo} SCU</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;