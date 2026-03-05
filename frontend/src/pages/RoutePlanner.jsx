import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Navigation, Clock, Ruler, ChevronRight, Zap, RotateCcw, ArrowLeftRight, Target, Gauge, Plus, X, AlertTriangle, CheckCircle, Fuel, ToggleLeft, ToggleRight, Shield, Eye, Trash2, Radio, MapPin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TYPE_COLORS = { star: '#FFD700', planet: '#00D4FF', moon: '#5A7A8F', station: '#00FF9D', gateway: '#FF6B35', city: '#FF1493', rest_stop: '#FFAE00', outpost: '#7CB342' };
const NODE_RADIUS = { star: 12, planet: 7, moon: 3.5, station: 3, gateway: 6, city: 5, rest_stop: 3.5, outpost: 3 };
const LABEL_MIN_ZOOM = { star: 0, planet: 0.3, city: 0.5, gateway: 0.4, moon: 0.7, station: 0.8, rest_stop: 0.9, outpost: 0.9 };
const TABS = [
  { id: 'route', label: 'Route', icon: Navigation },
  { id: 'interdiction', label: 'Interdiction', icon: Target },
  { id: 'chase', label: 'Chase', icon: Gauge },
];

// Generate static starfield
const genStars = (count) => Array.from({ length: count }, () => ({
  x: Math.random(), y: Math.random(),
  size: Math.random() * 1.6 + 0.4,
  baseAlpha: Math.random() * 0.6 + 0.2,
  speed: Math.random() * 2 + 0.5,
  offset: Math.random() * Math.PI * 2,
}));
const STARS = genStars(500);

const RoutePlanner = () => {
  const { API: authAPI } = useAuth();
  const [locations, setLocations] = useState([]);
  const [systems, setSystems] = useState({});
  const [qdSpeeds, setQdSpeeds] = useState({});
  const [allShips, setAllShips] = useState([]);
  const [fleetShips, setFleetShips] = useState([]);
  const [useFleet, setUseFleet] = useState(false);
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
  const [interdictYourQd, setInterdictYourQd] = useState(2);
  const [interdictTargetQd, setInterdictTargetQd] = useState(1);

  const [chaseYourQd, setChaseYourQd] = useState(1);
  const [chaseTargetQd, setChaseTargetQd] = useState(1);
  const [chaseDist, setChaseDist] = useState(10);
  const [chasePrep, setChasePrep] = useState(30);
  const [chaseResult, setChaseResult] = useState(null);

  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const mapState = useRef({ offset: { x: 0, y: 0 }, zoom: 1 });
  const [mapOffset, setMapOffset] = useState({ x: 0, y: 0 });
  const [mapZoom, setMapZoom] = useState(1);
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [hoveredLoc, setHoveredLoc] = useState(null);

  // Keep refs in sync for animation loop
  const stateRef = useRef({});
  stateRef.current = { locations, systems, origin, destination, route, interdictOrigins, interdictDest, interdictResult, hoveredLoc, activeTab, mapOffset, mapZoom, interdictYourQd, interdictTargetQd };

  const ships = useMemo(() => useFleet ? fleetShips : allShips, [useFleet, fleetShips, allShips]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const locRes = await axios.get(`${API}/routes/locations`);
        setLocations(locRes.data.data || []);
        setSystems(locRes.data.systems || {});
        setQdSpeeds(locRes.data.qd_speeds || {});
      } catch { toast.error('Failed to load map data'); }
      let shipData = [];
      try {
        const shipsRes = await axios.get(`${authAPI}/ships`);
        shipData = (shipsRes.data.data || []).filter(s => !s.is_ground_vehicle);
        setAllShips(shipData);
      } catch { toast.error('Failed to load ships'); }
      try {
        const fleetRes = await axios.get(`${authAPI}/fleet/my`);
        const fleetIds = (fleetRes.data.data || []).map(f => f.ship_id);
        const matched = shipData.filter(s => fleetIds.includes(s.id));
        setFleetShips(matched);
        if (matched.length > 0) setUseFleet(true);
      } catch { setFleetShips([]); }
      setLoading(false);
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
      const res = await axios.post(`${API}/routes/interdiction`, { origins: interdictOrigins, destination: interdictDest, snare_range_mkm: snareRange, your_qd_size: interdictYourQd, target_qd_size: interdictTargetQd });
      setInterdictResult(res.data.data);
    } catch (err) { toast.error(err.response?.data?.detail || 'Interdiction calculation failed'); }
    finally { setInterdicting(false); }
  }, [interdictOrigins, interdictDest, snareRange, interdictYourQd, interdictTargetQd]);

  const calcChase = useCallback(async () => {
    try {
      const res = await axios.post(`${API}/routes/chase`, { your_qd_size: chaseYourQd, target_qd_size: chaseTargetQd, distance_mkm: chaseDist, prep_time_seconds: chasePrep });
      setChaseResult(res.data.data);
    } catch { toast.error('Chase calculation failed'); }
  }, [chaseYourQd, chaseTargetQd, chaseDist, chasePrep]);

  const addInterdictOrigin = (id) => { if (id && !interdictOrigins.includes(id)) { setInterdictOrigins(prev => [...prev, id]); setInterdictResult(null); } };
  const removeInterdictOrigin = (id) => { setInterdictOrigins(prev => prev.filter(o => o !== id)); setInterdictResult(null); };
  const clearInterdiction = () => { setInterdictOrigins([]); setInterdictDest(''); setInterdictResult(null); };
  const addOriginsByType = (type) => {
    const ids = locations.filter(l => l.type === type && l.id !== interdictDest).map(l => l.id);
    setInterdictOrigins(prev => [...new Set([...prev, ...ids])]);
    setInterdictResult(null);
  };
  const onShipSelect = (shipId) => { const ship = ships.find(s => s.id === shipId); setSelectedShip(ship || null); if (ship?.hardpoints?.quantum_drive) setQdSize(ship.hardpoints.quantum_drive.size || 1); setRoute(null); };
  const swapOriginDest = () => { setOrigin(destination); setDestination(origin); setRoute(null); };
  const locName = (id) => locations.find(l => l.id === id)?.name || id;

  // ========== ANIMATED CANVAS ==========
  useEffect(() => {
    if (loading) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resize = () => {
      const p = canvas.parentElement;
      if (!p) return;
      const pw = p.clientWidth;
      const ph = p.clientHeight;
      if (pw > 10 && ph > 10 && (canvas.width !== pw || canvas.height !== ph)) {
        canvas.width = pw;
        canvas.height = ph;
      }
    };
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(canvas.parentElement);
    window.addEventListener('resize', resize);

    const toScreen = (mx, my, w, h, offset, zoom) => ({
      x: w / 2 + mx * zoom + offset.x,
      y: h / 2 + my * zoom + offset.y,
    });

    const draw = (time) => {
      const s = stateRef.current;
      const w = canvas.width, h = canvas.height;
      const { mapOffset: offset, mapZoom: zoom, locations: locs, systems: sys, origin: org, destination: dst, route: rt, hoveredLoc: hov, activeTab: tab, interdictOrigins: iOrigins, interdictDest: iDest, interdictResult: iResult } = s;
      const t = time * 0.001;

      ctx.clearRect(0, 0, w, h);

      // === BACKGROUND ===
      ctx.fillStyle = '#020306';
      ctx.fillRect(0, 0, w, h);

      // === STARFIELD ===
      for (const star of STARS) {
        const sx = star.x * w, sy = star.y * h;
        const twinkle = Math.sin(t * star.speed + star.offset) * 0.5 + 0.5;
        const alpha = star.baseAlpha * (0.4 + twinkle * 0.6);
        ctx.globalAlpha = alpha;
        ctx.fillStyle = '#c8d8f0';
        ctx.beginPath();
        ctx.arc(sx, sy, star.size, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;

      // === NEBULA GLOW PER SYSTEM ===
      const sysColors = { stanton: [0, 140, 220], pyro: [220, 60, 10], nyx: [140, 60, 220] };
      Object.entries(sys).forEach(([sysId, sysData]) => {
        const center = toScreen(sysData.star.x, sysData.star.y, w, h, offset, zoom);
        const nebR = 260 * zoom;
        const [cr, cg, cb] = sysColors[sysId] || [80, 80, 80];

        // Outer nebula haze
        const neb = ctx.createRadialGradient(center.x, center.y, 0, center.x, center.y, nebR);
        neb.addColorStop(0, `rgba(${cr},${cg},${cb},0.07)`);
        neb.addColorStop(0.35, `rgba(${cr},${cg},${cb},0.035)`);
        neb.addColorStop(0.7, `rgba(${cr},${cg},${cb},0.01)`);
        neb.addColorStop(1, 'transparent');
        ctx.fillStyle = neb;
        ctx.beginPath(); ctx.arc(center.x, center.y, nebR, 0, Math.PI * 2); ctx.fill();

        // Inner bright core
        const core = ctx.createRadialGradient(center.x, center.y, 0, center.x, center.y, nebR * 0.25);
        core.addColorStop(0, `rgba(${cr},${cg},${cb},0.12)`);
        core.addColorStop(1, 'transparent');
        ctx.fillStyle = core;
        ctx.beginPath(); ctx.arc(center.x, center.y, nebR * 0.25, 0, Math.PI * 2); ctx.fill();

        // Orbit rings
        ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.04)`;
        ctx.lineWidth = 0.8;
        for (let r = 50; r <= 220; r += 40) {
          ctx.beginPath(); ctx.arc(center.x, center.y, r * zoom, 0, Math.PI * 2); ctx.stroke();
        }

        // System label
        const labelAlpha = Math.min(1, 0.15 + zoom * 0.1);
        ctx.fillStyle = `rgba(${cr},${cg},${cb},${labelAlpha})`;
        ctx.font = `600 ${Math.max(10, 13 * zoom)}px Rajdhani, sans-serif`;
        ctx.textAlign = 'center';
        ctx.letterSpacing = '3px';
        ctx.fillText(sysData.name.toUpperCase(), center.x, center.y - 18 * zoom);
        ctx.letterSpacing = '0px';
      });

      // === JUMP CONNECTIONS (dashed glow) ===
      const jumpPairs = [['stanton-pyro-gw', 'pyro-stanton-gw'], ['stanton-nyx-gw', 'nyx-stanton-gw'], ['pyro-nyx-gw', 'nyx-pyro-gw']];
      jumpPairs.forEach(([a, b]) => {
        const la = locs.find(l => l.id === a), lb = locs.find(l => l.id === b);
        if (!la || !lb) return;
        const sa = toScreen(la.map_x, la.map_y, w, h, offset, zoom), sb = toScreen(lb.map_x, lb.map_y, w, h, offset, zoom);
        // Glow
        ctx.strokeStyle = 'rgba(255,107,53,0.06)';
        ctx.lineWidth = 6 * zoom;
        ctx.beginPath(); ctx.moveTo(sa.x, sa.y); ctx.lineTo(sb.x, sb.y); ctx.stroke();
        // Dashed line
        ctx.strokeStyle = 'rgba(255,107,53,0.2)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([6, 8]);
        ctx.lineDashOffset = -t * 20;
        ctx.beginPath(); ctx.moveTo(sa.x, sa.y); ctx.lineTo(sb.x, sb.y); ctx.stroke();
        ctx.setLineDash([]);
      });

      // === INTERDICTION OVERLAY ===
      if (tab === 'interdiction' && iResult) {
        // Route lines — green for covered, red for uncovered
        const routeDetails = iResult.route_details || [];
        (iResult.route_lines || []).forEach((rl, idx) => {
          const sf = toScreen(rl.sx, rl.sy, w, h, offset, zoom), st = toScreen(rl.ex, rl.ey, w, h, offset, zoom);
          const isCovered = routeDetails[idx]?.covered !== false;
          const routeColor = isCovered ? 'rgba(0,255,157,0.3)' : 'rgba(255,0,85,0.4)';
          const routeGlow = isCovered ? 'rgba(0,255,157,0.06)' : 'rgba(255,0,85,0.06)';

          // Glow
          ctx.strokeStyle = routeGlow;
          ctx.lineWidth = 6 * zoom;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
          // Dashed line
          ctx.strokeStyle = routeColor;
          ctx.lineWidth = 1.5;
          ctx.setLineDash([5, 4]);
          ctx.lineDashOffset = -t * 15;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
          ctx.setLineDash([]);

          // Origin marker
          ctx.fillStyle = isCovered ? '#00FF9D' : '#FF0055';
          ctx.shadowColor = ctx.fillStyle; ctx.shadowBlur = 6;
          ctx.beginPath(); ctx.arc(sf.x, sf.y, 3 * zoom, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;
        });

        // Primary snare
        const sp = iResult.snare_position;
        if (sp) {
          const ss = toScreen(sp.x, sp.y, w, h, offset, zoom);
          const sr = (iResult.snare_range_map || 25) * zoom;
          const pulse = Math.sin(t * 3) * 0.3 + 0.7;

          // Outer glow ring
          ctx.strokeStyle = `rgba(255,0,85,${0.08 * pulse})`;
          ctx.lineWidth = 3;
          ctx.beginPath(); ctx.arc(ss.x, ss.y, sr + 4, 0, Math.PI * 2); ctx.stroke();

          // Snare radius fill
          ctx.fillStyle = iResult.coverage_pct === 100 ? `rgba(255,0,85,${0.025 * pulse})` : `rgba(255,165,0,${0.025 * pulse})`;
          ctx.beginPath(); ctx.arc(ss.x, ss.y, sr, 0, Math.PI * 2); ctx.fill();

          // Animated scanning ring
          ctx.strokeStyle = iResult.coverage_pct === 100 ? `rgba(255,0,85,${0.5 * pulse})` : `rgba(255,165,0,${0.5 * pulse})`;
          ctx.lineWidth = 1.5;
          ctx.setLineDash([8, 4]);
          ctx.lineDashOffset = -t * 25;
          ctx.beginPath(); ctx.arc(ss.x, ss.y, sr, 0, Math.PI * 2); ctx.stroke();
          ctx.setLineDash([]);

          // Snare center crosshair
          ctx.fillStyle = '#FF0055';
          ctx.shadowColor = '#FF0055'; ctx.shadowBlur = 18;
          ctx.beginPath(); ctx.arc(ss.x, ss.y, 4 * zoom, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;

          // Crosshair lines
          ctx.strokeStyle = 'rgba(255,0,85,0.3)';
          ctx.lineWidth = 0.8;
          const chSize = 12 * zoom;
          ctx.beginPath(); ctx.moveTo(ss.x - chSize, ss.y); ctx.lineTo(ss.x - 6 * zoom, ss.y); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(ss.x + 6 * zoom, ss.y); ctx.lineTo(ss.x + chSize, ss.y); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(ss.x, ss.y - chSize); ctx.lineTo(ss.x, ss.y - 6 * zoom); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(ss.x, ss.y + 6 * zoom); ctx.lineTo(ss.x, ss.y + chSize); ctx.stroke();

          // Label
          ctx.fillStyle = `rgba(255,0,85,${0.7 * pulse})`;
          ctx.font = `700 ${Math.max(8, 9 * zoom)}px Rajdhani, sans-serif`;
          ctx.textAlign = 'center';
          ctx.fillText('PRIMARY SNARE', ss.x, ss.y - 14 * zoom);
        }

        // Second snare suggestion
        const ss2 = iResult.second_snare;
        if (ss2?.position) {
          const s2s = toScreen(ss2.position.x, ss2.position.y, w, h, offset, zoom);
          const sr = (iResult.snare_range_map || 25) * zoom;
          const pulse2 = Math.sin(t * 2.5 + 1) * 0.3 + 0.7;
          ctx.fillStyle = `rgba(255,174,0,${0.02 * pulse2})`;
          ctx.beginPath(); ctx.arc(s2s.x, s2s.y, sr, 0, Math.PI * 2); ctx.fill();
          ctx.strokeStyle = `rgba(255,174,0,${0.4 * pulse2})`;
          ctx.lineWidth = 1;
          ctx.setLineDash([4, 6]);
          ctx.lineDashOffset = -t * 15;
          ctx.beginPath(); ctx.arc(s2s.x, s2s.y, sr, 0, Math.PI * 2); ctx.stroke();
          ctx.setLineDash([]);
          ctx.fillStyle = '#FFAE00';
          ctx.shadowColor = '#FFAE00'; ctx.shadowBlur = 10;
          ctx.beginPath(); ctx.arc(s2s.x, s2s.y, 3 * zoom, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;
          ctx.fillStyle = `rgba(255,174,0,${0.6 * pulse2})`;
          ctx.font = `700 ${Math.max(7, 8 * zoom)}px Rajdhani, sans-serif`;
          ctx.textAlign = 'center';
          ctx.fillText('2ND SNARE', s2s.x, s2s.y - 10 * zoom);
        }
      }

      // === ROUTE LINES (animated glow) ===
      if (tab === 'route' && rt?.waypoints) {
        // Draw glow layer first, then sharp line, then animated dash
        rt.waypoints.forEach(wp => {
          if (wp.type === 'refuel') return;
          const fromLoc = locs.find(l => l.id === wp.from_id), toLoc = locs.find(l => l.id === wp.to_id);
          if (!fromLoc || !toLoc) return;
          const sf = toScreen(fromLoc.map_x, fromLoc.map_y, w, h, offset, zoom);
          const st = toScreen(toLoc.map_x, toLoc.map_y, w, h, offset, zoom);
          const isJump = wp.type === 'jump';
          const color = isJump ? '#FF6B35' : '#00D4FF';

          // Wide glow
          ctx.strokeStyle = isJump ? 'rgba(255,107,53,0.08)' : 'rgba(0,212,255,0.08)';
          ctx.lineWidth = 14 * zoom;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();

          // Medium glow
          ctx.strokeStyle = isJump ? 'rgba(255,107,53,0.15)' : 'rgba(0,212,255,0.15)';
          ctx.lineWidth = 6 * zoom;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();

          // Core line
          ctx.strokeStyle = color;
          ctx.lineWidth = 1.8;
          ctx.shadowColor = color; ctx.shadowBlur = 8;
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
          ctx.shadowBlur = 0;

          // Animated dash overlay
          ctx.strokeStyle = isJump ? 'rgba(255,200,150,0.6)' : 'rgba(180,240,255,0.6)';
          ctx.lineWidth = 1.2;
          ctx.setLineDash([3, 12]);
          ctx.lineDashOffset = -t * (isJump ? 30 : 50);
          ctx.beginPath(); ctx.moveTo(sf.x, sf.y); ctx.lineTo(st.x, st.y); ctx.stroke();
          ctx.setLineDash([]);

          // Direction arrow at midpoint
          const angle = Math.atan2(st.y - sf.y, st.x - sf.x);
          const mx = (sf.x + st.x) / 2, my = (sf.y + st.y) / 2;
          ctx.fillStyle = color;
          ctx.shadowColor = color; ctx.shadowBlur = 6;
          ctx.beginPath();
          ctx.moveTo(mx + 8 * Math.cos(angle), my + 8 * Math.sin(angle));
          ctx.lineTo(mx - 6 * Math.cos(angle) - 5 * Math.sin(angle), my - 6 * Math.sin(angle) + 5 * Math.cos(angle));
          ctx.lineTo(mx - 6 * Math.cos(angle) + 5 * Math.sin(angle), my - 6 * Math.sin(angle) - 5 * Math.cos(angle));
          ctx.closePath(); ctx.fill();
          ctx.shadowBlur = 0;
        });

        // Refuel markers
        rt.waypoints.forEach(wp => {
          if (wp.type !== 'refuel') return;
          const loc = locs.find(l => l.id === wp.from_id);
          if (!loc) return;
          const sc = toScreen(loc.map_x, loc.map_y, w, h, offset, zoom);
          const pulse = Math.sin(t * 4) * 0.3 + 0.7;
          // Glow ring
          ctx.strokeStyle = `rgba(255,174,0,${0.4 * pulse})`;
          ctx.lineWidth = 2;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, 12 * zoom, 0, Math.PI * 2); ctx.stroke();
          // Fill
          ctx.fillStyle = '#FFAE00';
          ctx.shadowColor = '#FFAE00'; ctx.shadowBlur = 12;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, 6 * zoom, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;
          // Label
          ctx.fillStyle = '#000';
          ctx.font = `700 ${Math.max(7, 8 * zoom)}px sans-serif`;
          ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.fillText('F', sc.x, sc.y);
          ctx.textBaseline = 'alphabetic';
          ctx.fillStyle = `rgba(255,174,0,${0.7 * pulse})`;
          ctx.font = `700 ${Math.max(7, 8 * zoom)}px Rajdhani, sans-serif`;
          ctx.fillText('REFUEL', sc.x, sc.y + 16 * zoom);
        });
      }

      // === LOCATION NODES ===
      const isInterdict = tab === 'interdiction';
      for (const loc of locs) {
        const sc = toScreen(loc.map_x, loc.map_y, w, h, offset, zoom);
        if (sc.x < -30 || sc.x > w + 30 || sc.y < -30 || sc.y > h + 30) continue;

        const baseR = (NODE_RADIUS[loc.type] || 3) * zoom;
        const color = TYPE_COLORS[loc.type] || '#888';
        const isOriginSel = isInterdict ? iOrigins.includes(loc.id) : loc.id === org;
        const isDestSel = isInterdict ? loc.id === iDest : loc.id === dst;
        const isHov = hov === loc.id;
        const isActive = isOriginSel || isDestSel || isHov;
        const pulse = Math.sin(t * 2 + loc.map_x * 0.1) * 0.15 + 1;
        const r = baseR * (isActive ? pulse * 1.2 : (loc.type === 'planet' ? pulse : 1));

        if (loc.type === 'star') {
          // Multi-layer star glow
          const g3 = ctx.createRadialGradient(sc.x, sc.y, 0, sc.x, sc.y, r * 6);
          g3.addColorStop(0, 'rgba(255,215,0,0.06)');
          g3.addColorStop(1, 'transparent');
          ctx.fillStyle = g3;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r * 6, 0, Math.PI * 2); ctx.fill();

          const g2 = ctx.createRadialGradient(sc.x, sc.y, 0, sc.x, sc.y, r * 3);
          g2.addColorStop(0, 'rgba(255,230,150,0.2)');
          g2.addColorStop(0.5, 'rgba(255,200,50,0.08)');
          g2.addColorStop(1, 'transparent');
          ctx.fillStyle = g2;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r * 3, 0, Math.PI * 2); ctx.fill();

          const g1 = ctx.createRadialGradient(sc.x, sc.y, 0, sc.x, sc.y, r * 1.2);
          g1.addColorStop(0, '#fffbe6');
          g1.addColorStop(0.6, '#FFD700');
          g1.addColorStop(1, 'rgba(255,200,0,0)');
          ctx.fillStyle = g1;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r * 1.2, 0, Math.PI * 2); ctx.fill();

          // Bright center
          ctx.fillStyle = '#fff';
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r * 0.3, 0, Math.PI * 2); ctx.fill();

        } else if (loc.type === 'gateway') {
          // Diamond shape with glow
          ctx.shadowColor = color; ctx.shadowBlur = isActive ? 16 : 8;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.moveTo(sc.x, sc.y - r * 1.3); ctx.lineTo(sc.x + r, sc.y);
          ctx.lineTo(sc.x, sc.y + r * 1.3); ctx.lineTo(sc.x - r, sc.y);
          ctx.closePath(); ctx.fill();
          ctx.shadowBlur = 0;

        } else if (loc.type === 'planet') {
          // Planet with atmospheric glow
          const atmo = ctx.createRadialGradient(sc.x, sc.y, r * 0.6, sc.x, sc.y, r * 2.5);
          atmo.addColorStop(0, `${color}15`);
          atmo.addColorStop(1, 'transparent');
          ctx.fillStyle = atmo;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r * 2.5, 0, Math.PI * 2); ctx.fill();

          // Body
          ctx.shadowColor = color; ctx.shadowBlur = isActive ? 18 : 10;
          const bodyGrad = ctx.createRadialGradient(sc.x - r * 0.3, sc.y - r * 0.3, 0, sc.x, sc.y, r);
          bodyGrad.addColorStop(0, '#ffffff40');
          bodyGrad.addColorStop(0.5, color);
          bodyGrad.addColorStop(1, `${color}80`);
          ctx.fillStyle = bodyGrad;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;

        } else if (loc.type === 'city') {
          // City - bright dot with ring
          ctx.shadowColor = color; ctx.shadowBlur = isActive ? 14 : 6;
          ctx.fillStyle = color;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;
          ctx.strokeStyle = `${color}60`;
          ctx.lineWidth = 0.8;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r + 3 * zoom, 0, Math.PI * 2); ctx.stroke();

        } else {
          // Stations, moons, rest stops, outposts
          ctx.shadowColor = color; ctx.shadowBlur = isActive ? 12 : 4;
          ctx.fillStyle = color;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r, 0, Math.PI * 2); ctx.fill();
          ctx.shadowBlur = 0;
        }

        // Selection rings for origin / destination
        if (isOriginSel || isDestSel) {
          const ringColor = isOriginSel ? '#00FF9D' : '#FF0055';
          const ringPulse = Math.sin(t * 3) * 0.3 + 0.7;
          ctx.strokeStyle = ringColor;
          ctx.globalAlpha = ringPulse;
          ctx.lineWidth = 1.5;
          ctx.setLineDash([4, 4]);
          ctx.lineDashOffset = -t * 20;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r + 8 * zoom, 0, Math.PI * 2); ctx.stroke();
          ctx.setLineDash([]);
          // Outer glow ring
          ctx.strokeStyle = `${ringColor}30`;
          ctx.lineWidth = 4;
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r + 12 * zoom, 0, Math.PI * 2); ctx.stroke();
          ctx.globalAlpha = 1;
        }

        // Hover highlight
        if (isHov && !isOriginSel && !isDestSel) {
          ctx.strokeStyle = `${color}80`;
          ctx.lineWidth = 1;
          ctx.setLineDash([3, 3]);
          ctx.beginPath(); ctx.arc(sc.x, sc.y, r + 6 * zoom, 0, Math.PI * 2); ctx.stroke();
          ctx.setLineDash([]);
        }

        // === LABELS ===
        const minZ = LABEL_MIN_ZOOM[loc.type] ?? 0.9;
        const showLabel = zoom >= minZ || isActive;
        if (showLabel) {
          const labelAlpha = isActive ? 1 : Math.min(1, (zoom - minZ) / 0.3 + 0.3);
          const fontSize = loc.type === 'star' ? Math.max(10, 13 * zoom)
            : loc.type === 'planet' ? Math.max(9, 11 * zoom)
            : loc.type === 'city' ? Math.max(8, 10 * zoom)
            : Math.max(7, 8 * zoom);
          const weight = (loc.type === 'planet' || loc.type === 'star' || loc.type === 'city') ? '600' : '400';
          ctx.font = `${weight} ${fontSize}px Rajdhani, sans-serif`;
          ctx.textAlign = 'center';

          const labelY = sc.y + r + 10 * zoom;
          const labelColor = isOriginSel ? '#00FF9D' : isDestSel ? '#FF0055' : isHov ? '#ffffff' : color;

          // Label background for readability
          if (isActive || loc.type === 'planet' || loc.type === 'star') {
            const metrics = ctx.measureText(loc.name);
            const tw = metrics.width;
            ctx.fillStyle = 'rgba(2,3,6,0.7)';
            ctx.fillRect(sc.x - tw / 2 - 3, labelY - fontSize + 2, tw + 6, fontSize + 2);
          }

          ctx.globalAlpha = labelAlpha;
          ctx.fillStyle = labelColor;
          ctx.fillText(loc.name, sc.x, labelY);
          ctx.globalAlpha = 1;
        }
      }

      // === HUD SCAN LINE ===
      const scanY = (t * 40) % h;
      const scanGrad = ctx.createLinearGradient(0, scanY - 30, 0, scanY + 30);
      scanGrad.addColorStop(0, 'transparent');
      scanGrad.addColorStop(0.5, 'rgba(0,212,255,0.015)');
      scanGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = scanGrad;
      ctx.fillRect(0, scanY - 30, w, 60);

      // === HUD CORNER BRACKETS ===
      ctx.strokeStyle = 'rgba(0,212,255,0.08)';
      ctx.lineWidth = 1;
      const cs = 20;
      [[0, 0, cs, 0, 0, cs], [w, 0, -cs, 0, 0, cs], [0, h, cs, 0, 0, -cs], [w, h, -cs, 0, 0, -cs]].forEach(([x, y, dx1, dy1, dx2, dy2]) => {
        ctx.beginPath(); ctx.moveTo(x + dx1, y + dy1); ctx.lineTo(x, y); ctx.lineTo(x + dx2, y + dy2); ctx.stroke();
      });

      animRef.current = requestAnimationFrame(draw);
    };

    animRef.current = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(animRef.current);
      observer.disconnect();
      window.removeEventListener('resize', resize);
    };
  }, [loading]);

  // === INTERACTION HANDLERS ===
  const handleWheel = (e) => { e.preventDefault(); setMapZoom(z => Math.max(0.25, Math.min(4, z + (e.deltaY > 0 ? -0.12 : 0.12)))); };
  const handleMouseDown = (e) => { if (e.button === 0) { setDragging(true); setDragStart({ x: e.clientX - mapOffset.x, y: e.clientY - mapOffset.y }); } };
  const handleMouseMove = (e) => {
    const canvas = canvasRef.current; if (!canvas) return;
    if (dragging) { setMapOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y }); return; }
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width, scaleY = canvas.height / rect.height;
    const mx = (e.clientX - rect.left) * scaleX, my = (e.clientY - rect.top) * scaleY;
    const w = canvas.width, h = canvas.height;
    let found = null;
    for (const loc of locations) {
      const sx = w / 2 + loc.map_x * mapZoom + mapOffset.x, sy = h / 2 + loc.map_y * mapZoom + mapOffset.y;
      if (Math.sqrt((mx - sx) ** 2 + (my - sy) ** 2) < 18 * mapZoom) { found = loc.id; break; }
    }
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

  const LocationSelect = ({ value, onChange, label, color, testId }) => (
    <div>
      <label className="text-[10px] font-bold uppercase tracking-widest block mb-1" style={{ color }}>{label}</label>
      <select value={value} onChange={e => onChange(e.target.value)} data-testid={testId}
        className="w-full px-3 py-2 bg-[#060a12] border rounded text-white text-xs focus:outline-none transition-all"
        style={{ borderColor: `${color}30`, colorScheme: 'dark' }}>
        <option value="" className="bg-[#060a12] text-gray-500">Select location...</option>
        {Object.entries(systems).map(([sysId, sys]) => (
          <optgroup key={sysId} label={sys.name} className="bg-[#060a12] text-gray-300">
            {locations.filter(l => l.system === sysId && l.type !== 'star').map(l => (
              <option key={l.id} value={l.id} className="bg-[#060a12] text-white">{l.name}</option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><div className="w-16 h-16 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" /></div>;

  return (
    <div className="h-[calc(100vh-80px)] flex gap-3" data-testid="route-planner-page">
      {/* Left Panel */}
      <div className="w-[310px] shrink-0 flex flex-col overflow-hidden">
        <div className="mb-3">
          <div className="flex items-center gap-2">
            <div className="w-1 h-8 bg-cyan-500 rounded-full" />
            <div>
              <h1 className="text-xl font-bold uppercase tracking-wider" style={{ fontFamily: 'Rajdhani, monospace', color: '#00D4FF' }}>ROUTE PLANNER</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-mono">Stanton // Pyro // Nyx</p>
            </div>
          </div>
        </div>

        <div className="flex gap-1 mb-3" data-testid="planner-tabs">
          {TABS.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} data-testid={`tab-${tab.id}`}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-[10px] font-bold uppercase tracking-wider transition-all border-b-2 ${activeTab === tab.id ? 'text-white border-cyan-500 bg-cyan-500/5' : 'text-gray-600 border-transparent hover:text-gray-400 hover:border-gray-700'}`}>
              <tab.icon className="w-3 h-3" /> {tab.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 custom-scrollbar">
          {activeTab === 'route' && (<>
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
                  {useFleet && fleetShips.length === 0 ? 'No ships in fleet — toggle to All Ships' : `Select a ship... (${ships.length})`}
                </option>
                {ships.map(s => (
                  <option key={s.id} value={s.id} className="bg-[#060a12] text-white">
                    {s.name} ({s.quantum?.speed_kms ? `${Math.round(s.quantum.speed_kms / 1000)}k km/s` : `QD S${s.hardpoints?.quantum_drive?.size || '?'}`})
                  </option>
                ))}
              </select>
              {selectedShip && (
                <div className="mt-2 grid grid-cols-3 gap-1">
                  {[
                    { label: 'Speed', value: selectedShip.quantum?.speed_kms ? `${Math.round(selectedShip.quantum.speed_kms / 1000)}k` : `S${qdSize}`, color: 'text-cyan-400' },
                    { label: 'Range', value: selectedShip.quantum?.range_mkm ? `${Math.round(selectedShip.quantum.range_mkm)}` : '--', unit: 'Mkm', color: 'text-yellow-400' },
                    { label: 'Fuel', value: selectedShip.quantum?.fuel_capacity || '--', color: 'text-orange-400' },
                  ].map(stat => (
                    <div key={stat.label} className="bg-white/3 rounded px-2 py-1 text-center">
                      <div className="text-[9px] text-gray-600 uppercase">{stat.label}</div>
                      <div className={`text-xs font-bold ${stat.color} font-mono`}>{stat.value}{stat.unit && <span className="text-[8px] text-gray-600"> {stat.unit}</span>}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

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

          {activeTab === 'interdiction' && (<>
            <div className="hud-panel p-3 space-y-3" data-testid="interdiction-panel">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-[10px] text-red-400 font-bold uppercase tracking-widest">
                  <Target className="w-3.5 h-3.5" /> QED Snare Planning
                </div>
                {(interdictOrigins.length > 0 || interdictDest) && (
                  <button onClick={clearInterdiction} data-testid="clear-interdiction" className="flex items-center gap-1 text-[9px] text-gray-600 hover:text-red-400 transition-colors uppercase tracking-wider">
                    <Trash2 className="w-3 h-3" /> Clear
                  </button>
                )}
              </div>

              <LocationSelect value={interdictDest} onChange={v => { setInterdictDest(v); setInterdictResult(null); }} label="Target Destination" color="#FF0055" testId="interdict-dest" />

              {/* QD Size selectors */}
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[9px] font-bold text-cyan-400 uppercase tracking-widest block mb-1">Your QD</label>
                  <div className="flex gap-1">
                    {[1, 2, 3].map(s => (
                      <button key={s} onClick={() => { setInterdictYourQd(s); setInterdictResult(null); }} data-testid={`interdict-your-qd-${s}`}
                        className={`flex-1 py-1 rounded text-[10px] font-bold font-mono transition-all ${interdictYourQd === s ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30' : 'bg-white/3 text-gray-600 border border-white/5'}`}>S{s}</button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-[9px] font-bold text-red-400 uppercase tracking-widest block mb-1">Target QD</label>
                  <div className="flex gap-1">
                    {[1, 2, 3].map(s => (
                      <button key={s} onClick={() => { setInterdictTargetQd(s); setInterdictResult(null); }} data-testid={`interdict-target-qd-${s}`}
                        className={`flex-1 py-1 rounded text-[10px] font-bold font-mono transition-all ${interdictTargetQd === s ? 'bg-red-500/15 text-red-400 border border-red-500/30' : 'bg-white/3 text-gray-600 border border-white/5'}`}>S{s}</button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Origins with presets */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-[10px] font-bold text-green-400 uppercase tracking-widest">Origins ({interdictOrigins.length})</label>
                </div>
                {/* Quick-add presets */}
                <div className="flex flex-wrap gap-1 mb-2" data-testid="origin-presets">
                  {[
                    { label: 'Cities', type: 'city', icon: MapPin },
                    { label: 'Stations', type: 'station', icon: Radio },
                    { label: 'R&R Stops', type: 'rest_stop', icon: Shield },
                  ].map(preset => (
                    <button key={preset.type} onClick={() => addOriginsByType(preset.type)} data-testid={`preset-${preset.type}`}
                      className="flex items-center gap-1 px-2 py-1 bg-green-500/8 border border-green-500/15 rounded text-[9px] text-green-400 hover:bg-green-500/15 transition-colors font-bold uppercase">
                      <preset.icon className="w-2.5 h-2.5" /> +{preset.label}
                    </button>
                  ))}
                </div>
                {interdictOrigins.length > 0 && (
                  <div className="space-y-0.5 mb-2 max-h-[100px] overflow-y-auto custom-scrollbar">
                    {interdictOrigins.map(oid => (
                      <div key={oid} className="flex items-center justify-between px-2 py-0.5 bg-green-500/5 border border-green-500/10 rounded text-[9px]">
                        <span className="text-green-400 font-mono truncate">{locName(oid)}</span>
                        <button onClick={() => removeInterdictOrigin(oid)} className="text-gray-700 hover:text-red-400 shrink-0 ml-1"><X className="w-2.5 h-2.5" /></button>
                      </div>
                    ))}
                  </div>
                )}
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
                {interdicting ? 'ANALYZING...' : 'ANALYZE INTERDICTION'}
              </button>
            </div>
            {interdictResult && <InterdictionResults result={interdictResult} formatTime={formatTime} qdSpeeds={qdSpeeds} />}
          </>)}

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

          <div className="hud-panel p-2.5" data-testid="map-legend">
            <h4 className="text-[9px] font-bold text-gray-600 uppercase tracking-widest mb-1.5">Legend</h4>
            <div className="grid grid-cols-2 gap-0.5 text-[9px]">
              {Object.entries(TYPE_COLORS).map(([type, color]) => (
                <div key={type} className="flex items-center gap-1.5 py-0.5">
                  <div className="w-2 h-2 rounded-full shrink-0" style={{ background: color, boxShadow: `0 0 4px ${color}` }} />
                  <span className="text-gray-500 capitalize" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{type.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Star Map Canvas */}
      <div className="flex-1 rounded-lg overflow-hidden relative border border-white/[0.04] bg-[#020306]" data-testid="star-map">
        <canvas ref={canvasRef}
          onWheel={handleWheel} onMouseDown={handleMouseDown} onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp} onClick={handleCanvasClick}
          className="w-full h-full" />
        {/* HUD overlay text */}
        <div className="absolute top-3 left-3 pointer-events-none">
          <div className="text-[9px] uppercase tracking-[3px] font-mono" style={{ color: 'rgba(0,212,255,0.25)' }}>mobi-glass // nav-sys v4.6</div>
          <div className="text-[8px] uppercase tracking-[2px] font-mono mt-0.5" style={{ color: 'rgba(0,212,255,0.12)' }}>quantum navigation active</div>
        </div>
        <div className="absolute top-3 right-3 flex items-center gap-2">
          <div className="text-[9px] text-gray-600 font-mono mr-2">{Math.round(mapZoom * 100)}%</div>
          <button onClick={() => { setMapOffset({ x: 0, y: 0 }); setMapZoom(1); }} data-testid="reset-map"
            className="p-1.5 bg-black/50 backdrop-blur-sm border border-white/[0.06] rounded text-gray-500 hover:text-cyan-400 transition-colors">
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
        {hoveredLoc && (
          <div className="absolute bottom-3 left-3 bg-[#020306]/90 backdrop-blur-md border border-cyan-500/15 rounded-lg px-3 py-2 pointer-events-none">
            <div className="text-sm font-bold text-white" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{locName(hoveredLoc)}</div>
            <div className="text-[9px] text-gray-500 capitalize" style={{ fontFamily: 'Rajdhani, sans-serif' }}>{locations.find(l => l.id === hoveredLoc)?.type?.replace('_', ' ')} &mdash; {locations.find(l => l.id === hoveredLoc)?.system}</div>
          </div>
        )}
        <div className="absolute bottom-3 right-3 text-[8px] text-gray-700 font-mono pointer-events-none">
          drag to pan &middot; scroll to zoom &middot; click to select
        </div>
      </div>
    </div>
  );
};

// === SUB COMPONENTS ===

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
            {wp.type !== 'refuel' && <div className="text-gray-600 font-mono">{wp.distance_mkm} Mkm {wp.type === 'jump' ? '// JUMP' : ''}</div>}
          </div>
          {wp.type !== 'refuel' && wp.fuel_remaining_pct !== undefined && (
            <div className="text-[8px] text-gray-600 shrink-0 font-mono">{wp.fuel_remaining_pct}%</div>
          )}
        </div>
      ))}
    </div>
  </motion.div>
);

const InterdictionResults = ({ result, formatTime, qdSpeeds }) => (
  <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-2.5" data-testid="interdiction-results">
    {/* Coverage Summary */}
    <div className="hud-panel p-3 space-y-2">
      <div className="flex items-center gap-2">
        {result.coverage_pct === 100 ? <CheckCircle className="w-4 h-4 text-green-400" /> : <AlertTriangle className="w-4 h-4 text-yellow-400" />}
        <span className={`text-[10px] font-bold uppercase tracking-wider ${result.coverage_pct === 100 ? 'text-green-400' : 'text-yellow-400'}`}>{result.message}</span>
      </div>
      <div className="grid grid-cols-3 gap-1.5">
        <div className="bg-white/3 rounded p-1.5 text-center">
          <div className={`text-lg font-bold font-mono ${result.coverage_pct === 100 ? 'text-green-400' : 'text-yellow-400'}`}>{result.coverage_pct}%</div>
          <div className="text-[8px] text-gray-600 uppercase">Coverage</div>
        </div>
        <div className="bg-white/3 rounded p-1.5 text-center">
          <div className="text-lg font-bold text-red-400 font-mono">{result.routes_covered}/{result.routes_total}</div>
          <div className="text-[8px] text-gray-600 uppercase">Routes</div>
        </div>
        <div className="bg-white/3 rounded p-1.5 text-center">
          <div className="text-lg font-bold text-cyan-400 font-mono">{result.distance_to_dest_mkm}</div>
          <div className="text-[8px] text-gray-600 uppercase">Mkm to dest</div>
        </div>
      </div>
    </div>

    {/* Per-route breakdown */}
    {result.route_details?.length > 0 && (
      <div className="hud-panel p-3" data-testid="route-breakdown">
        <h4 className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-2">Route Breakdown</h4>
        <div className="space-y-1 max-h-[140px] overflow-y-auto custom-scrollbar">
          {result.route_details.map((rd, i) => (
            <div key={i} data-testid={`interdict-route-${i}`}
              className={`flex items-center gap-1.5 p-1.5 rounded text-[9px] ${rd.covered ? 'bg-green-500/5 border border-green-500/10' : 'bg-red-500/5 border border-red-500/10'}`}>
              <div className={`w-3.5 h-3.5 rounded-full flex items-center justify-center text-[7px] font-bold shrink-0 ${rd.covered ? 'bg-green-500/25 text-green-400' : 'bg-red-500/25 text-red-400'}`}>
                {rd.covered ? '\u2713' : '\u2717'}
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-white font-mono truncate">{rd.origin_name}</div>
                <div className="text-gray-600 font-mono">{rd.distance_mkm} Mkm &middot; {formatTime(rd.target_travel_time_s)}</div>
              </div>
              <div className="text-[8px] text-gray-500 font-mono shrink-0">
                {rd.covered ? `~${formatTime(rd.time_to_snare_s)}` : `${rd.deviation_mkm}Mkm off`}
              </div>
            </div>
          ))}
        </div>
      </div>
    )}

    {/* Arrival Timeline */}
    {result.timing && result.timing.arrival_times?.length > 0 && (
      <div className="hud-panel p-3" data-testid="arrival-timeline">
        <h4 className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-1.5">Arrival Timeline</h4>
        <div className="text-[9px] text-gray-400 mb-2 font-mono">{result.timing.note}</div>
        {/* Mini timeline bar */}
        <div className="relative h-3 bg-white/3 rounded-full overflow-hidden mb-1">
          {result.timing.arrival_times.map((at, i) => {
            const maxT = Math.max(...result.timing.arrival_times, 1);
            const pct = (at / maxT) * 100;
            return <div key={i} className="absolute top-0 bottom-0 w-1 rounded-full bg-red-400" style={{ left: `${Math.min(pct, 98)}%` }} title={`${formatTime(at)}`} />;
          })}
        </div>
        <div className="flex justify-between text-[8px] text-gray-600 font-mono">
          <span>0s</span>
          <span>{formatTime(Math.max(...result.timing.arrival_times))}</span>
        </div>
      </div>
    )}

    {/* Escape Analysis */}
    {result.escape_analysis && (
      <div className="hud-panel p-3" data-testid="escape-analysis">
        <h4 className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-1.5">Escape Analysis</h4>
        <div className="flex items-center gap-2 mb-1.5">
          {result.escape_analysis.can_escape
            ? <AlertTriangle className="w-3 h-3 text-yellow-400 shrink-0" />
            : <Shield className="w-3 h-3 text-green-400 shrink-0" />}
          <span className={`text-[9px] font-bold ${result.escape_analysis.can_escape ? 'text-yellow-400' : 'text-green-400'}`}>
            {result.escape_analysis.can_escape ? 'Target may escape' : 'You have speed advantage'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-1 mb-1.5">
          <div className="bg-white/3 rounded px-2 py-1">
            <div className="text-[8px] text-gray-600">Your QD</div>
            <div className="text-[10px] text-cyan-400 font-bold font-mono">{result.escape_analysis.your_speed_kms?.toLocaleString()} km/s</div>
          </div>
          <div className="bg-white/3 rounded px-2 py-1">
            <div className="text-[8px] text-gray-600">Target QD</div>
            <div className="text-[10px] text-red-400 font-bold font-mono">{result.escape_analysis.target_speed_kms?.toLocaleString()} km/s</div>
          </div>
        </div>
        <div className="text-[9px] text-gray-500">{result.escape_analysis.note}</div>
      </div>
    )}

    {/* Tactical Notes */}
    {result.tactical_notes?.length > 0 && (
      <div className="hud-panel p-3" data-testid="tactical-notes">
        <h4 className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
          <Eye className="w-3 h-3" /> Tactical Intel
        </h4>
        <div className="space-y-1.5">
          {result.tactical_notes.map((note, i) => (
            <div key={i} className="flex gap-2 text-[9px] text-gray-300 leading-relaxed">
              <span className="text-red-400 shrink-0 mt-0.5">&bull;</span>
              <span>{note}</span>
            </div>
          ))}
        </div>
      </div>
    )}

    {/* Nearby POIs */}
    {result.nearby_pois?.length > 0 && (
      <div className="hud-panel p-3" data-testid="nearby-pois">
        <h4 className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-1.5">Nearby Locations</h4>
        <div className="space-y-0.5">
          {result.nearby_pois.slice(0, 4).map((poi, i) => (
            <div key={i} className="flex items-center justify-between text-[9px]">
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: TYPE_COLORS[poi.type] || '#888' }} />
                <span className="text-gray-400 font-mono">{poi.name}</span>
              </div>
              <span className="text-gray-600 font-mono">{poi.distance_mkm} Mkm</span>
            </div>
          ))}
        </div>
      </div>
    )}

    {/* Second Snare Suggestion */}
    {result.second_snare && (
      <div className="hud-panel p-3 border-yellow-500/20" data-testid="second-snare">
        <div className="flex items-center gap-2 text-[9px] text-yellow-400 font-bold uppercase tracking-widest mb-1.5">
          <Plus className="w-3 h-3" /> Second Snare Suggested
        </div>
        <div className="text-[9px] text-gray-400">
          Deploy a second QED snare to cover {result.second_snare.covers} uncovered route{result.second_snare.covers > 1 ? 's' : ''} out of {result.second_snare.total_uncovered}.
        </div>
      </div>
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
      <div className="bg-white/3 rounded p-1.5"><div className="text-gray-600 font-mono">Your QD</div><div className="text-cyan-400 font-bold font-mono">{result.your_speed_kms?.toLocaleString()} km/s</div></div>
      <div className="bg-white/3 rounded p-1.5"><div className="text-gray-600 font-mono">Target QD</div><div className="text-red-400 font-bold font-mono">{result.target_speed_kms?.toLocaleString()} km/s</div></div>
    </div>
    {result.can_catch && (
      <div className="grid grid-cols-2 gap-1.5 text-[10px]">
        <div className="bg-white/3 rounded p-1.5"><div className="text-gray-600 font-mono">Closing</div><div className="text-yellow-400 font-bold font-mono">{formatTime(result.closing_time_seconds)}</div></div>
        <div className="bg-white/3 rounded p-1.5"><div className="text-gray-600 font-mono">Total</div><div className="text-yellow-400 font-bold font-mono">{formatTime(result.total_time_seconds)}</div></div>
      </div>
    )}
  </motion.div>
);

export default RoutePlanner;
