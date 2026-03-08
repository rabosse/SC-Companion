import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Box, Search, Zap, Shield, Cpu, MapPin, DollarSign, SlidersHorizontal, ArrowUpDown, ChevronUp, ChevronDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const GRADE_COLORS = { A: '#00FF9D', B: '#00D4FF', C: '#FFAE00', D: '#FF6B6B' };
const CLASS_COLORS = { Military: '#FF6B6B', Civilian: '#00D4FF', Industrial: '#FFAE00', Stealth: '#A855F7', Competition: '#00FF9D' };

const Components = () => {
  const { API } = useAuth();
  const [components, setComponents] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedSize, setSelectedSize] = useState('all');
  const [selectedGrade, setSelectedGrade] = useState('all');
  const [selectedClass, setSelectedClass] = useState('all');
  const [availability, setAvailability] = useState('all');
  const [sortBy, setSortBy] = useState('grade');
  const [sortAsc, setSortAsc] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const response = await axios.get(`${API}/components`);
        setComponents(response.data.data || []);
      } catch {
        toast.error('Failed to load components');
      } finally {
        setLoading(false);
      }
    };
    fetchComponents();
  }, [API]);

  const types = useMemo(() => ['all', ...new Set(components.map(c => c.type))], [components]);
  const sizes = useMemo(() => ['all', ...new Set(components.map(c => c.size).filter(Boolean).sort((a, b) => Number(a) - Number(b)))], [components]);
  const grades = useMemo(() => ['all', ...new Set(components.map(c => c.grade).filter(Boolean).sort())], [components]);
  const classes = useMemo(() => {
    const unique = new Set(components.map(c => c.item_class).filter(Boolean));
    return ['all', ...Array.from(unique).sort()];
  }, [components]);

  const filtered = useMemo(() => {
    let result = components;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(c => c.name.toLowerCase().includes(q) || (c.manufacturer || '').toLowerCase().includes(q));
    }
    if (selectedType !== 'all') result = result.filter(c => c.type === selectedType);
    if (selectedSize !== 'all') result = result.filter(c => c.size === selectedSize);
    if (selectedGrade !== 'all') result = result.filter(c => c.grade === selectedGrade);
    if (selectedClass !== 'all') result = result.filter(c => c.item_class === selectedClass);
    if (availability === 'purchasable') result = result.filter(c => c.sold);
    if (availability === 'unknown') result = result.filter(c => !c.sold);

    const dir = sortAsc ? 1 : -1;
    const sortFns = {
      grade: (a, b) => dir * (a.grade || 'Z').localeCompare(b.grade || 'Z'),
      class: (a, b) => dir * (a.item_class || '').localeCompare(b.item_class || ''),
      name: (a, b) => dir * (a.name || '').localeCompare(b.name || ''),
      output: (a, b) => dir * ((a.output || 0) - (b.output || 0)),
      size: (a, b) => dir * (Number(a.size || 0) - Number(b.size || 0)),
    };
    if (sortFns[sortBy]) result = [...result].sort(sortFns[sortBy]);
    return result;
  }, [components, searchQuery, selectedType, selectedSize, selectedGrade, selectedClass, availability, sortBy, sortAsc]);

  const getTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'shield': return Shield;
      case 'power': return Zap;
      case 'quantum': case 'cooler': return Cpu;
      default: return Box;
    }
  };

  const getTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'shield': return '#00D4FF';
      case 'power': return '#FFAE00';
      case 'quantum': return '#D4AF37';
      case 'cooler': return '#00FF9D';
      case 'radar': return '#FF6B6B';
      default: return '#FFFFFF';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]" data-testid="loading-indicator">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading components...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="components-page">
      {/* Header */}
      <div>
        <h1 className="text-4xl sm:text-5xl font-bold mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
          Component Catalog
        </h1>
        <p className="text-gray-400 text-sm" data-testid="component-count">
          {filtered.length} components found
        </p>
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-2xl p-5 space-y-4" data-testid="filters-section">
        <div className="flex items-center gap-2 text-sm font-bold text-gray-400 uppercase tracking-wider">
          <SlidersHorizontal className="w-4 h-4" /> Filters
        </div>

        {/* Search + Dropdowns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div className="relative sm:col-span-2 lg:col-span-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search components..." data-testid="search-input"
              className="w-full pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all" />
          </div>
          <FilterSelect value={selectedType} onChange={setSelectedType} options={types} label="All Types" testId="type-filter" />
          <FilterSelect value={selectedSize} onChange={setSelectedSize} options={sizes} label="All Sizes" prefix="Size " testId="size-filter" />
          <FilterSelect value={selectedGrade} onChange={setSelectedGrade} options={grades} label="All Grades" prefix="Grade " testId="grade-filter" />
          <FilterSelect value={selectedClass} onChange={setSelectedClass} options={classes} label="All Classes" testId="class-filter" />
        </div>

        {/* Availability + Sort */}
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          <div className="flex items-center gap-2">
            {['all', 'purchasable', 'unknown'].map(opt => (
              <button key={opt} onClick={() => setAvailability(opt)} data-testid={`avail-${opt}`}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${availability === opt ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-white/5 text-gray-500 border border-white/5 hover:text-gray-300'}`}>
                {opt.charAt(0).toUpperCase() + opt.slice(1)}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 font-semibold uppercase">Sort:</span>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} data-testid="sort-dropdown"
              className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-white font-semibold focus:outline-none focus:border-cyan-500 transition-all">
              <option value="grade" className="bg-gray-900">Grade</option>
              <option value="class" className="bg-gray-900">Class</option>
              <option value="name" className="bg-gray-900">Name</option>
              <option value="output" className="bg-gray-900">Output</option>
              <option value="size" className="bg-gray-900">Size</option>
            </select>
            <button onClick={() => setSortAsc(!sortAsc)} data-testid="sort-direction-toggle"
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/5 border border-white/10 text-gray-400 hover:text-white transition-all"
              title={sortAsc ? 'Ascending' : 'Descending'}>
              <ArrowUpDown className="w-3.5 h-3.5" />
              {sortAsc ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              <span>{sortAsc ? 'ASC' : 'DESC'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Components Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((component, index) => {
          const Icon = getTypeIcon(component.type);
          const typeColor = getTypeColor(component.type);
          const gradeColor = GRADE_COLORS[component.grade] || '#888';
          const classification = component.item_class || '';
          const classColor = CLASS_COLORS[classification] || '#888';

          return (
            <motion.div key={component.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(index * 0.02, 0.5) }}
              className="glass-panel rounded-2xl p-5 hover:scale-[1.02] transition-transform duration-300"
              data-testid={`component-card-${component.id}`}>
              {/* Top row: icon + badges */}
              <div className="flex items-center justify-between mb-3">
                <Icon className="w-7 h-7" style={{ color: typeColor }} />
                <div className="flex items-center gap-1.5">
                  <span className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border"
                    style={{ color: gradeColor, borderColor: `${gradeColor}40`, background: `${gradeColor}15` }}>
                    {component.grade}
                  </span>
                  <span className="text-xs font-bold px-2 py-0.5 rounded border"
                    style={{ color: typeColor, borderColor: `${typeColor}30`, background: `${typeColor}10` }}>
                    S{component.size}
                  </span>
                </div>
              </div>

              {/* Name + Manufacturer */}
              <h3 className="text-base font-bold text-white mb-0.5" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                {component.name}
              </h3>
              <p className="text-xs text-gray-500 mb-3">{component.manufacturer}</p>

              {/* Tags */}
              <div className="flex flex-wrap items-center gap-1.5 mb-3">
                {classification && (
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{ color: classColor, background: `${classColor}15` }}>
                    {classification}
                  </span>
                )}
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{ color: gradeColor, background: `${gradeColor}15` }}>
                  Grade {component.grade}
                </span>
              </div>

              {/* Stats */}
              <div className="text-sm space-y-1.5 mb-3">
                {component.output > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">{component.type === 'Shield' ? 'Max Shield HP' : component.type === 'Power' ? 'Power Gen' : component.type === 'Cooler' ? 'Cooling Rate' : 'Output'}</span>
                    <span className="text-white font-semibold font-mono">{typeof component.output === 'number' ? component.output.toLocaleString() : component.output}</span>
                  </div>
                )}
                {component.rate > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">{component.type === 'Shield' ? 'Regen Rate' : 'Rate'}</span>
                    <span className="text-white font-semibold font-mono">{typeof component.rate === 'number' ? component.rate.toLocaleString() : component.rate}</span>
                  </div>
                )}
                {component.speed > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">QT Speed</span>
                    <span className="text-white font-semibold font-mono">{typeof component.speed === 'number' ? component.speed.toLocaleString() : component.speed} m/s</span>
                  </div>
                )}
                {component.durability > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Durability</span>
                    <span className="text-white font-semibold font-mono">{typeof component.durability === 'number' ? component.durability.toLocaleString() : component.durability} HP</span>
                  </div>
                )}
                {component.fuel_requirement > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Fuel Req</span>
                    <span className="text-white font-semibold font-mono">{component.fuel_requirement}</span>
                  </div>
                )}
              </div>

              {/* Sold indicator */}
              <div className="border-t border-white/10 pt-3 space-y-1.5">
                <div className="flex items-center gap-2 text-xs" data-testid={`component-sold-${component.id}`}>
                  <DollarSign className={`w-3.5 h-3.5 shrink-0 ${component.sold ? 'text-green-400' : 'text-gray-600'}`} />
                  <span className={component.sold ? 'text-green-400 font-medium' : 'text-gray-600'}>
                    {component.sold ? 'Available in-game' : 'Not sold in-game'}
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12" data-testid="no-components-message">
          <Box className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No components found matching your criteria</p>
        </div>
      )}
    </div>
  );
};

const FilterSelect = ({ value, onChange, options, label, prefix = '', testId }) => (
  <select value={value} onChange={e => onChange(e.target.value)} data-testid={testId}
    className="px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500 transition-all">
    {options.map(opt => (
      <option key={opt} value={opt} className="bg-gray-900">
        {opt === 'all' ? label : `${prefix}${opt}`}
      </option>
    ))}
  </select>
);

export default Components;
