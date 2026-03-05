import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Ship, Package, Crosshair, TrendingUp, Anchor, DollarSign, Building2, Users, Globe, Wrench, ArrowRight, Shield, Zap, Cpu, Snowflake } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const { API } = useAuth();
  const [ships, setShips] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [components, setComponents] = useState([]);
  const [weapons, setWeapons] = useState([]);
  const [fleet, setFleet] = useState([]);
  const [loadouts, setLoadouts] = useState([]);
  const [communityCount, setCommunityCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [shipsRes, vehiclesRes, componentsRes, weaponsRes, fleetRes, loadoutsRes, communityRes] = await Promise.all([
          axios.get(`${API}/ships`),
          axios.get(`${API}/vehicles`),
          axios.get(`${API}/components`),
          axios.get(`${API}/weapons`),
          axios.get(`${API}/fleet/my`),
          axios.get(`${API}/loadouts/my/all`),
          axios.get(`${API}/community/loadouts?limit=1`),
        ]);
        setShips(shipsRes.data.data || []);
        setVehicles(vehiclesRes.data.data || []);
        setComponents(componentsRes.data.data || []);
        setWeapons(weaponsRes.data.data || []);
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

  const fleetShips = useMemo(() => {
    const shipMap = {};
    ships.forEach(s => { shipMap[s.id] = s; });
    return fleet.map(f => ({ ...f, details: shipMap[f.ship_id] }));
  }, [fleet, ships]);

  const fleetStats = useMemo(() => {
    const mfgCount = {};
    let totalValueAuec = 0;
    let totalValueUsd = 0;
    let sizeBreakdown = {};

    fleetShips.forEach(f => {
      const mfg = f.manufacturer || 'Unknown';
      mfgCount[mfg] = (mfgCount[mfg] || 0) + 1;
      if (f.details) {
        totalValueAuec += f.details.price_auec || 0;
        totalValueUsd += f.details.price_usd || f.details.msrp || 0;
        const sz = f.details.size || 'Unknown';
        sizeBreakdown[sz] = (sizeBreakdown[sz] || 0) + 1;
      }
    });

    const sorted = Object.entries(mfgCount).sort((a, b) => b[1] - a[1]);
    const favoriteVendor = sorted.length > 0 ? sorted[0] : ['None', 0];
    const topManufacturers = sorted.slice(0, 5);

    return { totalValueAuec, totalValueUsd, favoriteVendor, topManufacturers, sizeBreakdown };
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

  const dbStats = [
    { label: 'Ships', value: ships.length, icon: Ship, color: '#00D4FF' },
    { label: 'Ground Vehicles', value: vehicles.length, icon: Package, color: '#D4AF37' },
    { label: 'Components', value: components.length, icon: TrendingUp, color: '#00FF9D' },
    { label: 'Weapons', value: weapons.length, icon: Crosshair, color: '#FFAE00' },
  ];

  return (
    <div className="space-y-8" data-testid="dashboard-page">
      {/* Hero */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center py-8">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-3 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Fleet Command Center
        </h1>
        <p className="text-base text-gray-400 max-w-2xl mx-auto">Precision management for the discerning star citizen</p>
      </motion.div>

      {/* Fleet Overview - Personal Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard label="My Fleet" value={fleet.length} icon={Anchor} color="#00D4FF" testId="stat-my-fleet" />
        <StatCard label="Fleet Value" value={formatAuec(fleetStats.totalValueAuec)} icon={DollarSign} color="#FFD700" sub="aUEC" testId="stat-fleet-value" />
        <StatCard label="Pledge Value" value={`$${fleetStats.totalValueUsd}`} icon={DollarSign} color="#00FF9D" sub="USD" testId="stat-pledge-value" />
        <StatCard label="My Loadouts" value={loadouts.length} icon={Wrench} color="#FF6B35" testId="stat-my-loadouts" />
        <StatCard label="Community" value={communityCount} icon={Globe} color="#A855F7" sub="Shared" testId="stat-community" />
        <StatCard label="Favorite Vendor" value={fleetStats.favoriteVendor[0].split(' ')[0]} icon={Building2} color="#FF0055" sub={`${fleetStats.favoriteVendor[1]} ships`} testId="stat-fav-vendor" />
      </div>

      {/* Database Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {dbStats.map((stat, i) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
            className="glass-panel rounded-xl p-4 flex items-center gap-4" data-testid={`stat-db-${stat.label.toLowerCase().replace(' ', '-')}`}>
            <stat.icon className="w-6 h-6 shrink-0" style={{ color: stat.color }} />
            <div>
              <div className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color: stat.color }}>{stat.value}</div>
              <div className="text-xs text-gray-500">{stat.label} in Database</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Two Column: Fleet Ships + Manufacturer Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* My Fleet Ships */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif' }}>My Fleet</h2>
            <Link to="/fleet" className="text-sm text-cyan-500 hover:text-cyan-400 flex items-center gap-1" data-testid="view-fleet-link">
              Manage Fleet <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          {fleetShips.length === 0 ? (
            <div className="glass-panel rounded-2xl p-8 text-center" data-testid="empty-fleet-card">
              <Ship className="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <h3 className="text-base font-bold mb-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>No Ships in Fleet</h3>
              <p className="text-sm text-gray-500 mb-4">Add ships to see them here</p>
              <Link to="/fleet" className="px-4 py-2 rounded-lg text-sm font-semibold text-black inline-block"
                style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}>
                Go to Fleet
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {fleetShips.map((fs, i) => {
                const hp = fs.details?.hardpoints || {};
                const wpns = hp.weapons || [];
                return (
                  <motion.div key={fs.id} initial={{ opacity: 0, x: -15 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                    data-testid={`fleet-ship-${fs.ship_id}`}>
                    <Link to={`/ships/${fs.ship_id}`} className="glass-panel rounded-xl p-4 group hover:border-cyan-500/30 transition-all block">
                      <div className="flex items-start gap-4">
                        <div className="w-24 h-16 rounded-lg overflow-hidden bg-white/5 shrink-0">
                          {fs.details?.image ? (
                            <img src={fs.details.image} alt={fs.ship_name} className="w-full h-full object-cover" onError={e => { e.target.style.display = 'none'; }} />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center"><Ship className="w-6 h-6 text-gray-600" /></div>
                          )}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="font-bold text-white text-sm group-hover:text-cyan-400 transition-colors truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                              {fs.ship_name}
                            </h4>
                            <div className="flex items-center gap-2 shrink-0 ml-2">
                              {fs.details?.size && <span className="text-[10px] px-1.5 py-0.5 rounded border border-white/10 text-gray-400">{fs.details.size}</span>}
                              {fs.details?.price_auec > 0 && <span className="text-xs text-yellow-400 font-semibold hidden sm:block">{formatAuec(fs.details.price_auec)}</span>}
                            </div>
                          </div>
                          <div className="text-xs text-gray-500 mb-2">{fs.manufacturer}</div>

                          {/* Components row */}
                          <div className="flex flex-wrap gap-x-3 gap-y-1 text-[11px]">
                            {hp.shield && (
                              <span className="flex items-center gap-1 text-cyan-400">
                                <Shield className="w-3 h-3" /> S{hp.shield.size} x{hp.shield.count}
                              </span>
                            )}
                            {hp.power_plant && (
                              <span className="flex items-center gap-1 text-yellow-400">
                                <Zap className="w-3 h-3" /> S{hp.power_plant.size} x{hp.power_plant.count}
                              </span>
                            )}
                            {hp.cooler && (
                              <span className="flex items-center gap-1 text-green-400">
                                <Snowflake className="w-3 h-3" /> S{hp.cooler.size} x{hp.cooler.count}
                              </span>
                            )}
                            {hp.quantum_drive && (
                              <span className="flex items-center gap-1 text-amber-400">
                                <Cpu className="w-3 h-3" /> S{hp.quantum_drive.size} x{hp.quantum_drive.count}
                              </span>
                            )}
                          </div>

                          {/* Weapons row */}
                          {wpns.length > 0 && (
                            <div className="flex items-center gap-1.5 mt-1.5 text-[11px] text-red-400">
                              <Crosshair className="w-3 h-3 shrink-0" />
                              {Object.entries(wpns.reduce((acc, s) => { acc[s] = (acc[s] || 0) + 1; return acc; }, {}))
                                .sort(([a], [b]) => b - a)
                                .map(([size, count]) => (
                                  <span key={size} className="px-1.5 py-0.5 bg-red-500/10 rounded border border-red-500/20">{count}x S{size}</span>
                                ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>

        {/* Sidebar: Manufacturer Breakdown + Quick Actions */}
        <div className="space-y-6">
          {/* Manufacturer Breakdown */}
          {fleetStats.topManufacturers.length > 0 && (
            <div className="glass-panel rounded-2xl p-5" data-testid="manufacturer-breakdown">
              <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">Top Manufacturers</h3>
              <div className="space-y-3">
                {fleetStats.topManufacturers.map(([mfg, count]) => {
                  const pct = Math.round((count / fleet.length) * 100);
                  return (
                    <div key={mfg}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-white font-medium truncate">{mfg}</span>
                        <span className="text-xs text-cyan-400 shrink-0 ml-2">{count} ({pct}%)</span>
                      </div>
                      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #00D4FF, #00A8CC)' }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Size Breakdown */}
          {Object.keys(fleetStats.sizeBreakdown).length > 0 && (
            <div className="glass-panel rounded-2xl p-5" data-testid="size-breakdown">
              <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">Fleet by Size</h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(fleetStats.sizeBreakdown).map(([size, count]) => (
                  <div key={size} className="bg-white/[0.03] rounded-lg p-3 text-center">
                    <div className="text-xl font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{count}</div>
                    <div className="text-xs text-gray-500">{size}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="glass-panel rounded-2xl p-5" data-testid="quick-actions">
            <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <QuickAction to="/ships" label="Browse Ships" icon={Ship} color="#00D4FF" />
              <QuickAction to="/compare" label="Compare Ships" icon={Users} color="#FFAE00" />
              <QuickAction to="/loadout" label="Build Loadout" icon={Wrench} color="#FF6B35" />
              <QuickAction to="/community" label="Community Loadouts" icon={Globe} color="#A855F7" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, icon: Icon, color, sub, testId }) => (
  <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}
    className="glass-panel rounded-xl p-4 text-center" data-testid={testId}>
    <Icon className="w-5 h-5 mx-auto mb-2" style={{ color }} />
    <div className="text-xl font-bold truncate" style={{ fontFamily: 'Rajdhani, sans-serif', color }}>{value}</div>
    <div className="text-xs text-gray-500">{label}</div>
    {sub && <div className="text-[10px] text-gray-600 mt-0.5">{sub}</div>}
  </motion.div>
);

const QuickAction = ({ to, label, icon: Icon, color }) => (
  <Link to={to} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/5 transition-colors group" data-testid={`quick-action-${label.toLowerCase().replace(/ /g, '-')}`}>
    <Icon className="w-4 h-4 shrink-0" style={{ color }} />
    <span className="text-sm text-gray-400 group-hover:text-white transition-colors">{label}</span>
    <ArrowRight className="w-3 h-3 ml-auto text-gray-600 group-hover:text-gray-400 transition-colors" />
  </Link>
);

function formatAuec(n) {
  if (!n || n === 0) return '0';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return n.toLocaleString();
}

export default Dashboard;
