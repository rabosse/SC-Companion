import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Package, Crosshair, Anchor, Wrench, Building2, ArrowRight, Shield, Zap, Cpu, Snowflake, Rocket, Users, Globe, Car } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import SpaceshipIcon from '../components/SpaceshipIcon';

const Dashboard = () => {
  const { API } = useAuth();
  const [ships, setShips] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [fleet, setFleet] = useState([]);
  const [loadouts, setLoadouts] = useState([]);
  const [communityCount, setCommunityCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [fleetFilter, setFleetFilter] = useState('all');
  const [fleetSort, setFleetSort] = useState('name');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [shipsRes, vehiclesRes, fleetRes, loadoutsRes, communityRes] = await Promise.all([
          axios.get(`${API}/ships`),
          axios.get(`${API}/vehicles`),
          axios.get(`${API}/fleet/my`),
          axios.get(`${API}/loadouts/my/all`),
          axios.get(`${API}/community/loadouts?limit=1`),
        ]);
        setShips(shipsRes.data.data || []);
        setVehicles(vehiclesRes.data.data || []);
        setFleet(fleetRes.data.data || []);
        setLoadouts(loadoutsRes.data.data || []);
        setCommunityCount(communityRes.data.total || 0);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [API]);

  const allVehicles = useMemo(() => [...ships, ...vehicles], [ships, vehicles]);

  const fleetShips = useMemo(() => {
    const lookup = {};
    allVehicles.forEach(s => { lookup[s.id] = s; });
    return fleet.map(f => ({ ...f, details: lookup[f.ship_id] }));
  }, [fleet, allVehicles]);

  const filteredFleet = useMemo(() => {
    const SIZE_ORDER = { snub: 0, small: 1, medium: 2, large: 3, capital: 4 };
    let items = fleetShips;
    if (fleetFilter === 'ships') items = items.filter(f => f.details && f.details.type !== 'ground');
    if (fleetFilter === 'land') items = items.filter(f => f.details && f.details.type === 'ground');
    items = [...items];
    if (fleetSort === 'name') items.sort((a, b) => (a.ship_name || '').localeCompare(b.ship_name || ''));
    if (fleetSort === 'size') items.sort((a, b) => (SIZE_ORDER[(a.details?.size || '').toLowerCase()] ?? 99) - (SIZE_ORDER[(b.details?.size || '').toLowerCase()] ?? 99));
    if (fleetSort === 'type') items.sort((a, b) => (a.details?.role || 'zzz').localeCompare(b.details?.role || 'zzz'));
    if (fleetSort === 'manufacturer') items.sort((a, b) => (a.manufacturer || 'zzz').localeCompare(b.manufacturer || 'zzz'));
    if (fleetSort === 'cargo') items.sort((a, b) => (b.details?.cargo || 0) - (a.details?.cargo || 0));
    return items;
  }, [fleetShips, fleetFilter, fleetSort]);

  const fleetStats = useMemo(() => {
    const mfgCount = {};
    fleetShips.forEach(f => {
      const mfg = f.manufacturer || 'Unknown';
      mfgCount[mfg] = (mfgCount[mfg] || 0) + 1;
    });
    const sorted = Object.entries(mfgCount).sort((a, b) => b[1] - a[1]);
    const topManufacturers = sorted.slice(0, 5);
    const uniqueMfgs = Object.keys(mfgCount).length;
    const shipCount = fleetShips.filter(f => !f.details || f.details.type !== 'ground').length;
    const vehicleCount = fleetShips.filter(f => f.details && f.details.type === 'ground').length;
    return { topManufacturers, uniqueMfgs, shipCount, vehicleCount };
  }, [fleetShips]);

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
    <div className="space-y-6" data-testid="dashboard-page">
      {/* Fleet Stats Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4" data-testid="fleet-stats">
        <StatCard label="Ships" value={fleetStats.shipCount} icon={SpaceshipIcon} color="#00D4FF" testId="stat-ships" />
        <StatCard label="Vehicles" value={fleetStats.vehicleCount} icon={Car} color="#D4AF37" testId="stat-vehicles" />
        <StatCard label="Loadouts" value={loadouts.length} icon={Wrench} color="#FF6B35" testId="stat-loadouts" />
        <StatCard label="Manufacturers" value={fleetStats.uniqueMfgs} icon={Building2} color="#A855F7" testId="stat-manufacturers" />
      </div>

      {/* Quick Actions - Horizontal */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="quick-actions">
        <QuickAction to="/ships" label="Browse Ships" icon={SpaceshipIcon} color="#00D4FF" />
        <QuickAction to="/compare" label="Compare Ships" icon={Users} color="#FFAE00" />
        <QuickAction to="/loadout" label="Build Loadout" icon={Wrench} color="#FF6B35" />
        <QuickAction to="/community" label="Community Loadouts" icon={Globe} color="#A855F7" />
      </div>

      {/* MY FLEET + Favorite Manufacturer side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        {/* MY FLEET - Left */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold uppercase tracking-wider" style={{ fontFamily: 'Rajdhani, sans-serif' }}>My Fleet</h2>
            <Link to="/fleet" className="text-sm text-cyan-500 hover:text-cyan-400 flex items-center gap-1" data-testid="manage-fleet-link">
              Manage Fleet <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Filter tabs + Sort */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex gap-2" data-testid="fleet-filter-tabs">
              {['all', 'ships', 'land'].map(f => (
                <button key={f} onClick={() => setFleetFilter(f)} data-testid={`fleet-filter-${f}`}
                  className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${fleetFilter === f ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-500 border border-white/10 hover:text-gray-300'}`}>
                  {f === 'all' ? 'All' : f === 'ships' ? 'Ships' : 'Land'}
                </button>
              ))}
            </div>
            <select value={fleetSort} onChange={e => setFleetSort(e.target.value)} data-testid="fleet-sort"
              className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-cyan-500">
              <option value="name" className="bg-gray-900">Name</option>
              <option value="size" className="bg-gray-900">Size</option>
              <option value="type" className="bg-gray-900">Type</option>
              <option value="manufacturer" className="bg-gray-900">Manufacturer</option>
              <option value="cargo" className="bg-gray-900">Storage (SCU)</option>
            </select>
          </div>

          {/* Fleet List */}
          {filteredFleet.length === 0 ? (
            <div className="glass-panel rounded-2xl p-8 text-center" data-testid="empty-fleet-card">
              <SpaceshipIcon className="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <h3 className="text-base font-bold mb-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>No Ships in Fleet</h3>
              <p className="text-sm text-gray-500 mb-4">Add ships to see them here</p>
              <Link to="/fleet" className="px-4 py-2 rounded-lg text-sm font-semibold text-black inline-block"
                style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}>
                Go to Fleet
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredFleet.map((fs, i) => (
                <FleetCard key={fs.id || i} fs={fs} index={i} />
              ))}
            </div>
          )}
        </div>

        {/* Favorite Manufacturer - Right sidebar */}
        <div>
          <h2 className="text-lg font-bold uppercase tracking-wider mb-4" style={{ fontFamily: 'Rajdhani, sans-serif' }}>Favorite Manufacturer</h2>
          {fleetStats.topManufacturers.length === 0 ? (
            <div className="glass-panel rounded-2xl p-6 text-center" data-testid="no-manufacturer">
              <Building2 className="w-10 h-10 mx-auto mb-3 text-gray-600" />
              <p className="text-sm text-gray-500">Add ships to see stats</p>
            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-5 space-y-4" data-testid="manufacturer-breakdown">
              {fleetStats.topManufacturers.map(([mfg, count]) => {
                const pct = Math.round((count / fleet.length) * 100);
                return (
                  <div key={mfg}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-bold text-white">{mfg.split(' ')[0]}</span>
                      <span className="text-xs text-cyan-400 font-semibold">{pct}%</span>
                    </div>
                    <p className="text-[10px] text-gray-600 mb-1">{count} ship{count !== 1 ? 's' : ''}</p>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #00D4FF, #D4AF37)' }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Saved Loadouts below manufacturer */}
          <h2 className="text-lg font-bold uppercase tracking-wider mb-4 mt-6" style={{ fontFamily: 'Rajdhani, sans-serif' }}>Saved Loadouts</h2>
          {loadouts.length === 0 ? (
            <div className="glass-panel rounded-2xl p-6 text-center" data-testid="no-loadouts">
              <Wrench className="w-8 h-8 mx-auto mb-2 text-gray-600" />
              <p className="text-sm text-gray-500 mb-2">No saved loadouts</p>
              <Link to="/loadout" className="text-xs text-cyan-500 hover:text-cyan-400">Create a Loadout</Link>
            </div>
          ) : (
            <div className="space-y-2" data-testid="saved-loadouts-list">
              {loadouts.map((lo, i) => {
                const ship = allVehicles.find(s => s.id === lo.ship_id);
                const configuredSlots = lo.components ? Object.keys(lo.components).filter(k => lo.components[k]).length : 0;
                return (
                  <Link key={lo.id || i} to="/loadout" className="glass-panel rounded-xl p-3 block hover:border-cyan-500/30 transition-all" data-testid={`loadout-card-${i}`}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg overflow-hidden bg-white/5 shrink-0 flex items-center justify-center">
                        {ship?.image ? (
                          <img src={ship.image} alt={lo.loadout_name} className="w-full h-full object-cover" onError={e => { e.target.style.display = 'none'; }} />
                        ) : (
                          <Wrench className="w-4 h-4 text-gray-600" />
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <h4 className="text-xs font-bold text-orange-400 truncate">{lo.loadout_name}</h4>
                        <p className="text-[10px] text-gray-500">{ship?.name || lo.ship_id}</p>
                        <p className="text-[9px] text-gray-600">{configuredSlots} slot{configuredSlots !== 1 ? 's' : ''}</p>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const FleetCard = ({ fs, index }) => {
  const hp = fs.details?.hardpoints || {};
  const wpns = hp.weapons || [];
  const msls = hp.missiles || [];
  const isCustom = fs.custom_name && fs.custom_name !== fs.ship_name;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(index * 0.04, 0.3) }}
      data-testid={`fleet-ship-${fs.ship_id}`}>
      <Link to={`/ships/${fs.ship_id}`} className="glass-panel rounded-xl p-3 flex items-center gap-4 hover:bg-white/5 transition-all group block">
        {/* Small image */}
        <div className="w-16 h-16 rounded-lg overflow-hidden bg-[#0a0a14] shrink-0">
          {fs.details?.image ? (
            <img src={fs.details.image} alt={fs.ship_name} className="w-full h-full object-cover" onError={e => { e.target.style.display = 'none'; }} />
          ) : (
            <div className="w-full h-full flex items-center justify-center"><SpaceshipIcon className="w-7 h-7 text-gray-700" /></div>
          )}
        </div>

        {/* Details */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <h3 className="text-sm font-bold text-white truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
              {isCustom ? fs.custom_name : fs.ship_name}
            </h3>
            {fs.details?.size && (
              <span className="text-[9px] px-1.5 py-0.5 rounded font-bold bg-white/5 text-gray-400 border border-white/10 shrink-0 uppercase">
                {fs.details.size}
              </span>
            )}
            {isCustom && (
              <span className="text-[9px] px-1.5 py-0.5 rounded font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
                CUSTOM
              </span>
            )}
          </div>
          {isCustom && <p className="text-[10px] text-gray-600 -mt-0.5">{fs.ship_name}</p>}
          <div className="flex items-center gap-2 mb-1">
            <p className="text-xs text-gray-500">{fs.manufacturer}</p>
            {fs.details?.role && <span className="text-[9px] text-gray-600">· {fs.details.role}</span>}
            {fs.details?.cargo > 0 && <span className="text-[9px] text-amber-500/70">· {fs.details.cargo} SCU</span>}
          </div>

          {/* Compact component + weapon line */}
          <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[10px]">
            {hp.shield && <CompBadge icon={Shield} label={`${hp.shield.count}xS${hp.shield.size}`} suffix="shld" color="#00D4FF" />}
            {hp.power_plant && <CompBadge icon={Zap} label={`${hp.power_plant.count}xS${hp.power_plant.size}`} suffix="pwr" color="#FFD700" />}
            {hp.cooler && <CompBadge icon={Snowflake} label={`${hp.cooler.count}xS${hp.cooler.size}`} suffix="cool" color="#00FF9D" />}
            {hp.quantum_drive && <CompBadge icon={Cpu} label={`${hp.quantum_drive.count}xS${hp.quantum_drive.size}`} suffix="qd" color="#FFAE00" />}
            {wpns.length > 0 && Object.entries(wpns.reduce((a, s) => { a[s] = (a[s] || 0) + 1; return a; }, {}))
              .sort(([a], [b]) => b - a)
              .map(([size, count]) => (
                <span key={`w${size}`} className="text-red-400 font-semibold">{count}xS{size}</span>
              ))}
            {msls.length > 0 && Object.entries(msls.reduce((a, s) => { a[s] = (a[s] || 0) + 1; return a; }, {}))
              .sort(([a], [b]) => b - a)
              .map(([size, count]) => (
                <span key={`m${size}`} className="text-orange-400 font-semibold">{count}xS{size}m</span>
              ))}
          </div>
        </div>

        {/* Arrow */}
        <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-cyan-400 transition-colors shrink-0" />
      </Link>
    </motion.div>
  );
};

const CompBadge = ({ icon: Icon, label, suffix, color }) => (
  <span className="flex items-center gap-0.5" style={{ color }}>
    <Icon className="w-3 h-3" /> {label} <span className="text-gray-600">{suffix}</span>
  </span>
);

const StatCard = ({ label, value, icon: Icon, color, testId }) => (
  <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}
    className="glass-panel rounded-xl p-4 text-center" data-testid={testId}>
    <Icon className="w-5 h-5 mx-auto mb-2" style={{ color }} />
    <div className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color }}>{value}</div>
    <div className="text-xs text-gray-500">{label}</div>
  </motion.div>
);

const QuickAction = ({ to, label, icon: Icon, color }) => (
  <Link to={to} className="glass-panel rounded-xl p-3 flex items-center gap-3 hover:bg-white/5 transition-all group" data-testid={`quick-action-${label.toLowerCase().replace(/ /g, '-')}`}>
    <Icon className="w-5 h-5 shrink-0" style={{ color }} />
    <span className="text-sm text-gray-400 group-hover:text-white transition-colors font-medium">{label}</span>
    <ArrowRight className="w-3.5 h-3.5 ml-auto text-gray-600 group-hover:text-gray-400 transition-colors" />
  </Link>
);

export default Dashboard;
