import { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Fleet from './pages/Fleet';
import Ships from './pages/Ships';
import Vehicles from './pages/Vehicles';
import Components from './pages/Components';
import Weapons from './pages/Weapons';
import ShipDetail from './pages/ShipDetail';
import Compare from './pages/Compare';
import LoadoutBuilder from './pages/LoadoutBuilder';
import CommunityLoadouts from './pages/CommunityLoadouts';
import SharedLoadout from './pages/SharedLoadout';
import RoutePlanner from './pages/RoutePlanner';
import Layout from './components/Layout';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, authLoading } = useAuth();
  if (authLoading) return null;
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
    setAuthLoading(false);
  }, []);

  const login = async (username, password) => {
    const response = await axios.post(`${API}/auth/login`, { username, password });
    const { access_token, user: userData } = response.data;
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    setIsAuthenticated(true);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, token, login, logout, API, authLoading }}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <Login />} />
          <Route path="/" element={<PrivateRoute><Layout><Dashboard /></Layout></PrivateRoute>} />
          <Route path="/fleet" element={<PrivateRoute><Layout><Fleet /></Layout></PrivateRoute>} />
          <Route path="/ships" element={<PrivateRoute><Layout><Ships /></Layout></PrivateRoute>} />
          <Route path="/ships/:shipId" element={<PrivateRoute><Layout><ShipDetail /></Layout></PrivateRoute>} />
          <Route path="/ships/:shipId/loadout" element={<PrivateRoute><Layout><LoadoutBuilder /></Layout></PrivateRoute>} />
          <Route path="/loadout" element={<PrivateRoute><Layout><LoadoutBuilder /></Layout></PrivateRoute>} />
          <Route path="/compare" element={<PrivateRoute><Layout><Compare /></Layout></PrivateRoute>} />
          <Route path="/vehicles" element={<PrivateRoute><Layout><Vehicles /></Layout></PrivateRoute>} />
          <Route path="/components" element={<PrivateRoute><Layout><Components /></Layout></PrivateRoute>} />
          <Route path="/weapons" element={<PrivateRoute><Layout><Weapons /></Layout></PrivateRoute>} />
          <Route path="/community" element={<PrivateRoute><Layout><CommunityLoadouts /></Layout></PrivateRoute>} />
          <Route path="/routes" element={<PrivateRoute><Layout><RoutePlanner /></Layout></PrivateRoute>} />
          <Route path="/shared/:shareCode" element={<SharedLoadout />} />
        </Routes>
        <Toaster position="top-right" />
      </BrowserRouter>
    </AuthContext.Provider>
  );
}

export default App;