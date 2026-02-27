import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import axios from 'axios';
import { Ship, ArrowLeft, Zap, Shield, Cpu, TrendingUp, Package, Users, Ruler, Weight, Gauge, DollarSign, Settings, MapPin } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const ShipDetail = () => {
  const { shipId } = useParams();
  const navigate = useNavigate();
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

  const specs = [
    { icon: Users, label: 'Crew', value: ship.crew_max ? `${ship.crew_min}-${ship.crew_max}` : (ship.crew || 'N/A'), color: '#00D4FF' },
    { icon: Package, label: 'Cargo (SCU)', value: ship.cargo ?? 'N/A', color: '#D4AF37' },
    { icon: Ruler, label: 'Length (m)', value: ship.length || 'N/A', color: '#00FF9D' },
    { icon: Ruler, label: 'Beam (m)', value: ship.beam || 'N/A', color: '#00FF9D' },
    { icon: Ruler, label: 'Height (m)', value: ship.height || 'N/A', color: '#00FF9D' },
    { icon: Weight, label: 'Mass (kg)', value: ship.mass?.toLocaleString() || 'N/A', color: '#FFAE00' },
    { icon: Gauge, label: 'SCM Speed (m/s)', value: ship.max_speed || 'N/A', color: '#FF0055' },
    { icon: Shield, label: 'Shield HP', value: ship.shield_hp?.toLocaleString() || 'N/A', color: '#00D4FF' },
    { icon: DollarSign, label: 'Price (UEC)', value: ship.price?.toLocaleString() || 'TBD', color: '#D4AF37' },
  ];

  return (
    <div className="space-y-8" data-testid="ship-detail-page">
      {/* Back Button */}
      <div className="flex items-center justify-between">
        <Link
          to="/ships"
          data-testid="back-to-ships"
          className="inline-flex items-center space-x-2 text-gray-400 hover:text-cyan-500 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Ships</span>
        </Link>
        <button
          onClick={() => navigate(`/ships/${shipId}/loadout`)}
          className="btn-origin"
        >
          <Settings className="w-5 h-5 inline mr-2" />
          Customize Loadout
        </button>
      </div>

      {/* Ship Header with Image */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-3xl overflow-hidden"
      >
        {/* Hero Image */}
        <div className="relative h-96 overflow-hidden bg-gradient-to-br from-cyan-500/20 to-blue-600/20">
          {ship.image ? (
            <img
              src={ship.image}
              alt={ship.name}
              data-testid="ship-detail-image"
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.onerror = null;
                e.target.style.display = 'none';
              }}
            />
          ) : null}
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent"></div>
          <div className="absolute bottom-0 left-0 right-0 p-8">
            <div className="flex items-center space-x-3 mb-2">
              <span className="px-3 py-1 bg-cyan-500/20 text-cyan-500 rounded-full border border-cyan-500/30 text-sm backdrop-blur-sm">
                {ship.size}
              </span>
              <span className="px-3 py-1 bg-white/10 text-white rounded-full text-sm backdrop-blur-sm">
                {ship.role || 'Multi-role'}
              </span>
            </div>
            <h1 className="text-6xl font-bold uppercase mb-2" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
              {ship.name}
            </h1>
            <p className="text-2xl text-gray-300">{ship.manufacturer}</p>
          </div>
        </div>

        {/* Description */}
        <div className="p-8 border-b border-white/5">
          <p className="text-lg text-gray-300 leading-relaxed">
            {ship.description || `The ${ship.name} by ${ship.manufacturer} is a ${ship.size.toLowerCase()}-class vessel designed for versatility and performance in the Star Citizen universe.`}
          </p>
        </div>

        {/* Specifications Grid */}
        <div className="p-8">
          <h2 className="text-3xl font-bold mb-6 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#FFFFFF' }}>
            Technical Specifications
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {specs.map((spec, index) => {
              const Icon = spec.icon;
              return (
                <motion.div
                  key={spec.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4 bg-white/5 rounded-xl border border-white/10"
                >
                  <Icon className="w-6 h-6 mb-2" style={{ color: spec.color }} />
                  <div className="text-xs text-gray-500 mb-1">{spec.label}</div>
                  <div className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color: spec.color }}>
                    {spec.value}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Purchase Locations */}
      {(ship.purchase_locations?.length > 0 || ship.msrp > 0 || ship.pledge_url) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-panel rounded-3xl p-8"
          data-testid="purchase-section"
        >
          <h2 className="text-3xl font-bold mb-6 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#D4AF37' }}>
            Where to Buy
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* In-Game Dealers */}
            {ship.purchase_locations?.length > 0 && (
              <div>
                <h3 className="text-lg font-bold text-cyan-400 mb-3" style={{ fontFamily: 'Rajdhani, sans-serif' }}>In-Game Dealers</h3>
                <div className="space-y-3">
                  {ship.purchase_locations.map((dealer, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <MapPin className="w-5 h-5 text-cyan-400 shrink-0" />
                        <span className="text-white font-medium">{dealer}</span>
                      </div>
                      {ship.price_auec > 0 && (
                        <span className="text-yellow-400 font-bold" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                          {ship.price_auec.toLocaleString()} aUEC
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* RSI Pledge Store */}
            {(ship.msrp > 0 || ship.pledge_url) && (
              <div>
                <h3 className="text-lg font-bold text-yellow-400 mb-3" style={{ fontFamily: 'Rajdhani, sans-serif' }}>RSI Pledge Store</h3>
                <div className="p-4 bg-white/5 rounded-xl border border-white/10 space-y-3">
                  {ship.msrp > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Pledge Price</span>
                      <span className="text-2xl font-bold text-green-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                        ${ship.msrp} USD
                      </span>
                    </div>
                  )}
                  {ship.pledge_url && (
                    <a
                      href={ship.pledge_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      data-testid="pledge-link"
                      className="block text-center py-3 rounded-xl font-bold uppercase tracking-wider transition-all hover:opacity-90"
                      style={{ background: 'linear-gradient(135deg, #D4AF37, #B8860B)', color: '#000', fontFamily: 'Rajdhani, sans-serif' }}
                    >
                      View on RSI Store
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>

          {ship.purchase_locations?.length === 0 && ship.price_auec === 0 && (
            <p className="text-gray-500">No in-game purchase locations found for this ship.</p>
          )}
        </motion.div>
      )}

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