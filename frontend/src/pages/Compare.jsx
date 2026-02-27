import { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Ship, X, Plus, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';

const Compare = () => {
  const { API } = useAuth();
  const [ships, setShips] = useState([]);
  const [compareList, setCompareList] = useState([]);
  const [showSelector, setShowSelector] = useState(false);

  useEffect(() => {
    fetchShips();
    const saved = localStorage.getItem('compareShips');
    if (saved) {
      setCompareList(JSON.parse(saved));
    }
  }, []);

  const fetchShips = async () => {
    try {
      const response = await axios.get(`${API}/ships`);
      setShips(response.data.data || []);
    } catch (error) {
      toast.error('Failed to load ships');
    }
  };

  const addToCompare = (ship) => {
    if (compareList.length >= 3) {
      toast.error('Maximum 3 ships can be compared');
      return;
    }
    if (compareList.find(s => s.id === ship.id)) {
      toast.error('Ship already in comparison');
      return;
    }
    const newList = [...compareList, ship];
    setCompareList(newList);
    localStorage.setItem('compareShips', JSON.stringify(newList));
    setShowSelector(false);
    toast.success(`${ship.name} added to comparison`);
  };

  const removeFromCompare = (shipId) => {
    const newList = compareList.filter(s => s.id !== shipId);
    setCompareList(newList);
    localStorage.setItem('compareShips', JSON.stringify(newList));
  };

  const specs = [
    { key: 'manufacturer', label: 'Manufacturer' },
    { key: 'size', label: 'Size' },
    { key: 'role', label: 'Role' },
    { key: 'crew', label: 'Crew' },
    { key: 'cargo', label: 'Cargo (SCU)' },
    { key: 'length', label: 'Length (m)' },
    { key: 'beam', label: 'Beam (m)' },
    { key: 'height', label: 'Height (m)' },
    { key: 'mass', label: 'Mass (kg)' },
    { key: 'max_speed', label: 'Max Speed (m/s)' },
    { key: 'price', label: 'Price (UEC)' },
  ];

  return (
    <div className="space-y-8" data-testid="compare-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-5xl font-bold mb-4 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Ship Comparison
          </h1>
          <p className="text-gray-400">Compare up to 3 ships side by side</p>
        </div>
        <Link to="/ships" className="text-gray-400 hover:text-cyan-500 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
      </div>

      {compareList.length === 0 && (
        <div className="text-center py-16">
          <div className="glass-panel rounded-3xl p-12 max-w-2xl mx-auto">
            <Ship className="w-24 h-24 text-gray-600 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#FFFFFF' }}>
              No Ships Selected
            </h2>
            <p className="text-gray-400 mb-8">Add ships to start comparing their specifications</p>
            <button onClick={() => setShowSelector(true)} className="btn-origin">
              <Plus className="w-5 h-5 inline mr-2" />
              Add Ship
            </button>
          </div>
        </div>
      )}

      {compareList.length > 0 && (
        <>
          <div className="flex justify-end mb-4">
            {compareList.length < 3 && (
              <button onClick={() => setShowSelector(true)} className="btn-origin">
                <Plus className="w-5 h-5 inline mr-2" />
                Add Ship ({compareList.length}/3)
              </button>
            )}
          </div>

          <div className="glass-panel rounded-3xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="p-6 text-left text-gray-400 font-semibold">Specification</th>
                    {compareList.map(ship => (
                      <th key={ship.id} className="p-6 text-center relative">
                        <button
                          onClick={() => removeFromCompare(ship.id)}
                          className="absolute top-2 right-2 p-1 rounded-full bg-red-500/20 hover:bg-red-500 text-red-500 hover:text-white transition-all"
                        >
                          <X className="w-4 h-4" />
                        </button>
                        <div className="mb-4">
                          <img src={ship.image} alt={ship.name} className="w-full h-32 object-cover rounded-xl" />
                        </div>
                        <div className="text-xl font-bold text-cyan-500" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                          {ship.name}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {specs.map((spec, index) => (
                    <tr key={spec.key} className={index % 2 === 0 ? 'bg-white/5' : ''}>
                      <td className="p-4 text-gray-400 font-medium">{spec.label}</td>
                      {compareList.map(ship => (
                        <td key={ship.id} className="p-4 text-center text-white font-semibold">
                          {spec.key === 'price' && ship[spec.key] ? ship[spec.key].toLocaleString() :
                           spec.key === 'mass' && ship[spec.key] ? ship[spec.key].toLocaleString() :
                           ship[spec.key] || 'N/A'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Ship Selector Modal */}
      {showSelector && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel rounded-3xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
          >
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
                Select Ship to Compare
              </h2>
              <button onClick={() => setShowSelector(false)} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                <X className="w-6 h-6 text-gray-400" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {ships.filter(s => !compareList.find(c => c.id === s.id)).map(ship => (
                  <button
                    key={ship.id}
                    onClick={() => addToCompare(ship)}
                    className="glass-panel rounded-xl p-4 hover:border-cyan-500/50 transition-all text-left"
                  >
                    <img src={ship.image} alt={ship.name} className="w-full h-24 object-cover rounded-lg mb-3" />
                    <div className="font-bold text-white">{ship.name}</div>
                    <div className="text-sm text-gray-400">{ship.manufacturer}</div>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Compare;