import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Navigation, MapPin, Clock, Ruler, Ship, ChevronRight, Zap, RotateCcw, ArrowLeftRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPE_COLORS = {
  star: '#FFD700',
  planet: '#00D4FF',
  moon: '#8B9DAF',
  station: '#00FF9D',
  gateway: '#FF6B35',
};

const SYSTEM_COLORS = {
  stanton: '#00D4FF',
  pyro: '#FF4500',
  nyx: '#A855F7',
};

const TYPE_RADIUS = {
  star: 8,
  planet: 6,
  moon: 3,
  station: 3,
  gateway: 5,
};

const RoutePlanner = () => {
  const { API: authAPI } = useAuth();
  const [locations, setLocations] = useState([]);
  const [systems, setSystems] = useState({});
  const [qdSpeeds, setQdSpeeds] = useState({});
  const [ships, setShips] = useState([]);
  const [selectedShip, setSelectedShip] = useState(null);
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [qdSize, setQdSize] = useState(1);
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const canvasRef = useRef(null);
  const [mapOffset, setMapOffset] = useState({ x: 0, y: 0 });
  const [mapZoom, setMapZoom] = useState(1);
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [hoveredLoc, setHoveredLoc] = useState(null);
  const [filterSystem, setFilterSystem] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [locRes, shipsRes] = await Promise.all([
          axios.get(`${API}/routes/locations`),
          axios.get(`${authAPI}/ships`),
        ]);
        setLocations(locRes.data.data || []);
        setSystems(locRes.data.systems || {});
        setQdSpeeds(locRes.data.qd_speeds || {});
        const allShips = (shipsRes.data.data || []).filter(s =>
          s.hardpoints?.quantum_drive && !s.is_ground_vehicle
        );
        setShips(allShips);
      } catch {
        toast.error('Failed to load route data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [authAPI]);

  const filteredLocations = useMemo(() => {
    if (filterSystem === 'all') return locations.filter(l => l.type !== 'star');
    return locations.filter(l => l.system === filterSystem && l.type !== 'star');
  }, [locations, filterSystem]);

  const calculateRoute = useCallback(async () => {
    if (!origin || !destination) {
      toast.error('Select both origin and destination');
      return;
    }
    setCalculating(true);
    try {
      const res = await axios.get(`${API}/routes/calculate`, {
        params: { origin, destination, qd_size: qdSize },
      });
      setRoute(res.data.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Route calculation failed');
    } finally {
      setCalculating(false);
    }
  }, [origin, destination, qdSize]);

  const swapOriginDest = () => {
    setOrigin(destination);
    setDestination(origin);
    setRoute(null);
  };

  const onShipSelect = (shipId) => {
    const ship = ships.find(s => s.id === shipId);
    setSelectedShip(ship);
    if (ship?.hardpoints?.quantum_drive) {
      setQdSize(ship.hardpoints.quantum_drive.size || 1);
    }
    setRoute(null);
  };

  // --- Canvas Map ---
  const drawMap = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || locations.length === 0) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Background
    ctx.fillStyle = '#050508';
    ctx.fillRect(0, 0, w, h);

    // Draw grid
    ctx.strokeStyle = 'rgba(255,255,255,0.03)';
    ctx.lineWidth = 1;
    const gridSize = 50 * mapZoom;
    const offX = (w / 2 + mapOffset.x) % gridSize;
    const offY = (h / 2 + mapOffset.y) % gridSize;
    for (let x = offX; x < w; x += gridSize) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = offY; y < h; y += gridSize) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    const toScreen = (mx, my) => ({
      x: w / 2 + (mx * mapZoom) + mapOffset.x,
      y: h / 2 + (my * mapZoom) + mapOffset.y,
    });

    // Draw system orbit rings
    Object.entries(systems).forEach(([sysId, sys]) => {
      const center = toScreen(sys.star.x, sys.star.y);
      ctx.strokeStyle = `${sys.color}10`;
      ctx.lineWidth = 1;
      [40, 80, 120, 160].forEach(r => {
        ctx.beginPath();
        ctx.arc(center.x, center.y, r * mapZoom * 0.7, 0, Math.PI * 2);
        ctx.stroke();
      });
      // System label
      ctx.fillStyle = `${sys.color}60`;
      ctx.font = `bold ${Math.max(10, 14 * mapZoom)}px Rajdhani, sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(sys.name.toUpperCase(), center.x, center.y - 10 * mapZoom);
    });

    // Draw jump connections
    const jumpPairs = [
      ['stanton-pyro-gw', 'pyro-stanton-gw'],
      ['stanton-nyx-gw', 'nyx-stanton-gw'],
      ['pyro-nyx-gw', 'nyx-pyro-gw'],
    ];
    jumpPairs.forEach(([a, b]) => {
      const la = locations.find(l => l.id === a);
      const lb = locations.find(l => l.id === b);
      if (la && lb) {
        const sa = toScreen(la.map_x, la.map_y);
        const sb = toScreen(lb.map_x, lb.map_y);
        ctx.strokeStyle = '#FF6B3540';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 4]);
        ctx.beginPath(); ctx.moveTo(sa.x, sa.y); ctx.lineTo(sb.x, sb.y); ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // Draw route if exists
    if (route?.waypoints) {
      route.waypoints.forEach(wp => {
        const fromLoc = locations.find(l => l.id === wp.from_id);
        const toLoc = locations.find(l => l.id === wp.to_id);
        if (fromLoc && toLoc) {
          const sf = toScreen(fromLoc.map_x, fromLoc.map_y);
          const st = toScreen(toLoc.map_x, toLoc.map_y);
          const isJump = wp.type === 'jump';
          ctx.strokeStyle = isJump ? '#FF6B35' : '#00D4FF';
          ctx.lineWidth = isJump ? 3 : 2.5;
          ctx.setLineDash(isJump ? [8, 4] : []);
          ctx.shadowColor = isJump ? '#FF6B35' : '#00D4FF';
          ctx.shadowBlur = 8;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
          ctx.shadowBlur = 0;
          ctx.setLineDash([]);
          // Arrow
          const angle = Math.atan2(st.y - sf.y, st.x - sf.x);
          const mx = (sf.x + st.x) / 2;
          const my = (sf.y + st.y) / 2;
          ctx.fillStyle = isJump ? '#FF6B35' : '#00D4FF';
          ctx.beginPath();
          ctx.moveTo(mx + 6 * Math.cos(angle), my + 6 * Math.sin(angle));
          ctx.lineTo(mx - 6 * Math.cos(angle) - 4 * Math.sin(angle), my - 6 * Math.sin(angle) + 4 * Math.cos(angle));
          ctx.lineTo(mx - 6 * Math.cos(angle) + 4 * Math.sin(angle), my - 6 * Math.sin(angle) - 4 * Math.cos(angle));
          ctx.fill();
        }
      });
    }

    // Draw locations
    locations.forEach(loc => {
      const s = toScreen(loc.map_x, loc.map_y);
      if (s.x < -20 || s.x > w + 20 || s.y < -20 || s.y > h + 20) return;

      const r = (TYPE_RADIUS[loc.type] || 3) * mapZoom;
      const color = TYPE_COLORS[loc.type] || '#888';
      const isOrigin = loc.id === origin;
      const isDest = loc.id === destination;
      const isHovered = hoveredLoc === loc.id;

      // Glow for selected
      if (isOrigin || isDest || isHovered) {
        ctx.shadowColor = isOrigin ? '#00FF9D' : isDest ? '#FF0055' : color;
        ctx.shadowBlur = 12;
      }

      ctx.fillStyle = color;
      if (loc.type === 'gateway') {
        // Diamond shape
        ctx.beginPath();
        ctx.moveTo(s.x, s.y - r); ctx.lineTo(s.x + r, s.y);
        ctx.lineTo(s.x, s.y + r); ctx.lineTo(s.x - r, s.y);
        ctx.closePath(); ctx.fill();
      } else if (loc.type === 'star') {
        // Star glow
        const gradient = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, r * 2);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient;
        ctx.beginPath(); ctx.arc(s.x, s.y, r * 2, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = color;
        ctx.beginPath(); ctx.arc(s.x, s.y, r * 0.6, 0, Math.PI * 2); ctx.fill();
      } else {
        ctx.beginPath(); ctx.arc(s.x, s.y, r, 0, Math.PI * 2); ctx.fill();
      }

      // Selection ring
      if (isOrigin || isDest) {
        ctx.strokeStyle = isOrigin ? '#00FF9D' : '#FF0055';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(s.x, s.y, r + 4, 0, Math.PI * 2); ctx.stroke();
      }

      ctx.shadowBlur = 0;

      // Label
      if (mapZoom > 0.6 || loc.type === 'planet' || loc.type === 'star' || isOrigin || isDest || isHovered) {
        ctx.fillStyle = isOrigin ? '#00FF9D' : isDest ? '#FF0055' : 'rgba(255,255,255,0.7)';
        ctx.font = `${loc.type === 'planet' ? 'bold ' : ''}${Math.max(8, (loc.type === 'moon' || loc.type === 'station' ? 9 : 11) * mapZoom)}px Rajdhani, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(loc.name, s.x, s.y + r + 12 * mapZoom);
      }
    });
  }, [locations, systems, origin, destination, route, mapOffset, mapZoom, hoveredLoc]);

  useEffect(() => { drawMap(); }, [drawMap]);

  // Resize canvas
  useEffect(() => {
    const resize = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const parent = canvas.parentElement;
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
      drawMap();
    };
    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, [drawMap]);

  // Mouse handlers for pan/zoom
  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setMapZoom(z => Math.max(0.3, Math.min(3, z + delta)));
  };

  const handleMouseDown = (e) => {
    if (e.button === 0) {
      setDragging(true);
      setDragStart({ x: e.clientX - mapOffset.x, y: e.clientY - mapOffset.y });
    }
  };

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    if (dragging) {
      setMapOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
      return;
    }
    // Hover detection
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const w = canvas.width;
    const h = canvas.height;
    let found = null;
    locations.forEach(loc => {
      const sx = w / 2 + (loc.map_x * mapZoom) + mapOffset.x;
      const sy = h / 2 + (loc.map_y * mapZoom) + mapOffset.y;
      const dist = Math.sqrt((mx - sx) ** 2 + (my - sy) ** 2);
      if (dist < 15) found = loc.id;
    });
    setHoveredLoc(found);
    canvas.style.cursor = found ? 'pointer' : dragging ? 'grabbing' : 'grab';
  };

  const handleMouseUp = () => setDragging(false);

  const handleCanvasClick = (e) => {
    if (!hoveredLoc) return;
    if (!origin) setOrigin(hoveredLoc);
    else if (!destination) setDestination(hoveredLoc);
    else { setOrigin(hoveredLoc); setDestination(''); setRoute(null); }
  };

  const resetMap = () => {
    setMapOffset({ x: 0, y: 0 });
    setMapZoom(1);
  };

  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    if (m < 60) return `${m}m ${s}s`;
    const h = Math.floor(m / 60);
    return `${h}h ${m % 60}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-80px)] flex gap-4" data-testid="route-planner-page">
      {/* Left Panel */}
      <div className="w-80 shrink-0 space-y-4 overflow-y-auto pr-2">
        <div>
          <h1 className="text-2xl font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Route Planner
          </h1>
          <p className="text-xs text-gray-500 mt-1">Plan quantum travel across Stanton, Pyro & Nyx</p>
        </div>

        {/* Ship Selection */}
        <div className="glass-panel rounded-xl p-4" data-testid="ship-selector">
          <label className="text-xs font-semibold text-gray-400 uppercase block mb-2">Ship</label>
          <select
            value={selectedShip?.id || ''}
            onChange={e => onShipSelect(e.target.value)}
            data-testid="ship-select"
            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500"
          >
            <option value="">Select a ship...</option>
            {ships.map(s => (
              <option key={s.id} value={s.id}>
                {s.name} (QD S{s.hardpoints?.quantum_drive?.size || '?'})
              </option>
            ))}
          </select>
          {selectedShip && (
            <div className="mt-2 text-xs text-gray-400">
              QD Size: <span className="text-cyan-400 font-semibold">S{qdSize}</span>
              {' | '}Speed: <span className="text-cyan-400 font-semibold">{(qdSpeeds[qdSize] || 165000).toLocaleString()} km/s</span>
            </div>
          )}
        </div>

        {/* Origin / Destination */}
        <div className="glass-panel rounded-xl p-4 space-y-3" data-testid="route-selectors">
          <div>
            <label className="text-xs font-semibold text-green-400 uppercase block mb-1">Origin</label>
            <select
              value={origin}
              onChange={e => { setOrigin(e.target.value); setRoute(null); }}
              data-testid="origin-select"
              className="w-full px-3 py-2 bg-white/5 border border-green-500/30 rounded-lg text-white text-sm focus:outline-none focus:border-green-500"
            >
              <option value="">Select origin...</option>
              {Object.entries(systems).map(([sysId, sys]) => (
                <optgroup key={sysId} label={sys.name}>
                  {locations.filter(l => l.system === sysId && l.type !== 'star').map(l => (
                    <option key={l.id} value={l.id}>{l.name}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          <button onClick={swapOriginDest} data-testid="swap-btn"
            className="w-full flex items-center justify-center gap-2 py-1.5 rounded-lg bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-all text-xs">
            <ArrowLeftRight className="w-3 h-3" /> Swap
          </button>

          <div>
            <label className="text-xs font-semibold text-red-400 uppercase block mb-1">Destination</label>
            <select
              value={destination}
              onChange={e => { setDestination(e.target.value); setRoute(null); }}
              data-testid="destination-select"
              className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded-lg text-white text-sm focus:outline-none focus:border-red-500"
            >
              <option value="">Select destination...</option>
              {Object.entries(systems).map(([sysId, sys]) => (
                <optgroup key={sysId} label={sys.name}>
                  {locations.filter(l => l.system === sysId && l.type !== 'star').map(l => (
                    <option key={l.id} value={l.id}>{l.name}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          {/* QD Size Override */}
          {!selectedShip && (
            <div>
              <label className="text-xs font-semibold text-gray-400 uppercase block mb-1">QD Size</label>
              <div className="flex gap-2">
                {[1, 2, 3].map(s => (
                  <button key={s} onClick={() => { setQdSize(s); setRoute(null); }}
                    data-testid={`qd-size-${s}`}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${qdSize === s ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
                    S{s}
                  </button>
                ))}
              </div>
            </div>
          )}

          <button onClick={calculateRoute} disabled={!origin || !destination || calculating}
            data-testid="calculate-route-btn"
            className="w-full py-2.5 rounded-xl font-bold text-sm text-black disabled:opacity-40 transition-all"
            style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}>
            {calculating ? 'Calculating...' : 'Calculate Route'}
          </button>
        </div>

        {/* Route Results */}
        {route && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className="glass-panel rounded-xl p-4 space-y-4" data-testid="route-results">
            <h3 className="text-sm font-bold uppercase text-gray-400">Route Details</h3>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/5 rounded-lg p-3 text-center">
                <Ruler className="w-4 h-4 mx-auto mb-1 text-cyan-400" />
                <div className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  {route.total_distance_mkm.toLocaleString()}
                </div>
                <div className="text-[10px] text-gray-500">Mkm Distance</div>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center">
                <Clock className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
                <div className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                  {formatTime(route.travel_time_seconds)}
                </div>
                <div className="text-[10px] text-gray-500">Travel Time</div>
              </div>
            </div>

            <div className="text-xs text-gray-500 flex items-center gap-2">
              <Zap className="w-3 h-3 text-cyan-400" />
              QD S{route.qd_size} at {route.qd_speed_kms.toLocaleString()} km/s
              {route.cross_system && <span className="px-1.5 py-0.5 bg-orange-500/20 text-orange-400 rounded text-[10px]">Cross-System</span>}
            </div>

            {/* Waypoints */}
            <div className="space-y-1">
              <h4 className="text-xs font-semibold text-gray-400 uppercase">Waypoints</h4>
              {route.waypoints.map((wp, i) => (
                <div key={i} className={`flex items-center gap-2 p-2 rounded-lg text-xs ${wp.type === 'jump' ? 'bg-orange-500/10 border border-orange-500/20' : 'bg-white/[0.03]'}`}
                  data-testid={`waypoint-${i}`}>
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${wp.type === 'jump' ? 'bg-orange-500/30 text-orange-400' : 'bg-cyan-500/20 text-cyan-400'}`}>
                    {i + 1}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1 text-gray-300">
                      <span className="truncate">{wp.from}</span>
                      <ChevronRight className="w-3 h-3 text-gray-600 shrink-0" />
                      <span className="truncate">{wp.to}</span>
                    </div>
                    <div className="text-gray-600">
                      {wp.distance_mkm} Mkm
                      {wp.type === 'jump' && ' (Jump Tunnel)'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Legend */}
        <div className="glass-panel rounded-xl p-4" data-testid="map-legend">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Legend</h4>
          <div className="grid grid-cols-2 gap-1.5 text-[11px]">
            {Object.entries(TYPE_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: color }} />
                <span className="text-gray-400 capitalize">{type}</span>
              </div>
            ))}
          </div>
          <div className="mt-2 text-[10px] text-gray-600">Click map locations to set origin/destination. Scroll to zoom, drag to pan.</div>
        </div>
      </div>

      {/* Map Canvas */}
      <div className="flex-1 glass-panel rounded-xl overflow-hidden relative" data-testid="star-map">
        <canvas
          ref={canvasRef}
          onWheel={handleWheel}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onClick={handleCanvasClick}
          className="w-full h-full"
        />
        {/* Map Controls */}
        <div className="absolute top-3 right-3 flex items-center gap-2">
          <div className="flex gap-1 bg-black/60 backdrop-blur rounded-lg p-1">
            {['all', 'stanton', 'pyro', 'nyx'].map(sys => (
              <button key={sys} onClick={() => setFilterSystem(sys)}
                data-testid={`filter-${sys}`}
                className={`px-2 py-1 rounded text-[10px] font-bold uppercase transition-all ${filterSystem === sys ? 'bg-white/20 text-white' : 'text-gray-500 hover:text-white'}`}
                style={filterSystem === sys && sys !== 'all' ? { color: SYSTEM_COLORS[sys] } : {}}>
                {sys}
              </button>
            ))}
          </div>
          <button onClick={resetMap} data-testid="reset-map"
            className="p-2 bg-black/60 backdrop-blur rounded-lg text-gray-400 hover:text-white transition-colors">
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
        {/* Hover tooltip */}
        {hoveredLoc && (
          <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur rounded-lg px-3 py-2 text-xs pointer-events-none">
            <div className="font-bold text-white">{locations.find(l => l.id === hoveredLoc)?.name}</div>
            <div className="text-gray-400 capitalize">{locations.find(l => l.id === hoveredLoc)?.type} - {locations.find(l => l.id === hoveredLoc)?.system}</div>
          </div>
        )}
        {/* Zoom indicator */}
        <div className="absolute bottom-3 right-3 text-[10px] text-gray-600 bg-black/40 px-2 py-1 rounded">
          {Math.round(mapZoom * 100)}%
        </div>
      </div>
    </div>
  );
};

export default RoutePlanner;
