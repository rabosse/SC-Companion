import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../App';
import axios from 'axios';
import { Ship, ArrowLeft, Zap, Shield, Cpu, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const ShipDetail = () => {
  const { shipId } = useParams();
  const { API } = useAuth();
  const [ship, setShip] = useState(null);
  const [upgrades, setUpgrades] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [shipsRes, upgradesRes] = await Promise.all([
          axios.get(`${API}/ships`),
          axios.get(`${API}/upgrades/${shipId}`),
        ]);

        const foundShip = shipsRes.data.data.find((s) => s.id === shipId);
        setShip(foundShip);
        setUpgrades(upgradesRes.data.data);
      } catch (error) {
        toast.error('Failed to load ship details');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [API, shipId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading ship details...</p>
        </div>
      </div>
    );
  }

  if (!ship) {
    return (
      <div className="text-center py-12" data-testid="ship-not-found">
        <Ship className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400 mb-4">Ship not found</p>
        <Link to="/ships" className="text-cyan-500 hover:text-cyan-400">
          ← Back to Ships
        </Link>
      </div>
    );
  }

  const upgradeCategories = [
    { key: 'shields', label: 'Shield Upgrades', icon: Shield, color: '#00D4FF' },
    { key: 'power', label: 'Power Plant', icon: Zap, color: '#FFAE00' },
    { key: 'weapons', label: 'Weapon Systems', icon: TrendingUp, color: '#00FF9D' },
    { key: 'quantum', label: 'Quantum Drive', icon: Cpu, color: '#D4AF37' },
  ];

  return (
    <div className="space-y-8" data-testid="ship-detail-page">
      {/* Back Button */}
      <Link
        to="/ships"
        data-testid="back-to-ships"
        className="inline-flex items-center space-x-2 text-gray-400 hover:text-cyan-500 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Ships</span>
      </Link>

      {/* Ship Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-3xl overflow-hidden"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Ship Image */}
          <div className="h-96 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0 radial-glow opacity-50"></div>
            <Ship className="w-40 h-40 text-cyan-500 relative z-10" />
          </div>

          {/* Ship Info */}
          <div className="p-8 flex flex-col justify-center">
            <div className="flex items-center space-x-3 mb-4">
              <h1 className="text-5xl font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
                {ship.name}
              </h1>
              <span className="px-3 py-1 bg-cyan-500/20 text-cyan-500 rounded-full border border-cyan-500/30 text-sm">
                {ship.size}
              </span>
            </div>
            <p className="text-xl text-gray-400 mb-8">{ship.manufacturer}</p>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <span className="text-sm text-gray-500 block mb-1">Crew Capacity</span>
                <span className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  {ship.crew}
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-500 block mb-1">Cargo (SCU)</span>
                <span className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  {ship.cargo}
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-500 block mb-1">Length (m)</span>
                <span className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  {ship.length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Recommended Upgrades */}
      <div>
        <h2 className="text-3xl font-bold mb-6 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#FFFFFF' }}>
          Recommended Upgrades
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {upgradeCategories.map((category, index) => {
            const Icon = category.icon;
            const categoryUpgrades = upgrades?.[category.key] || [];

            return (
              <motion.div
                key={category.key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-panel rounded-2xl p-6"
                data-testid={`upgrade-category-${category.key}`}
              >
                <div className="flex items-center space-x-3 mb-4">
                  <Icon className="w-6 h-6" style={{ color: category.color }} />
                  <h3 className="text-xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color: category.color }}>
                    {category.label}
                  </h3>
                </div>

                {categoryUpgrades.length > 0 ? (
                  <div className="space-y-3">
                    {categoryUpgrades.map((upgrade) => (
                      <div key={upgrade.id} className="p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="font-semibold text-white mb-1">{upgrade.name}</div>
                        <div className="text-sm text-gray-400">{upgrade.reason}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No upgrades available</p>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ShipDetail;