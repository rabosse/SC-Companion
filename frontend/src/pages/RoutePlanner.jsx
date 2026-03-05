import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Navigation, Clock, Ruler, Ship, ChevronRight, Zap, RotateCcw, ArrowLeftRight, Target, Gauge, Plus, X, AlertTriangle, CheckCircle, Fuel, Anchor, ToggleLeft, ToggleRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPE_COLORS = { star: '#FFD700', planet: '#00D4FF', moon: '#5A7A8F', station: '#00FF9D', gateway: '#FF6B35', city: '#FF1493', rest_stop: '#FFAE00', outpost: '#7CB342' };
const SYSTEM_COLORS = { stanton: '#00D4FF', pyro: '#FF4500', nyx: '#A855F7' };
const TYPE_RADIUS = { star: 8, planet: 6, moon: 3, station: 3, gateway: 5, city: 5, rest_stop: 3, outpost: 3 };
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
  const [allShips, setAllShips] = useState([]);
  const [fleetShips, setFleetShips] = useState([]);
  const [useFleet, setUseFleet] = useState(true);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('route');

  const [selectedShip, setSelectedShip] = useState(null);
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [qdSize, setQdSize] = useState(1);
  const [route, setRoute] = useState(null);
  const [calculating, setCalculating] = useState(false);

  const [interdictOrigins, setInterdictOrigins] = useState([]);
  const [interdictDest, setInterdictDest] = useState('');
  const [snareRange, setSnareRange] = useState(7.5);
  const [interdictResult, setInterdictResult] = useState(null);
  const [interdicting, setInterdicting] = useState(false);

  const [chaseYourQd, setChaseYourQd] = useState(1);
  const [chaseTargetQd, setChaseTargetQd] = useState(1);
  const [chaseDist, setChaseDist] = useState(10);
  const [chasePrep, setChasePrep] = useState(30);
  const [chaseResult, setChaseResult] = useState(null);

  const canvasRef = useRef(null);
  const [mapOffset, setMapOffset] = useState({ x: 0, y: 0 });
  const [mapZoom, setMapZoom] = useState(1);
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [hoveredLoc, setHoveredLoc] = useState(null);

  const ships = useMemo(() => {
    if (useFleet && fleetShips.length > 0) return fleetShips;
    return allShips;
  }, [useFleet, fleetShips, allShips]);

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
        const shipData = (shipsRes.data.data || []).filter(s => !s.is_ground_vehicle);
        setAllShips(shipData);
        // Fetch fleet
        try {
          const fleetRes = await axios.get(`${authAPI}/fleet/my`);
          const fleetIds = (fleetRes.data.data || []).map(f => f.ship_id);
          const matched = shipData.filter(s => fleetIds.includes(s.id));
          setFleetShips(matched);
        } catch { setFleetShips([]); }
      } catch { toast.error('Failed to load route data'); }
      finally { setLoading(false); }
    };
    fetchData();
  }, [authAPI]);

  const calcRoute = useCallback(async () => {
    if (!origin || !destination) { toast.error('Select both origin and destination'); return; }
    setCalculating(true);
    try {
      const params = { origin, destination, qd_size: qdSize };
      if (selectedShip?.quantum?.speed_kms) params.qd_speed = selectedShip.quantum.speed_kms;
      if (selectedShip?.quantum?.range_mkm) params.qd_range = selectedShip.quantum.range_mkm;
      const res = await axios.get(`${API}/routes/calculate`, { params });
      setRoute(res.data.data);
    } catch (err) { toast.error(err.response?.data?.detail || 'Route calculation failed'); }
    finally { setCalculating(false); }
  }, [origin, destination, qdSize, selectedShip]);

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
    if (id && !interdictOrigins.includes(id)) { setInterdictOrigins(prev => [...prev, id]); setInterdictResult(null); }
  };
  const removeInterdictOrigin = (id) => { setInterdictOrigins(prev => prev.filter(o => o !== id)); setInterdictResult(null); };

  const onShipSelect = (shipId) => {
    const ship = ships.find(s => s.id === shipId);
    setSelectedShip(ship || null);
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

    // Background gradient
    const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w * 0.7);
    bgGrad.addColorStop(0, '#080c14');
    bgGrad.addColorStop(1, '#020408');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // Subtle grid with glow
    ctx.strokeStyle = 'rgba(0,212,255,0.03)';
    ctx.lineWidth = 1;
    const gridSize = 50 * mapZoom;
    const offX = (w / 2 + mapOffset.x) % gridSize, offY = (h / 2 + mapOffset.y) % gridSize;
    for (let x = offX; x < w; x += gridSize) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
    for (let y = offY; y < h; y += gridSize) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }

    // Scan-line effect
    ctx.fillStyle = 'rgba(0,212,255,0.008)';
    const scanY = (Date.now() / 40) % h;
    ctx.fillRect(0, scanY - 2, w, 4);

    const toScreen = (mx, my) => ({ x: w / 2 + (mx * mapZoom) + mapOffset.x, y: h / 2 + (my * mapZoom) + mapOffset.y });

    // System nebula glow
    Object.entries(systems).forEach(([, sys]) => {
      const center = toScreen(sys.star.x, sys.star.y);
      const nebGrad = ctx.createRadialGradient(center.x, center.y, 0, center.x, center.y, 180 * mapZoom);
      nebGrad.addColorStop(0, `${sys.color}08`);
      nebGrad.addColorStop(0.5, `${sys.color}04`);
      nebGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = nebGrad;
      ctx.beginPath(); ctx.arc(center.x, center.y, 180 * mapZoom, 0, Math.PI * 2); ctx.fill();

      // Orbit rings
      ctx.strokeStyle = `${sys.color}0a`;
      ctx.lineWidth = 1;
      [40, 80, 120, 160].forEach(r => { ctx.beginPath(); ctx.arc(center.x, center.y, r * mapZoom * 0.7, 0, Math.PI * 2); ctx.stroke(); });

      // System label
      ctx.fillStyle = `${sys.color}50`;
      ctx.font = `bold ${Math.max(10, 14 * mapZoom)}px 'Rajdhani', monospace`;
      ctx.textAlign = 'center';
      ctx.fillText(sys.name.toUpperCase(), center.x, center.y - 12 * mapZoom);
    });

    // Jump connections (dashed glowing lines)
    [['stanton-pyro-gw', 'pyro-stanton-gw'], ['stanton-nyx-gw', 'nyx-stanton-gw'], ['pyro-nyx-gw', 'nyx-pyro-gw']].forEach(([a, b]) => {
      const la = locations.find(l => l.id === a), lb = locations.find(l => l.id === b);
      if (la && lb) {
        const sa = toScreen(la.map_x, la.map_y), sb = toScreen(lb.map_x, lb.map_y);
        ctx.strokeStyle = '#FF6B3530'; ctx.lineWidth = 2; ctx.setLineDash([8, 6]);
        ctx.beginPath(); ctx.moveTo(sa.x, sa.y); ctx.lineTo(sb.x, sb.y); ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // Draw interdiction routes + snare
    if (activeTab === 'interdiction' && interdictResult) {
      (interdictResult.route_lines || []).forEach(rl => {
        const sf = toScreen(rl.sx, rl.sy), st = toScreen(rl.ex, rl.ey);
        ctx.strokeStyle = '#FF005550'; ctx.lineWidth = 1.5; ctx.setLineDash([4, 3]);
        ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
        ctx.setLineDash([]);
      });
      const sp = interdictResult.snare_position;
      if (sp) {
        const ss = toScreen(sp.x, sp.y);
        const sr = (interdictResult.snare_range_map || 25) * mapZoom;
        ctx.fillStyle = interdictResult.coverage_pct === 100 ? 'rgba(255,0,85,0.06)' : 'rgba(255,165,0,0.06)';
        ctx.beginPath(); ctx.arc(ss.x, ss.y, sr, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = interdictResult.coverage_pct === 100 ? '#FF0055' : '#FFA500';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(ss.x, ss.y, sr, 0, Math.PI * 2); ctx.stroke();
        ctx.fillStyle = '#FF0055'; ctx.shadowColor = '#FF0055'; ctx.shadowBlur = 12;
        ctx.beginPath(); ctx.arc(ss.x, ss.y, 5, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#FF005590'; ctx.font = `bold ${Math.max(8, 10 * mapZoom)}px 'Rajdhani', monospace`;
        ctx.textAlign = 'center'; ctx.fillText('SNARE', ss.x, ss.y - 10);
      }
    }

    // Draw route lines with glow
    if (activeTab === 'route' && route?.waypoints) {
      route.waypoints.forEach(wp => {
        if (wp.type === 'refuel') return;
        const fromLoc = locations.find(l => l.id === wp.from_id), toLoc = locations.find(l => l.id === wp.to_id);
        if (fromLoc && toLoc) {
          const sf = toScreen(fromLoc.map_x, fromLoc.map_y), st = toScreen(toLoc.map_x, toLoc.map_y);
          const isJump = wp.type === 'jump';
          // Glow layer
          ctx.strokeStyle = isJump ? '#FF6B3520' : '#00D4FF18';
          ctx.lineWidth = isJump ? 8 : 6;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
          // Main line
          ctx.strokeStyle = isJump ? '#FF6B35' : '#00D4FF';
          ctx.lineWidth = isJump ? 2.5 : 2;
          ctx.setLineDash(isJump ? [8, 4] : []);
          ctx.shadowColor = ctx.strokeStyle; ctx.shadowBlur = 6;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
          ctx.shadowBlur = 0; ctx.setLineDash([]);
          // Arrow
          const angle = Math.atan2(st.y - sf.y, st.x - sf.x);
          const mx = (sf.x + st.x) / 2, my = (sf.y + st.y) / 2;
          ctx.fillStyle = isJump ? '#FF6B35' : '#00D4FF';
          ctx.beginPath();
          ctx.moveTo(mx + 7 * Math.cos(angle), my + 7 * Math.sin(angle));
          ctx.lineTo(mx - 7 * Math.cos(angle) - 5 * Math.sin(angle), my - 7 * Math.sin(angle) + 5 * Math.cos(angle));
          ctx.lineTo(mx - 7 * Math.cos(angle) + 5 * Math.sin(angle), my - 7 * Math.sin(angle) - 5 * Math.cos(angle));
          ctx.fill();
        }
      });
      // Draw refuel markers
      route.waypoints.forEach(wp => {
        if (wp.type !== 'refuel') return;
        const loc = locations.find(l => l.id === wp.from_id);
        if (loc) {
          const s = toScreen(loc.map_x, loc.map_y);
          ctx.fillStyle = '#FFAE00'; ctx.shadowColor = '#FFAE00'; ctx.shadowBlur = 14;
          ctx.beginPath(); ctx.arc(s.x, s.y, 7 * mapZoom, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;
          ctx.fillStyle = '#000'; ctx.font = `bold ${Math.max(8, 10 * mapZoom)}px sans-serif`;
          ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.fillText('F', s.x, s.y);
          ctx.textBaseline = 'alphabetic';
          ctx.fillStyle = '#FFAE00'; ctx.font = `bold ${Math.max(7, 9 * mapZoom)}px 'Rajdhani', monospace`;
          ctx.fillText('REFUEL', s.x, s.y + 14 * mapZoom);
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

      if (isOriginSel || isDestSel || isHov) { ctx.shadowColor = isOriginSel ? '#00FF9D' : isDestSel ? '#FF0055' : color; ctx.shadowBlur = 14; }

      ctx.fillStyle = color;
      if (loc.type === 'gateway') {
        ctx.beginPath(); ctx.moveTo(s.x, s.y - r); ctx.lineTo(s.x + r, s.y); ctx.lineTo(s.x, s.y + r); ctx.lineTo(s.x - r, s.y); ctx.closePath(); ctx.fill();
      } else if (loc.type === 'star') {
        const gradient = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, r * 2.5);
        gradient.addColorStop(0, '#ffffff'); gradient.addColorStop(0.3, color); gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(s.x, s.y, r * 2.5, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(s.x, s.y, r * 0.4, 0, Math.PI * 2); ctx.fill();
      } else {
        ctx.beginPath(); ctx.arc(s.x, s.y, r, 0, Math.PI * 2); ctx.fill();
      }

      if (isOriginSel || isDestSel) {
        ctx.strokeStyle = isOriginSel ? '#00FF9D' : '#FF0055'; ctx.lineWidth = 1.5;
        ctx.setLineDash([3, 3]);
        ctx.beginPath(); ctx.arc(s.x, s.y, r + 5, 0, Math.PI * 2); ctx.stroke();
        ctx.setLineDash([]);
      }
      ctx.shadowBlur = 0;

      if (mapZoom > 0.6 || loc.type === 'planet' || loc.type === 'star' || isOriginSel || isDestSel || isHov) {
        ctx.fillStyle = isOriginSel ? '#00FF9D' : isDestSel ? '#FF0055' : 'rgba(255,255,255,0.55)';
        ctx.font = `${loc.type === 'planet' ? 'bold ' : ''}${Math.max(7, (loc.type === 'moon' || loc.type === 'station' ? 8 : 10) * mapZoom)}px 'Rajdhani', monospace`;
        ctx.textAlign = 'center';
        ctx.fillText(loc.name, s.x, s.y + r + 11 * mapZoom);
      }
    });

    // HUD overlay corners
    ctx.strokeStyle = '#00D4FF20';
    ctx.lineWidth = 1;
    const cs = 15;
    [[0, 0, cs, 0, 0, cs], [w, 0, -cs, 0, 0, cs], [0, h, cs, 0, 0, -cs], [w, h, -cs, 0, 0, -cs]].forEach(([x, y, dx1, dy1, dx2, dy2]) => {
      ctx.beginPath(); ctx.moveTo(x + dx1, y + dy1); ctx.lineTo(x, y); ctx.lineTo(x + dx2, y + dy2); ctx.stroke();
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
      if (!interdictDest) setInterdictDest(hoveredLoc); else addInterdictOrigin(hoveredLoc);
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
      <label className="text-[10px] font-bold uppercase tracking-widest block mb-1" style={{ color }}>{label}</label>
      <select value={value} onChange={e => onChange(e.target.value)} data-testid={testId}
        className="w-full px-3 py-2 bg-[#060a12] border rounded text-white text-xs focus:outline-none transition-all"
        style={{ borderColor: `${color}30`, colorScheme: 'dark' }}>
        <option value="" className="bg-[#060a12] text-gray-500">Select location...</option>
        {Object.entries(systems).map(([sysId, sys]) => (
          <optgroup key={sysId} label={sys.name} className="bg-[#060a12] text-gray-300">
            {locations.filter(l => l.system === sysId && l.type !== 'star' && !exclude.includes(l.id)).map(l => (
              <option key={l.id} value={l.id} className="bg-[#060a12] text-white">{l.name}</option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><div className="w-16 h-16 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin"></div></div>;

  return (
    <div className="h-[calc(100vh-80px)] flex gap-3" data-testid="route-planner-page">
      {/* Left Panel - HUD Style */}
      <div className="w-[310px] shrink-0 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="mb-3 relative">
          <div className="flex items-center gap-2">
            <div className="w-1 h-8 bg-cyan-500 rounded-full" />
            <div>
              <h1 className="text-xl font-bold uppercase tracking-wider" style={{ fontFamily: 'Rajdhani, monospace', color: '#00D4FF' }}>
                ROUTE PLANNER
              </h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-mono">Stanton // Pyro // Nyx</p>
            </div>
          </div>
        </div>

        {/* Tabs - HUD Buttons */}
        <div className="flex gap-1 mb-3" data-testid="planner-tabs">
          {TABS.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} data-testid={`tab-${tab.id}`}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-[10px] font-bold uppercase tracking-wider transition-all border-b-2 ${activeTab === tab.id ? 'text-white border-cyan-500 bg-cyan-500/5' : 'text-gray-600 border-transparent hover:text-gray-400 hover:border-gray-700'}`}>
              <tab.icon className="w-3 h-3" /> {tab.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 custom-scrollbar">
          {/* === ROUTE TAB === */}
          {activeTab === 'route' && (<>
            {/* Ship Selector with Fleet Toggle */}
            <div className="hud-panel p-3" data-testid="ship-selector">
              <div className="flex items-center justify-between mb-2">
                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Ship</label>
                <button onClick={() => setUseFleet(f => !f)} data-testid="fleet-toggle"
                  className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider transition-all hover:opacity-80"
                  style={{ color: useFleet ? '#00FF9D' : '#888' }}>
                  {useFleet ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
                  {useFleet ? 'Fleet' : 'All Ships'}
                </button>
              </div>
              <select value={selectedShip?.id || ''} onChange={e => onShipSelect(e.target.value)} data-testid="ship-select"
                className="w-full px-3 py-2 bg-[#060a12] border border-white/8 rounded text-white text-xs focus:outline-none focus:border-cyan-500/50" style={{ colorScheme: 'dark' }}>
                <option value="" className="bg-[#060a12] text-gray-500">
                  {useFleet && fleetShips.length === 0 ? 'No ships in fleet' : 'Select a ship...'}
                </option>
                {ships.map(s => (
                  <option key={s.id} value={s.id} className="bg-[#060a12] text-white">
                    {s.name} ({s.quantum?.speed_kms ? `${Math.round(s.quantum.speed_kms / 1000)}k km/s` : `QD S${s.hardpoints?.quantum_drive?.size || '?'}`})
                  </option>
                ))}
              </select>
              {selectedShip && (
                <div className="mt-2 grid grid-cols-3 gap-1">
                  <div className="bg-white/3 rounded px-2 py-1 text-center">
                    <div className="text-[9px] text-gray-600 uppercase">Speed</div>
                    <div className="text-xs font-bold text-cyan-400 font-mono">{selectedShip.quantum?.speed_kms ? `${Math.round(selectedShip.quantum.speed_kms / 1000)}k` : `S${qdSize}`}</div>
                  </div>
                  <div className="bg-white/3 rounded px-2 py-1 text-center">
                    <div className="text-[9px] text-gray-600 uppercase">Range</div>
                    <div className="text-xs font-bold text-yellow-400 font-mono">{selectedShip.quantum?.range_mkm ? `${Math.round(selectedShip.quantum.range_mkm)}` : '--'}<span className="text-[8px] text-gray-600"> Mkm</span></div>
                  </div>
                  <div className="bg-white/3 rounded px-2 py-1 text-center">
                    <div className="text-[9px] text-gray-600 uppercase">Fuel</div>
                    <div className="text-xs font-bold text-orange-400 font-mono">{selectedShip.quantum?.fuel_capacity || '--'}</div>
                  </div>
                </div>
              )}
            </div>

            {/* Route Config */}
            <div className="hud-panel p-3 space-y-2.5" data-testid="route-selectors">
              <LocationSelect value={origin} onChange={v => { setOrigin(v); setRoute(null); }} label="Origin" color="#00FF9D" testId="origin-select" />
              <button onClick={swapOriginDest} data-testid="swap-btn" className="w-full flex items-center justify-center gap-2 py-1 rounded text-gray-600 hover:text-gray-300 text-[10px] uppercase tracking-wider transition-all">
                <ArrowLeftRight className="w-3 h-3" /> Swap
              </button>
              <LocationSelect value={destination} onChange={v => { setDestination(v); setRoute(null); }} label="Destination" color="#FF0055" testId="destination-select" />
              {!selectedShip && (
                <div>
                  <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-1">QD Size</label>
                  <div className="flex gap-1.5">
                    {[1, 2, 3].map(s => (
                      <button key={s} onClick={() => { setQdSize(s); setRoute(null); }} data-testid={`qd-size-${s}`}
                        className={`flex-1 py-1.5 rounded text-xs font-bold font-mono transition-all ${qdSize === s ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30' : 'bg-white/3 text-gray-600 border border-white/5'}`}>S{s}</button>
                    ))}
                  </div>
                </div>
              )}
              <button onClick={calcRoute} disabled={!origin || !destination || calculating} data-testid="calculate-route-btn"
                className="w-full py-2.5 rounded font-bold text-xs uppercase tracking-widest text-black disabled:opacity-30 transition-all hover:shadow-lg hover:shadow-cyan-500/20"
                style={{ background: 'linear-gradient(135deg, #00D4FF, #0088AA)' }}>
                {calculating ? 'CALCULATING...' : 'CALCULATE ROUTE'}
              </button>
            </div>
            {route && <RouteResults route={route} formatTime={formatTime} />}
          </>)}

          {/* === INTERDICTION TAB === */}
          {activeTab === 'interdiction' && (<>
            <div className="hud-panel p-3 space-y-3" data-testid="interdiction-panel">
              <div className="flex items-center gap-2 text-[10px] text-red-400 font-bold uppercase tracking-widest">
                <Target className="w-3.5 h-3.5" /> QED Snare Planning
              </div>
              <LocationSelect value={interdictDest} onChange={v => { setInterdictDest(v); setInterdictResult(null); }} label="Target Destination" color="#FF0055" testId="interdict-dest" />
              <div>
                <label className="text-[10px] font-bold text-green-400 uppercase tracking-widest block mb-1">Possible Origins ({interdictOrigins.length})</label>
                <div className="space-y-1 mb-2">
                  {interdictOrigins.map(oid => (
                    <div key={oid} className="flex items-center justify-between px-2 py-1 bg-green-500/8 border border-green-500/15 rounded text-[10px]">
                      <span className="text-green-400 font-mono">{locName(oid)}</span>
                      <button onClick={() => removeInterdictOrigin(oid)} className="text-gray-600 hover:text-red-400"><X className="w-3 h-3" /></button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-1.5">
                  <select id="add-origin-select" data-testid="add-origin-select"
                    className="flex-1 px-2 py-1.5 bg-[#060a12] border border-white/8 rounded text-white text-[10px] focus:outline-none" style={{ colorScheme: 'dark' }}>
                    <option value="" className="bg-[#060a12] text-gray-500">Add origin...</option>
                    {Object.entries(systems).map(([sysId, sys]) => (
                      <optgroup key={sysId} label={sys.name} className="bg-[#060a12] text-gray-300">
                        {locations.filter(l => l.system === sysId && l.type !== 'star' && !interdictOrigins.includes(l.id)).map(l => (
                          <option key={l.id} value={l.id} className="bg-[#060a12] text-white">{l.name}</option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                  <button onClick={() => { const sel = document.getElementById('add-origin-select'); addInterdictOrigin(sel.value); sel.value = ''; }}
                    data-testid="add-origin-btn" className="p-1.5 bg-green-500/15 text-green-400 rounded hover:bg-green-500/25 transition-colors">
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              <div>
                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-1">Snare Range: {snareRange} Mkm</label>
                <input type="range" min="2" max="20" step="0.5" value={snareRange}
                  onChange={e => { setSnareRange(parseFloat(e.target.value)); setInterdictResult(null); }}
                  data-testid="snare-range-slider" className="w-full accent-red-500" />
              </div>
              <button onClick={calcInterdiction} disabled={interdictOrigins.length === 0 || !interdictDest || interdicting}
                data-testid="calc-interdiction-btn"
                className="w-full py-2.5 rounded font-bold text-xs uppercase tracking-widest text-white disabled:opacity-30 transition-all hover:shadow-lg hover:shadow-red-500/20"
                style={{ background: 'linear-gradient(135deg, #FF0055, #AA0033)' }}>
                {interdicting ? 'CALCULATING...' : 'FIND OPTIMAL SNARE'}
              </button>
            </div>
            {interdictResult && <InterdictionResults result={interdictResult} />}
          </>)}

          {/* === CHASE TAB === */}
          {activeTab === 'chase' && (<>
            <div className="hud-panel p-3 space-y-3" data-testid="chase-panel">
              <div className="flex items-center gap-2 text-[10px] text-yellow-400 font-bold uppercase tracking-widest">
                <Gauge className="w-3.5 h-3.5" /> Chase Calculator
              </div>
              <QdSizeSelector value={chaseYourQd} onChange={v => { setChaseYourQd(v); setChaseResult(null); }} label="Your QD" color="cyan" testPrefix="chase-your-qd" qdSpeeds={qdSpeeds} />
              <QdSizeSelector value={chaseTargetQd} onChange={v => { setChaseTargetQd(v); setChaseResult(null); }} label="Target QD" color="red" testPrefix="chase-target-qd" qdSpeeds={qdSpeeds} />
              <div>
                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-1">Distance: {chaseDist} Mkm</label>
                <input type="range" min="1" max="60" step="1" value={chaseDist}
                  onChange={e => { setChaseDist(parseFloat(e.target.value)); setChaseResult(null); }}
                  data-testid="chase-dist-slider" className="w-full accent-yellow-500" />
              </div>
              <div>
                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-1">Prep Time: {chasePrep}s</label>
                <input type="range" min="5" max="120" step="5" value={chasePrep}
                  onChange={e => { setChasePrep(parseInt(e.target.value)); setChaseResult(null); }}
                  data-testid="chase-prep-slider" className="w-full accent-yellow-500" />
              </div>
              <button onClick={calcChase} data-testid="calc-chase-btn"
                className="w-full py-2.5 rounded font-bold text-xs uppercase tracking-widest text-black disabled:opacity-30 transition-all hover:shadow-lg hover:shadow-yellow-500/20"
                style={{ background: 'linear-gradient(135deg, #FFAE00, #CC8A00)' }}>
                CALCULATE CHASE
              </button>
            </div>
            {chaseResult && <ChaseResults result={chaseResult} qdSpeeds={qdSpeeds} formatTime={formatTime} />}
          </>)}

          {/* Legend */}
          <div className="hud-panel p-2.5" data-testid="map-legend">
            <h4 className="text-[9px] font-bold text-gray-600 uppercase tracking-widest mb-1.5">Legend</h4>
            <div className="grid grid-cols-2 gap-0.5 text-[9px]">
              {Object.entries(TYPE_COLORS).map(([type, color]) => (
                <div key={type} className="flex items-center gap-1.5 py-0.5">
                  <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: color }} />
                  <span className="text-gray-500 capitalize font-mono">{type.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Map Canvas - HUD Frame */}
      <div className="flex-1 rounded overflow-hidden relative border border-white/5 bg-[#040810]" data-testid="star-map">
        <canvas ref={canvasRef} onWheel={handleWheel} onMouseDown={handleMouseDown} onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp} onClick={handleCanvasClick} className="w-full h-full" />
        {/* HUD overlays */}
        <div className="absolute top-3 left-3 text-[9px] text-cyan-500/40 font-mono uppercase tracking-widest">
          mobi-glass // nav-sys v4.6
        </div>
        <div className="absolute top-3 right-3 flex items-center gap-2">
          <button onClick={() => { setMapOffset({ x: 0, y: 0 }); setMapZoom(1); }} data-testid="reset-map"
            className="p-1.5 bg-black/40 backdrop-blur-sm border border-white/5 rounded text-gray-500 hover:text-white transition-colors">
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
        {hoveredLoc && (
          <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur-sm border border-cyan-500/20 rounded px-3 py-2 pointer-events-none">
            <div className="text-xs font-bold text-white font-mono">{locName(hoveredLoc)}</div>
            <div className="text-[9px] text-gray-500 capitalize font-mono">{locations.find(l => l.id === hoveredLoc)?.type?.replace('_', ' ')} // {locations.find(l => l.id === hoveredLoc)?.system}</div>
          </div>
        )}
        <div className="absolute bottom-3 right-3 text-[9px] text-gray-600 font-mono bg-black/40 px-2 py-0.5 rounded">{Math.round(mapZoom * 100)}%</div>
      </div>
    </div>
  );
};

// --- Sub-components ---

const QdSizeSelector = ({ value, onChange, label, color, testPrefix, qdSpeeds }) => (
  <div>
    <label className={`text-[10px] font-bold uppercase tracking-widest block mb-1 text-${color}-400`}>{label}</label>
    <div className="flex gap-1.5">
      {[1, 2, 3].map(s => (
        <button key={s} onClick={() => onChange(s)} data-testid={`${testPrefix}-${s}`}
          className={`flex-1 py-1.5 rounded text-xs font-bold font-mono transition-all ${value === s ? `bg-${color}-500/15 text-${color}-400 border border-${color}-500/30` : 'bg-white/3 text-gray-600 border border-white/5'}`}>S{s}</button>
      ))}
    </div>
    <div className="text-[9px] text-gray-600 mt-0.5 font-mono">{(qdSpeeds[value] || 165000).toLocaleString()} km/s</div>
  </div>
);

const RouteResults = ({ route, formatTime }) => (
  <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="hud-panel p-3 space-y-2.5" data-testid="route-results">
    <h3 className="text-[9px] font-bold uppercase tracking-widest text-gray-500">Route Summary</h3>
    <div className="grid grid-cols-2 gap-1.5">
      <div className="bg-white/3 rounded p-2 text-center">
        <Ruler className="w-3.5 h-3.5 mx-auto mb-0.5 text-cyan-400" />
        <div className="text-sm font-bold text-white font-mono">{route.total_distance_mkm.toLocaleString()}</div>
        <div className="text-[8px] text-gray-600 uppercase">Mkm</div>
      </div>
      <div className="bg-white/3 rounded p-2 text-center">
        <Clock className="w-3.5 h-3.5 mx-auto mb-0.5 text-yellow-400" />
        <div className="text-sm font-bold text-white font-mono">{formatTime(route.travel_time_seconds)}</div>
        <div className="text-[8px] text-gray-600 uppercase">Travel Time</div>
      </div>
    </div>

    {/* Fuel & QD Info */}
    <div className="flex items-center gap-2 text-[10px] text-gray-400 font-mono flex-wrap">
      <div className="flex items-center gap-1"><Zap className="w-3 h-3 text-cyan-400" /> S{route.qd_size} @ {route.qd_speed_kms?.toLocaleString()} km/s</div>
      {route.cross_system && <span className="px-1.5 py-0.5 bg-orange-500/15 text-orange-400 rounded text-[9px] font-bold">CROSS-SYS</span>}
    </div>
    {route.fuel_stops > 0 && (
      <div className="flex items-center gap-1.5 text-[10px] bg-yellow-500/8 border border-yellow-500/15 rounded px-2 py-1.5">
        <Fuel className="w-3 h-3 text-yellow-400" />
        <span className="text-yellow-400 font-bold">{route.fuel_stops} fuel stop{route.fuel_stops > 1 ? 's' : ''}</span>
        <span className="text-gray-500 ml-auto font-mono">+{route.refuel_time_seconds}s</span>
      </div>
    )}
    <div className="flex items-center gap-1.5 text-[10px]">
      <span className="text-gray-600">Fuel remaining:</span>
      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{
          width: `${route.fuel_remaining_pct}%`,
          background: route.fuel_remaining_pct > 40 ? '#00FF9D' : route.fuel_remaining_pct > 15 ? '#FFAE00' : '#FF0055'
        }} />
      </div>
      <span className="text-gray-500 font-mono text-[9px]">{route.fuel_remaining_pct}%</span>
    </div>

    {/* Waypoints */}
    <div className="space-y-1">
      <h4 className="text-[9px] font-bold text-gray-600 uppercase tracking-widest">Waypoints</h4>
      {route.waypoints.map((wp, i) => (
        <div key={i} data-testid={`waypoint-${i}`}
          className={`flex items-center gap-1.5 p-1.5 rounded text-[10px] ${wp.type === 'jump' ? 'bg-orange-500/8 border border-orange-500/15' : wp.type === 'refuel' ? 'bg-yellow-500/8 border border-yellow-500/15' : 'bg-white/[0.02]'}`}>
          <div className={`w-4 h-4 rounded flex items-center justify-center text-[8px] font-bold shrink-0 ${wp.type === 'jump' ? 'bg-orange-500/25 text-orange-400' : wp.type === 'refuel' ? 'bg-yellow-500/25 text-yellow-400' : 'bg-cyan-500/15 text-cyan-400'}`}>
            {wp.type === 'refuel' ? 'F' : i + 1}
          </div>
          <div className="min-w-0 flex-1">
            {wp.type === 'refuel' ? (
              <div className="text-yellow-400 font-bold font-mono">REFUELING @ {wp.from}</div>
            ) : (
              <div className="flex items-center gap-1 text-gray-300 font-mono">
                <span className="truncate">{wp.from}</span>
                <ChevronRight className="w-2.5 h-2.5 text-gray-700 shrink-0" />
                <span className="truncate">{wp.to}</span>
              </div>
            )}
            {wp.type !== 'refuel' && (
              <div className="text-gray-600 font-mono">{wp.distance_mkm} Mkm {wp.type === 'jump' ? '// JUMP' : ''}</div>
            )}
          </div>
          {wp.type !== 'refuel' && wp.fuel_remaining_pct !== undefined && (
            <div className="text-[8px] text-gray-600 shrink-0 font-mono">{wp.fuel_remaining_pct}%</div>
          )}
        </div>
      ))}
    </div>
  </motion.div>
);

const InterdictionResults = ({ result }) => (
  <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="hud-panel p-3 space-y-2.5" data-testid="interdiction-results">
    <div className="flex items-center gap-2">
      {result.coverage_pct === 100 ? <CheckCircle className="w-3.5 h-3.5 text-green-400" /> : <AlertTriangle className="w-3.5 h-3.5 text-yellow-400" />}
      <span className={`text-[10px] font-bold uppercase tracking-wider ${result.coverage_pct === 100 ? 'text-green-400' : 'text-yellow-400'}`}>{result.message}</span>
    </div>
    <div className="grid grid-cols-2 gap-1.5">
      <div className="bg-white/3 rounded p-2 text-center">
        <div className={`text-lg font-bold font-mono ${result.coverage_pct === 100 ? 'text-green-400' : 'text-yellow-400'}`}>{result.coverage_pct}%</div>
        <div className="text-[8px] text-gray-600 uppercase">Coverage</div>
      </div>
      <div className="bg-white/3 rounded p-2 text-center">
        <div className="text-lg font-bold text-red-400 font-mono">{result.routes_covered}/{result.routes_total}</div>
        <div className="text-[8px] text-gray-600 uppercase">Routes</div>
      </div>
    </div>
    {result.distance_to_dest_mkm && (
      <div className="text-[10px] text-gray-500 font-mono">Snare: <span className="text-red-400 font-bold">{result.distance_to_dest_mkm} Mkm</span> from dest</div>
    )}
  </motion.div>
);

const ChaseResults = ({ result, qdSpeeds, formatTime }) => (
  <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="hud-panel p-3 space-y-2.5" data-testid="chase-results">
    <div className="flex items-center gap-2">
      {result.can_catch ? <CheckCircle className="w-3.5 h-3.5 text-green-400" /> : <AlertTriangle className="w-3.5 h-3.5 text-red-400" />}
      <span className={`text-[10px] font-bold uppercase tracking-wider ${result.can_catch ? 'text-green-400' : 'text-red-400'}`}>{result.can_catch ? 'Target Catchable' : 'Cannot Catch'}</span>
    </div>
    <div className="p-2 rounded text-[10px] leading-relaxed font-mono" style={{
      background: result.can_catch ? 'rgba(0,255,157,0.04)' : 'rgba(255,0,85,0.04)',
      border: `1px solid ${result.can_catch ? 'rgba(0,255,157,0.15)' : 'rgba(255,0,85,0.15)'}`
    }}>{result.verdict}</div>
    <div className="grid grid-cols-2 gap-1.5 text-[10px]">
      <div className="bg-white/3 rounded p-1.5">
        <div className="text-gray-600 font-mono">Your QD</div>
        <div className="text-cyan-400 font-bold font-mono">{result.your_speed_kms?.toLocaleString()} km/s</div>
      </div>
      <div className="bg-white/3 rounded p-1.5">
        <div className="text-gray-600 font-mono">Target QD</div>
        <div className="text-red-400 font-bold font-mono">{result.target_speed_kms?.toLocaleString()} km/s</div>
      </div>
    </div>
    {result.can_catch && (
      <div className="grid grid-cols-2 gap-1.5 text-[10px]">
        <div className="bg-white/3 rounded p-1.5">
          <div className="text-gray-600 font-mono">Closing</div>
          <div className="text-yellow-400 font-bold font-mono">{formatTime(result.closing_time_seconds)}</div>
        </div>
        <div className="bg-white/3 rounded p-1.5">
          <div className="text-gray-600 font-mono">Total</div>
          <div className="text-yellow-400 font-bold font-mono">{formatTime(result.total_time_seconds)}</div>
        </div>
      </div>
    )}
  </motion.div>
);

export default RoutePlanner;
