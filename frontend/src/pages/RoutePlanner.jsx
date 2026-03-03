import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Navigation, Clock, Ruler, Ship, ChevronRight, Zap, RotateCcw, ArrowLeftRight, Target, Gauge, Plus, X, AlertTriangle, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPE_COLORS = { star: '#FFD700', planet: '#00D4FF', moon: '#8B9DAF', station: '#00FF9D', gateway: '#FF6B35' };
const SYSTEM_COLORS = { stanton: '#00D4FF', pyro: '#FF4500', nyx: '#A855F7' };
const TYPE_RADIUS = { star: 8, planet: 6, moon: 3, station: 3, gateway: 5 };
const TABS = [
  { id: 'route', label: 'Route', icon: Navigation },
  { id: 'interdiction', label: 'Interdiction', icon: Target },
  { id: 'chase', label: 'Chase', icon: Gauge },
];

const RoutePlanner = () => {
  const { API: authAPI } = useAuth();
  const [locations, setLocations] = useState([]);
  const [systems, setSystems] = useState({});
  const [qdSpeeds, setQdSpeeds] = useState({});
  const [ships, setShips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('route');

  // Route state
  const [selectedShip, setSelectedShip] = useState(null);
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [qdSize, setQdSize] = useState(1);
  const [route, setRoute] = useState(null);
  const [calculating, setCalculating] = useState(false);

  // Interdiction state
  const [interdictOrigins, setInterdictOrigins] = useState([]);
  const [interdictDest, setInterdictDest] = useState('');
  const [snareRange, setSnareRange] = useState(7.5);
  const [interdictResult, setInterdictResult] = useState(null);
  const [interdicting, setInterdicting] = useState(false);

  // Chase state
  const [chaseYourQd, setChaseYourQd] = useState(1);
  const [chaseTargetQd, setChaseTargetQd] = useState(1);
  const [chaseDist, setChaseDist] = useState(10);
  const [chasePrep, setChasePrep] = useState(30);
  const [chaseResult, setChaseResult] = useState(null);

  // Map state
  const canvasRef = useRef(null);
  const [mapOffset, setMapOffset] = useState({ x: 0, y: 0 });
  const [mapZoom, setMapZoom] = useState(1);
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [hoveredLoc, setHoveredLoc] = useState(null);

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
        setShips((shipsRes.data.data || []).filter(s => s.hardpoints?.quantum_drive && !s.is_ground_vehicle));
      } catch { toast.error('Failed to load route data'); }
      finally { setLoading(false); }
    };
    fetchData();
  }, [authAPI]);

  // --- Actions ---
  const calcRoute = useCallback(async () => {
    if (!origin || !destination) { toast.error('Select both origin and destination'); return; }
    setCalculating(true);
    try {
      const res = await axios.get(`${API}/routes/calculate`, { params: { origin, destination, qd_size: qdSize } });
      setRoute(res.data.data);
    } catch (err) { toast.error(err.response?.data?.detail || 'Route calculation failed'); }
    finally { setCalculating(false); }
  }, [origin, destination, qdSize]);

  const calcInterdiction = useCallback(async () => {
    if (interdictOrigins.length === 0 || !interdictDest) { toast.error('Add origins and select a destination'); return; }
    setInterdicting(true);
    try {
      const res = await axios.post(`${API}/routes/interdiction`, {
        origins: interdictOrigins, destination: interdictDest, snare_range_mkm: snareRange,
      });
      setInterdictResult(res.data.data);
    } catch (err) { toast.error(err.response?.data?.detail || 'Interdiction calculation failed'); }
    finally { setInterdicting(false); }
  }, [interdictOrigins, interdictDest, snareRange]);

  const calcChase = useCallback(async () => {
    try {
      const res = await axios.post(`${API}/routes/chase`, {
        your_qd_size: chaseYourQd, target_qd_size: chaseTargetQd,
        distance_mkm: chaseDist, prep_time_seconds: chasePrep,
      });
      setChaseResult(res.data.data);
    } catch { toast.error('Chase calculation failed'); }
  }, [chaseYourQd, chaseTargetQd, chaseDist, chasePrep]);

  const addInterdictOrigin = (id) => {
    if (id && !interdictOrigins.includes(id)) {
      setInterdictOrigins(prev => [...prev, id]);
      setInterdictResult(null);
    }
  };
  const removeInterdictOrigin = (id) => {
    setInterdictOrigins(prev => prev.filter(o => o !== id));
    setInterdictResult(null);
  };

  const onShipSelect = (shipId) => {
    const ship = ships.find(s => s.id === shipId);
    setSelectedShip(ship);
    if (ship?.hardpoints?.quantum_drive) setQdSize(ship.hardpoints.quantum_drive.size || 1);
    setRoute(null);
  };

  const swapOriginDest = () => { setOrigin(destination); setDestination(origin); setRoute(null); };
  const locName = (id) => locations.find(l => l.id === id)?.name || id;

  // --- Canvas Map ---
  const drawMap = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || locations.length === 0) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#050508';
    ctx.fillRect(0, 0, w, h);

    // Grid
    ctx.strokeStyle = 'rgba(255,255,255,0.03)';
    ctx.lineWidth = 1;
    const gridSize = 50 * mapZoom;
    const offX = (w / 2 + mapOffset.x) % gridSize, offY = (h / 2 + mapOffset.y) % gridSize;
    for (let x = offX; x < w; x += gridSize) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
    for (let y = offY; y < h; y += gridSize) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }

    const toScreen = (mx, my) => ({ x: w / 2 + (mx * mapZoom) + mapOffset.x, y: h / 2 + (my * mapZoom) + mapOffset.y });

    // System orbit rings
    Object.entries(systems).forEach(([, sys]) => {
      const center = toScreen(sys.star.x, sys.star.y);
      ctx.strokeStyle = `${sys.color}10`;
      ctx.lineWidth = 1;
      [40, 80, 120, 160].forEach(r => { ctx.beginPath(); ctx.arc(center.x, center.y, r * mapZoom * 0.7, 0, Math.PI * 2); ctx.stroke(); });
      ctx.fillStyle = `${sys.color}60`;
      ctx.font = `bold ${Math.max(10, 14 * mapZoom)}px Rajdhani, sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(sys.name.toUpperCase(), center.x, center.y - 10 * mapZoom);
    });

    // Jump connections
    [['stanton-pyro-gw', 'pyro-stanton-gw'], ['stanton-nyx-gw', 'nyx-stanton-gw'], ['pyro-nyx-gw', 'nyx-pyro-gw']].forEach(([a, b]) => {
      const la = locations.find(l => l.id === a), lb = locations.find(l => l.id === b);
      if (la && lb) {
        const sa = toScreen(la.map_x, la.map_y), sb = toScreen(lb.map_x, lb.map_y);
        ctx.strokeStyle = '#FF6B3540'; ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
        ctx.beginPath(); ctx.moveTo(sa.x, sa.y); ctx.lineTo(sb.x, sb.y); ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // Draw interdiction route lines + snare circle
    if (activeTab === 'interdiction' && interdictResult) {
      // Route lines from origins to destination
      (interdictResult.route_lines || []).forEach(rl => {
        const sf = toScreen(rl.sx, rl.sy), st = toScreen(rl.ex, rl.ey);
        ctx.strokeStyle = '#FF005580'; ctx.lineWidth = 1.5; ctx.setLineDash([4, 3]);
        ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
        ctx.setLineDash([]);
      });
      // Snare circle
      const sp = interdictResult.snare_position;
      if (sp) {
        const ss = toScreen(sp.x, sp.y);
        const sr = (interdictResult.snare_range_map || 25) * mapZoom;
        // Glow
        ctx.fillStyle = interdictResult.coverage_pct === 100 ? 'rgba(255,0,85,0.08)' : 'rgba(255,165,0,0.08)';
        ctx.beginPath(); ctx.arc(ss.x, ss.y, sr, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = interdictResult.coverage_pct === 100 ? '#FF0055' : '#FFA500';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(ss.x, ss.y, sr, 0, Math.PI * 2); ctx.stroke();
        // Center marker
        ctx.fillStyle = '#FF0055'; ctx.shadowColor = '#FF0055'; ctx.shadowBlur = 10;
        ctx.beginPath(); ctx.arc(ss.x, ss.y, 5, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#fff'; ctx.font = `bold ${Math.max(9, 11 * mapZoom)}px Rajdhani, sans-serif`;
        ctx.textAlign = 'center'; ctx.fillText('SNARE', ss.x, ss.y - 10);
      }
    }

    // Draw route if exists (route tab)
    if (activeTab === 'route' && route?.waypoints) {
      route.waypoints.forEach(wp => {
        const fromLoc = locations.find(l => l.id === wp.from_id), toLoc = locations.find(l => l.id === wp.to_id);
        if (fromLoc && toLoc) {
          const sf = toScreen(fromLoc.map_x, fromLoc.map_y), st = toScreen(toLoc.map_x, toLoc.map_y);
          const isJump = wp.type === 'jump';
          ctx.strokeStyle = isJump ? '#FF6B35' : '#00D4FF'; ctx.lineWidth = isJump ? 3 : 2.5;
          ctx.setLineDash(isJump ? [8, 4] : []); ctx.shadowColor = ctx.strokeStyle; ctx.shadowBlur = 8;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
          ctx.shadowBlur = 0; ctx.setLineDash([]);
          // Arrow
          const angle = Math.atan2(st.y - sf.y, st.x - sf.x);
          const mx = (sf.x + st.x) / 2, my = (sf.y + st.y) / 2;
          ctx.fillStyle = isJump ? '#FF6B35' : '#00D4FF';
          ctx.beginPath();
          ctx.moveTo(mx + 6 * Math.cos(angle), my + 6 * Math.sin(angle));
          ctx.lineTo(mx - 6 * Math.cos(angle) - 4 * Math.sin(angle), my - 6 * Math.sin(angle) + 4 * Math.cos(angle));
          ctx.lineTo(mx - 6 * Math.cos(angle) + 4 * Math.sin(angle), my - 6 * Math.sin(angle) - 4 * Math.cos(angle));
          ctx.fill();
        }
      });
    }

    // Locations
    const isInterdict = activeTab === 'interdiction';
    locations.forEach(loc => {
      const s = toScreen(loc.map_x, loc.map_y);
      if (s.x < -20 || s.x > w + 20 || s.y < -20 || s.y > h + 20) return;
      const r = (TYPE_RADIUS[loc.type] || 3) * mapZoom;
      const color = TYPE_COLORS[loc.type] || '#888';
      const isOriginSel = isInterdict ? interdictOrigins.includes(loc.id) : loc.id === origin;
      const isDestSel = isInterdict ? loc.id === interdictDest : loc.id === destination;
      const isHov = hoveredLoc === loc.id;

      if (isOriginSel || isDestSel || isHov) { ctx.shadowColor = isOriginSel ? '#00FF9D' : isDestSel ? '#FF0055' : color; ctx.shadowBlur = 12; }

      ctx.fillStyle = color;
      if (loc.type === 'gateway') {
        ctx.beginPath(); ctx.moveTo(s.x, s.y - r); ctx.lineTo(s.x + r, s.y); ctx.lineTo(s.x, s.y + r); ctx.lineTo(s.x - r, s.y); ctx.closePath(); ctx.fill();
      } else if (loc.type === 'star') {
        const gradient = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, r * 2);
        gradient.addColorStop(0, color); gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(s.x, s.y, r * 2, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = color; ctx.beginPath(); ctx.arc(s.x, s.y, r * 0.6, 0, Math.PI * 2); ctx.fill();
      } else {
        ctx.beginPath(); ctx.arc(s.x, s.y, r, 0, Math.PI * 2); ctx.fill();
      }

      if (isOriginSel || isDestSel) {
        ctx.strokeStyle = isOriginSel ? '#00FF9D' : '#FF0055'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(s.x, s.y, r + 4, 0, Math.PI * 2); ctx.stroke();
      }
      ctx.shadowBlur = 0;

      if (mapZoom > 0.6 || loc.type === 'planet' || loc.type === 'star' || isOriginSel || isDestSel || isHov) {
        ctx.fillStyle = isOriginSel ? '#00FF9D' : isDestSel ? '#FF0055' : 'rgba(255,255,255,0.7)';
        ctx.font = `${loc.type === 'planet' ? 'bold ' : ''}${Math.max(8, (loc.type === 'moon' || loc.type === 'station' ? 9 : 11) * mapZoom)}px Rajdhani, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(loc.name, s.x, s.y + r + 12 * mapZoom);
      }
    });
  }, [locations, systems, origin, destination, route, interdictOrigins, interdictDest, interdictResult, mapOffset, mapZoom, hoveredLoc, activeTab]);

  useEffect(() => { drawMap(); }, [drawMap]);

  useEffect(() => {
    const resize = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const parent = canvas.parentElement;
      canvas.width = parent.clientWidth; canvas.height = parent.clientHeight;
      drawMap();
    };
    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, [drawMap]);

  const handleWheel = (e) => { e.preventDefault(); setMapZoom(z => Math.max(0.3, Math.min(3, z + (e.deltaY > 0 ? -0.1 : 0.1)))); };
  const handleMouseDown = (e) => { if (e.button === 0) { setDragging(true); setDragStart({ x: e.clientX - mapOffset.x, y: e.clientY - mapOffset.y }); } };
  const handleMouseMove = (e) => {
    const canvas = canvasRef.current; if (!canvas) return;
    if (dragging) { setMapOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y }); return; }
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    const w = canvas.width, h = canvas.height;
    let found = null;
    locations.forEach(loc => {
      const sx = w / 2 + (loc.map_x * mapZoom) + mapOffset.x, sy = h / 2 + (loc.map_y * mapZoom) + mapOffset.y;
      if (Math.sqrt((mx - sx) ** 2 + (my - sy) ** 2) < 15) found = loc.id;
    });
    setHoveredLoc(found);
    canvas.style.cursor = found ? 'pointer' : dragging ? 'grabbing' : 'grab';
  };
  const handleMouseUp = () => setDragging(false);
  const handleCanvasClick = () => {
    if (!hoveredLoc) return;
    if (activeTab === 'interdiction') {
      // In interdiction mode, clicking adds origins, shift+click or if origins exist sets dest
      if (!interdictDest) { setInterdictDest(hoveredLoc); } else { addInterdictOrigin(hoveredLoc); }
    } else {
      if (!origin) setOrigin(hoveredLoc);
      else if (!destination) setDestination(hoveredLoc);
      else { setOrigin(hoveredLoc); setDestination(''); setRoute(null); }
    }
  };

  const formatTime = (seconds) => {
    if (!seconds) return '0s';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const m = Math.floor(seconds / 60), s = Math.round(seconds % 60);
    if (m < 60) return `${m}m ${s}s`;
    return `${Math.floor(m / 60)}h ${m % 60}m`;
  };

  const LocationSelect = ({ value, onChange, label, color, testId, exclude = [] }) => (
    <div>
      <label className="text-xs font-semibold uppercase block mb-1" style={{ color }}>{label}</label>
      <select value={value} onChange={e => onChange(e.target.value)} data-testid={testId}
        className="w-full px-3 py-2 bg-white/5 border rounded-lg text-white text-sm focus:outline-none transition-all"
        style={{ borderColor: `${color}40`, '--tw-ring-color': color }}>
        <option value="">Select...</option>
        {Object.entries(systems).map(([sysId, sys]) => (
          <optgroup key={sysId} label={sys.name}>
            {locations.filter(l => l.system === sysId && l.type !== 'star' && !exclude.includes(l.id)).map(l => (
              <option key={l.id} value={l.id}>{l.name}</option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div></div>;

  return (
    <div className="h-[calc(100vh-80px)] flex gap-4" data-testid="route-planner-page">
      {/* Left Panel */}
      <div className="w-80 shrink-0 flex flex-col overflow-hidden">
        <div className="mb-3">
          <h1 className="text-2xl font-bold uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>Route Planner</h1>
          <p className="text-xs text-gray-500 mt-0.5">Stanton / Pyro / Nyx</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-3 bg-white/5 rounded-lg p-1" data-testid="planner-tabs">
          {TABS.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} data-testid={`tab-${tab.id}`}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-md text-xs font-bold uppercase transition-all ${activeTab === tab.id ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-gray-300'}`}>
              <tab.icon className="w-3.5 h-3.5" /> {tab.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          {/* === ROUTE TAB === */}
          {activeTab === 'route' && (<>
            <div className="glass-panel rounded-xl p-3" data-testid="ship-selector">
              <label className="text-xs font-semibold text-gray-400 uppercase block mb-1.5">Ship</label>
              <select value={selectedShip?.id || ''} onChange={e => onShipSelect(e.target.value)} data-testid="ship-select"
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500">
                <option value="">Select a ship...</option>
                {ships.map(s => <option key={s.id} value={s.id}>{s.name} (QD S{s.hardpoints?.quantum_drive?.size || '?'})</option>)}
              </select>
              {selectedShip && <div className="mt-1.5 text-xs text-gray-400">QD S{qdSize} | {(qdSpeeds[qdSize] || 165000).toLocaleString()} km/s</div>}
            </div>
            <div className="glass-panel rounded-xl p-3 space-y-2.5" data-testid="route-selectors">
              <LocationSelect value={origin} onChange={v => { setOrigin(v); setRoute(null); }} label="Origin" color="#00FF9D" testId="origin-select" />
              <button onClick={swapOriginDest} data-testid="swap-btn" className="w-full flex items-center justify-center gap-2 py-1 rounded-lg bg-white/5 text-gray-400 hover:text-white text-xs"><ArrowLeftRight className="w-3 h-3" /> Swap</button>
              <LocationSelect value={destination} onChange={v => { setDestination(v); setRoute(null); }} label="Destination" color="#FF0055" testId="destination-select" />
              {!selectedShip && (
                <div>
                  <label className="text-xs font-semibold text-gray-400 uppercase block mb-1">QD Size</label>
                  <div className="flex gap-2">
                    {[1, 2, 3].map(s => (
                      <button key={s} onClick={() => { setQdSize(s); setRoute(null); }} data-testid={`qd-size-${s}`}
                        className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${qdSize === s ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-400 border border-white/10'}`}>S{s}</button>
                    ))}
                  </div>
                </div>
              )}
              <button onClick={calcRoute} disabled={!origin || !destination || calculating} data-testid="calculate-route-btn"
                className="w-full py-2.5 rounded-xl font-bold text-sm text-black disabled:opacity-40 transition-all" style={{ background: 'linear-gradient(135deg, #00D4FF, #00A8CC)' }}>
                {calculating ? 'Calculating...' : 'Calculate Route'}
              </button>
            </div>
            {route && <RouteResults route={route} formatTime={formatTime} />}
          </>)}

          {/* === INTERDICTION TAB === */}
          {activeTab === 'interdiction' && (<>
            <div className="glass-panel rounded-xl p-3 space-y-3" data-testid="interdiction-panel">
              <div className="flex items-center gap-2 text-xs text-red-400">
                <Target className="w-4 h-4" /> <span className="font-bold uppercase">QED Snare Planning</span>
              </div>

              {/* Destination */}
              <LocationSelect value={interdictDest} onChange={v => { setInterdictDest(v); setInterdictResult(null); }} label="Target Destination" color="#FF0055" testId="interdict-dest" />

              {/* Origins */}
              <div>
                <label className="text-xs font-semibold text-green-400 uppercase block mb-1">Possible Origins ({interdictOrigins.length})</label>
                <div className="space-y-1 mb-2">
                  {interdictOrigins.map(oid => (
                    <div key={oid} className="flex items-center justify-between px-2 py-1 bg-green-500/10 border border-green-500/20 rounded-lg text-xs">
                      <span className="text-green-400">{locName(oid)}</span>
                      <button onClick={() => removeInterdictOrigin(oid)} className="text-gray-500 hover:text-red-400"><X className="w-3 h-3" /></button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <select id="add-origin-select" data-testid="add-origin-select"
                    className="flex-1 px-2 py-1.5 bg-white/5 border border-white/10 rounded-lg text-white text-xs focus:outline-none">
                    <option value="">Add origin...</option>
                    {Object.entries(systems).map(([sysId, sys]) => (
                      <optgroup key={sysId} label={sys.name}>
                        {locations.filter(l => l.system === sysId && l.type !== 'star' && !interdictOrigins.includes(l.id)).map(l => (
                          <option key={l.id} value={l.id}>{l.name}</option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                  <button onClick={() => { const sel = document.getElementById('add-origin-select'); addInterdictOrigin(sel.value); sel.value = ''; }}
                    data-testid="add-origin-btn" className="p-1.5 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors">
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Snare Range */}
              <div>
                <label className="text-xs font-semibold text-gray-400 uppercase block mb-1">Snare Range: {snareRange} Mkm</label>
                <input type="range" min="2" max="20" step="0.5" value={snareRange}
                  onChange={e => { setSnareRange(parseFloat(e.target.value)); setInterdictResult(null); }}
                  data-testid="snare-range-slider"
                  className="w-full accent-red-500" />
                <div className="flex justify-between text-[10px] text-gray-600"><span>2 Mkm</span><span>20 Mkm</span></div>
              </div>

              <button onClick={calcInterdiction} disabled={interdictOrigins.length === 0 || !interdictDest || interdicting}
                data-testid="calc-interdiction-btn"
                className="w-full py-2.5 rounded-xl font-bold text-sm text-white disabled:opacity-40 transition-all"
                style={{ background: 'linear-gradient(135deg, #FF0055, #CC0044)' }}>
                {interdicting ? 'Calculating...' : 'Find Optimal Snare Position'}
              </button>
            </div>

            {interdictResult && <InterdictionResults result={interdictResult} />}
          </>)}

          {/* === CHASE TAB === */}
          {activeTab === 'chase' && (<>
            <div className="glass-panel rounded-xl p-3 space-y-3" data-testid="chase-panel">
              <div className="flex items-center gap-2 text-xs text-yellow-400">
                <Gauge className="w-4 h-4" /> <span className="font-bold uppercase">Chase Calculator</span>
              </div>

              <div>
                <label className="text-xs font-semibold text-cyan-400 uppercase block mb-1">Your QD Size</label>
                <div className="flex gap-2">
                  {[1, 2, 3].map(s => (
                    <button key={s} onClick={() => { setChaseYourQd(s); setChaseResult(null); }} data-testid={`chase-your-qd-${s}`}
                      className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${chaseYourQd === s ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-gray-400 border border-white/10'}`}>S{s}</button>
                  ))}
                </div>
                <div className="text-[10px] text-gray-600 mt-1">{(qdSpeeds[chaseYourQd] || 165000).toLocaleString()} km/s</div>
              </div>

              <div>
                <label className="text-xs font-semibold text-red-400 uppercase block mb-1">Target QD Size</label>
                <div className="flex gap-2">
                  {[1, 2, 3].map(s => (
                    <button key={s} onClick={() => { setChaseTargetQd(s); setChaseResult(null); }} data-testid={`chase-target-qd-${s}`}
                      className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${chaseTargetQd === s ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-white/5 text-gray-400 border border-white/10'}`}>S{s}</button>
                  ))}
                </div>
                <div className="text-[10px] text-gray-600 mt-1">{(qdSpeeds[chaseTargetQd] || 165000).toLocaleString()} km/s</div>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-400 uppercase block mb-1">Distance to Target: {chaseDist} Mkm</label>
                <input type="range" min="1" max="60" step="1" value={chaseDist}
                  onChange={e => { setChaseDist(parseFloat(e.target.value)); setChaseResult(null); }}
                  data-testid="chase-dist-slider" className="w-full accent-yellow-500" />
                <div className="flex justify-between text-[10px] text-gray-600"><span>1 Mkm</span><span>60 Mkm</span></div>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-400 uppercase block mb-1">Prep Time: {chasePrep}s</label>
                <input type="range" min="5" max="120" step="5" value={chasePrep}
                  onChange={e => { setChasePrep(parseInt(e.target.value)); setChaseResult(null); }}
                  data-testid="chase-prep-slider" className="w-full accent-yellow-500" />
                <div className="flex justify-between text-[10px] text-gray-600"><span>5s</span><span>120s</span></div>
              </div>

              <button onClick={calcChase} data-testid="calc-chase-btn"
                className="w-full py-2.5 rounded-xl font-bold text-sm text-black disabled:opacity-40 transition-all"
                style={{ background: 'linear-gradient(135deg, #FFAE00, #FF8C00)' }}>
                Calculate Chase
              </button>
            </div>

            {chaseResult && <ChaseResults result={chaseResult} qdSpeeds={qdSpeeds} formatTime={formatTime} />}
          </>)}

          {/* Legend */}
          <div className="glass-panel rounded-xl p-3" data-testid="map-legend">
            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1.5">Legend</h4>
            <div className="grid grid-cols-2 gap-1 text-[10px]">
              {Object.entries(TYPE_COLORS).map(([type, color]) => (
                <div key={type} className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                  <span className="text-gray-400 capitalize">{type}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Map Canvas */}
      <div className="flex-1 glass-panel rounded-xl overflow-hidden relative" data-testid="star-map">
        <canvas ref={canvasRef} onWheel={handleWheel} onMouseDown={handleMouseDown} onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp} onClick={handleCanvasClick} className="w-full h-full" />
        <div className="absolute top-3 right-3 flex items-center gap-2">
          <button onClick={() => { setMapOffset({ x: 0, y: 0 }); setMapZoom(1); }} data-testid="reset-map"
            className="p-2 bg-black/60 backdrop-blur rounded-lg text-gray-400 hover:text-white transition-colors">
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
        {hoveredLoc && (
          <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur rounded-lg px-3 py-2 text-xs pointer-events-none">
            <div className="font-bold text-white">{locName(hoveredLoc)}</div>
            <div className="text-gray-400 capitalize">{locations.find(l => l.id === hoveredLoc)?.type} - {locations.find(l => l.id === hoveredLoc)?.system}</div>
          </div>
        )}
        <div className="absolute bottom-3 right-3 text-[10px] text-gray-600 bg-black/40 px-2 py-1 rounded">{Math.round(mapZoom * 100)}%</div>
      </div>
    </div>
  );
};

// --- Sub-components ---

const RouteResults = ({ route, formatTime }) => (
  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
    className="glass-panel rounded-xl p-3 space-y-3" data-testid="route-results">
    <h3 className="text-xs font-bold uppercase text-gray-400">Route Details</h3>
    <div className="grid grid-cols-2 gap-2">
      <div className="bg-white/5 rounded-lg p-2.5 text-center">
        <Ruler className="w-4 h-4 mx-auto mb-1 text-cyan-400" />
        <div className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{route.total_distance_mkm.toLocaleString()}</div>
        <div className="text-[10px] text-gray-500">Mkm</div>
      </div>
      <div className="bg-white/5 rounded-lg p-2.5 text-center">
        <Clock className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
        <div className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{formatTime(route.travel_time_seconds)}</div>
        <div className="text-[10px] text-gray-500">Travel Time</div>
      </div>
    </div>
    <div className="text-xs text-gray-500 flex items-center gap-2">
      <Zap className="w-3 h-3 text-cyan-400" /> QD S{route.qd_size} at {route.qd_speed_kms.toLocaleString()} km/s
      {route.cross_system && <span className="px-1.5 py-0.5 bg-orange-500/20 text-orange-400 rounded text-[10px]">Cross-System</span>}
    </div>
    <div className="space-y-1">
      <h4 className="text-xs font-semibold text-gray-400 uppercase">Waypoints</h4>
      {route.waypoints.map((wp, i) => (
        <div key={i} className={`flex items-center gap-2 p-2 rounded-lg text-xs ${wp.type === 'jump' ? 'bg-orange-500/10 border border-orange-500/20' : 'bg-white/[0.03]'}`} data-testid={`waypoint-${i}`}>
          <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${wp.type === 'jump' ? 'bg-orange-500/30 text-orange-400' : 'bg-cyan-500/20 text-cyan-400'}`}>{i + 1}</div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1 text-gray-300">
              <span className="truncate">{wp.from}</span><ChevronRight className="w-3 h-3 text-gray-600 shrink-0" /><span className="truncate">{wp.to}</span>
            </div>
            <div className="text-gray-600">{wp.distance_mkm} Mkm{wp.type === 'jump' ? ' (Jump Tunnel)' : ''}</div>
          </div>
        </div>
      ))}
    </div>
  </motion.div>
);

const InterdictionResults = ({ result }) => (
  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
    className="glass-panel rounded-xl p-3 space-y-3" data-testid="interdiction-results">
    <div className="flex items-center gap-2">
      {result.coverage_pct === 100
        ? <CheckCircle className="w-4 h-4 text-green-400" />
        : <AlertTriangle className="w-4 h-4 text-yellow-400" />}
      <span className={`text-xs font-bold ${result.coverage_pct === 100 ? 'text-green-400' : 'text-yellow-400'}`}>
        {result.message}
      </span>
    </div>
    <div className="grid grid-cols-2 gap-2">
      <div className="bg-white/5 rounded-lg p-2.5 text-center">
        <div className={`text-2xl font-bold ${result.coverage_pct === 100 ? 'text-green-400' : 'text-yellow-400'}`} style={{ fontFamily: 'Rajdhani, sans-serif' }}>
          {result.coverage_pct}%
        </div>
        <div className="text-[10px] text-gray-500">Coverage</div>
      </div>
      <div className="bg-white/5 rounded-lg p-2.5 text-center">
        <div className="text-2xl font-bold text-red-400" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
          {result.routes_covered}/{result.routes_total}
        </div>
        <div className="text-[10px] text-gray-500">Routes Covered</div>
      </div>
    </div>
    {result.distance_to_dest_mkm && (
      <div className="text-xs text-gray-400">
        Snare position: <span className="text-red-400 font-semibold">{result.distance_to_dest_mkm} Mkm</span> from destination
      </div>
    )}
    <div className="text-xs text-gray-500">
      Snare range: {result.snare_range_mkm} Mkm | Covers {result.routes_covered} route{result.routes_covered > 1 ? 's' : ''}
    </div>
    <div>
      <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Target Routes</h4>
      {(result.route_lines || []).map((rl, i) => (
        <div key={i} className="text-xs text-gray-300 py-0.5">{rl.from} → {result.destination.name}</div>
      ))}
    </div>
  </motion.div>
);

const ChaseResults = ({ result, qdSpeeds, formatTime }) => (
  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
    className="glass-panel rounded-xl p-3 space-y-3" data-testid="chase-results">
    <div className="flex items-center gap-2">
      {result.can_catch
        ? <CheckCircle className="w-4 h-4 text-green-400" />
        : <AlertTriangle className="w-4 h-4 text-red-400" />}
      <span className={`text-xs font-bold ${result.can_catch ? 'text-green-400' : 'text-red-400'}`}>
        {result.can_catch ? 'Target Catchable' : 'Cannot Catch'}
      </span>
    </div>
    <div className="p-3 rounded-lg text-xs leading-relaxed"
      style={{ background: result.can_catch ? 'rgba(0,255,157,0.05)' : 'rgba(255,0,85,0.05)', border: `1px solid ${result.can_catch ? 'rgba(0,255,157,0.2)' : 'rgba(255,0,85,0.2)'}` }}>
      {result.verdict}
    </div>
    <div className="grid grid-cols-2 gap-2 text-xs">
      <div className="bg-white/5 rounded-lg p-2">
        <div className="text-gray-500">Your QD</div>
        <div className="text-cyan-400 font-bold">{result.your_speed_kms?.toLocaleString()} km/s</div>
      </div>
      <div className="bg-white/5 rounded-lg p-2">
        <div className="text-gray-500">Target QD</div>
        <div className="text-red-400 font-bold">{result.target_speed_kms?.toLocaleString()} km/s</div>
      </div>
    </div>
    {result.can_catch && (
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-gray-500">Closing Time</div>
          <div className="text-yellow-400 font-bold">{formatTime(result.closing_time_seconds)}</div>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-gray-500">Total (+ prep)</div>
          <div className="text-yellow-400 font-bold">{formatTime(result.total_time_seconds)}</div>
        </div>
      </div>
    )}
    <div className="text-[10px] text-gray-600">
      Speed {result.speed_advantage_kms > 0 ? 'advantage' : 'disadvantage'}: {Math.abs(result.speed_advantage_kms || 0).toLocaleString()} km/s
    </div>
  </motion.div>
);

export default RoutePlanner;
