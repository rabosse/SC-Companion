import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Plus, Search, Scale } from 'lucide-react';
import SpaceshipIcon from '../components/SpaceshipIcon';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

const ShipCard = ({ ship, index, onAddToFleet }) => {
  const [selectedVariant, setSelectedVariant] = useState(null);
  const displayName = selectedVariant ? selectedVariant.name : ship.name;
  const displayImage = selectedVariant?.image || ship.image;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="glass-panel rounded-2xl overflow-hidden ship-card group"
      data-testid={`ship-card-${ship.id}`}
    >
      <Link to={`/ships/${selectedVariant?.id || ship.id}`}>
        <div className="h-48 relative overflow-hidden bg-gradient-to-br from-cyan-500/20 to-blue-600/20">
          {displayImage && (
            <img src={displayImage} alt={displayName} data-testid={`ship-image-${ship.id}`}
              className="w-full h-full object-cover"
              onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }} />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          {!displayImage && (
            <div className="absolute inset-0 flex items-center justify-center">
              <SpaceshipIcon className="w-16 h-16 text-cyan-500/30" />
            </div>
          )}
        </div>
      </Link>

      <div className="p-6">
        <div className="flex items-center justify-between mb-2 gap-2">
          <Link to={`/ships/${selectedVariant?.id || ship.id}`} className="min-w-0">
            <h3 className="text-xl font-bold text-white hover:text-cyan-500 transition-colors truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
              {displayName}
            </h3>
          </Link>
          <div className="flex items-center gap-1.5 shrink-0">
            {ship.flight_ready === false && (
              <span className="text-xs px-2 py-1 bg-amber-500/20 text-amber-400 rounded-full border border-amber-500/30" data-testid={`not-flight-ready-${ship.id}`}>
                Not Flight Ready
              </span>
            )}
            <span className="text-xs px-2 py-1 bg-cyan-500/20 text-cyan-500 rounded-full border border-cyan-500/30">
              {ship.size}
            </span>
          </div>
        </div>
        <p className="text-sm text-gray-400 mb-3">{ship.manufacturer}</p>

        {/* Variant Dropdown */}
        {ship.variants?.length > 0 && (
          <div className="mb-3">
            <select
              value={selectedVariant?.name || ''}
              onChange={(e) => {
                if (!e.target.value) { setSelectedVariant(null); return; }
                const v = ship.variants.find(v => v.name === e.target.value);
                setSelectedVariant(v || null);
              }}
              data-testid={`variant-select-${ship.id}`}
              className="w-full px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500 transition-all"
              style={{ colorScheme: 'dark' }}
            >
              <option value="" className="bg-gray-900">{ship.name} (Base)</option>
              {ship.variants.map(v => (
                <option key={v.name} value={v.name} className="bg-gray-900">{v.name}</option>
              ))}
            </select>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 text-sm mb-4">
          <div>
            <span className="text-gray-500 block">Crew</span>
            <span className="text-white font-semibold">{ship.crew_max ? `${ship.crew_min}-${ship.crew_max}` : (ship.crew || 'N/A')}</span>
          </div>
          <div>
            <span className="text-gray-500 block">Cargo</span>
            <span className="text-white font-semibold">{ship.cargo ?? 0} SCU</span>
          </div>
          <div>
            <span className="text-gray-500 block">Length</span>
            <span className="text-white font-semibold">{ship.length}m</span>
          </div>
          {ship.price_auec > 0 && (
            <div>
              <span className="text-gray-500 block">Price</span>
              <span className="text-yellow-400 font-semibold">{ship.price_auec.toLocaleString()} aUEC</span>
            </div>
          )}
        </div>

        <button
          onClick={() => onAddToFleet(selectedVariant || ship)}
          data-testid={`add-to-fleet-${ship.id}`}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-full border border-cyan-500/30 text-cyan-500 hover:bg-cyan-500 hover:text-black transition-all duration-300"
          style={{ fontFamily: 'Rajdhani, sans-serif', fontWeight: 600 }}
        >
          <Plus className="w-4 h-4" />
          <span>Add to Fleet</span>
        </button>
      </div>
    </motion.div>
  );
};

const Ships = () => {
  const { API } = useAuth();
  const navigate = useNavigate();
  const [ships, setShips] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedManufacturer, setSelectedManufacturer] = useState('all');
  const [flightReadyFilter, setFlightReadyFilter] = useState('all');
  const [filterSize, setFilterSize] = useState('all');
  const [filterRole, setFilterRole] = useState('all');
  const [filterCargo, setFilterCargo] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchShips = async () => {
      try {
        const response = await axios.get(`${API}/ships`);
        setShips(response.data.data || []);
      } catch (error) {
        toast.error('Failed to load ships');
      } finally {
        setLoading(false);
      }
    };
    fetchShips();
  }, [API]);

  const filterOptions = useMemo(() => {
    const sizes = new Set();
    const roles = new Set();
    const mfgs = new Set();
    ships.forEach(s => {
      if (s.size) sizes.add(s.size);
      if (s.role) roles.add(s.role);
      if (s.manufacturer) mfgs.add(s.manufacturer);
    });
    const sizeOrder = ['Snub', 'Small', 'Medium', 'Large', 'Capital'];
    return {
      sizes: [...sizes].sort((a, b) => sizeOrder.indexOf(a) - sizeOrder.indexOf(b)),
      roles: [...roles].sort(),
      mfgs: ['all', ...[...mfgs].sort()],
    };
  }, [ships]);

  const filteredShips = useMemo(() => {
    let result = ships;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter((ship) =>
        ship.name.toLowerCase().includes(q) ||
        ship.manufacturer.toLowerCase().includes(q) ||
        ship.variants?.some(v => v.name.toLowerCase().includes(q))
      );
    }

    if (selectedManufacturer !== 'all') {
      result = result.filter((ship) => ship.manufacturer === selectedManufacturer);
    }

    if (flightReadyFilter === 'ready') {
      result = result.filter((ship) => ship.flight_ready !== false);
    } else if (flightReadyFilter === 'not_ready') {
      result = result.filter((ship) => ship.flight_ready === false);
    }

    if (filterSize !== 'all') {
      result = result.filter((ship) => ship.size === filterSize);
    }

    if (filterRole !== 'all') {
      result = result.filter((ship) => ship.role === filterRole);
    }

    if (filterCargo === 'has') {
      result = result.filter((ship) => (ship.cargo || 0) > 0);
    } else if (filterCargo === 'none') {
      result = result.filter((ship) => !(ship.cargo > 0));
    }

    return result;
  }, [ships, searchQuery, selectedManufacturer, flightReadyFilter, filterSize, filterRole, filterCargo]);

  const hasActiveFilters = flightReadyFilter !== 'all' || filterSize !== 'all' || filterRole !== 'all' || filterCargo !== 'all' || selectedManufacturer !== 'all';

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
        <div className="flex flex-col gap-4">
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
              {filterOptions.mfgs.map((manufacturer) => (
                <option key={manufacturer} value={manufacturer} className="bg-gray-900">
                  {manufacturer === 'all' ? 'All Manufacturers' : manufacturer}
                </option>
              ))}
            </select>
          </div>

          {/* Flight Ready Toggle + Sort Filters */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Flight Ready Toggle */}
            <div className="flex gap-1.5" data-testid="flight-ready-toggle">
              {[
                { key: 'all', label: 'All' },
                { key: 'ready', label: 'Flight Ready' },
                { key: 'not_ready', label: 'Not Flight Ready' },
              ].map(opt => (
                <button
                  key={opt.key}
                  onClick={() => setFlightReadyFilter(opt.key)}
                  data-testid={`flight-filter-${opt.key}`}
                  className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
                    flightReadyFilter === opt.key
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            <div className="w-px h-6 bg-white/10 hidden sm:block" />

            {/* Size Filter */}
            <select value={filterSize} onChange={e => setFilterSize(e.target.value)} data-testid="filter-size"
              className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-cyan-500">
              <option value="all" className="bg-gray-900">Size: All</option>
              {filterOptions.sizes.map(s => <option key={s} value={s} className="bg-gray-900">{s}</option>)}
            </select>

            {/* Role Filter */}
            <select value={filterRole} onChange={e => setFilterRole(e.target.value)} data-testid="filter-role"
              className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-cyan-500">
              <option value="all" className="bg-gray-900">Type: All</option>
              {filterOptions.roles.map(r => <option key={r} value={r} className="bg-gray-900">{r}</option>)}
            </select>

            {/* Cargo Filter */}
            <select value={filterCargo} onChange={e => setFilterCargo(e.target.value)} data-testid="filter-cargo"
              className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-cyan-500">
              <option value="all" className="bg-gray-900">Storage: All</option>
              <option value="has" className="bg-gray-900">Has Cargo</option>
              <option value="none" className="bg-gray-900">No Cargo</option>
            </select>

            {hasActiveFilters && (
              <button
                onClick={() => { setFlightReadyFilter('all'); setFilterSize('all'); setFilterRole('all'); setFilterCargo('all'); setSelectedManufacturer('all'); }}
                data-testid="clear-all-filters"
                className="text-xs text-cyan-500 hover:text-cyan-400 transition-colors ml-auto"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500" data-testid="ship-count">
          Showing {filteredShips.length} of {ships.length} ships
        </p>
      </div>

      {/* Ships Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredShips.map((ship, index) => (
          <ShipCard key={`${ship.id}-${index}`} ship={ship} index={index} onAddToFleet={addToFleet} />
        ))}
      </div>

      {filteredShips.length === 0 && (
        <div className="text-center py-12" data-testid="no-ships-message">
          <SpaceshipIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No ships found matching your criteria</p>
        </div>
      )}
    </div>
  );
};

export default Ships;