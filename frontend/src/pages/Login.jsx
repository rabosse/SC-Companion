import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import axios from 'axios';
import { Lock } from 'lucide-react';
import { toast } from 'sonner';

const Login = () => {
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, API } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        star_citizen_token: token,
      });

      login(response.data.access_token, response.data.user);
      toast.success('Welcome to Star Citizen Fleet Manager');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden" style={{ background: '#050508' }}>
      {/* Background effects */}
      <div className="absolute inset-0 radial-glow opacity-30"></div>
      <div className="absolute top-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>

      <div className="relative z-10 w-full max-w-md px-6">
        <div className="glass-panel rounded-3xl p-8 sm:p-12">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <img 
              src="https://media.robertsspaceindustries.com/logo/SC-Logo-white.png" 
              alt="Star Citizen Logo"
              className="h-20 w-auto"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-center mb-2 uppercase" style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}>
            Star Citizen Fleet Manager
          </h1>
          <p className="text-center text-gray-400 mb-8" style={{ fontFamily: 'Inter, sans-serif' }}>
            Manage your Star Citizen fleet with precision
          </p>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="email-input"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2" htmlFor="token">
                Star Citizen API Token
              </label>
              <input
                id="token"
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
                data-testid="token-input"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                placeholder="Your API token"
              />
            </div>

            <p className="text-xs text-gray-500 text-center">
              Get your token from{' '}
              <a
                href="https://star-citizen.wiki"
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-500 hover:underline"
              >
                star-citizen.wiki
              </a>
            </p>

            <button
              type="submit"
              disabled={loading}
              data-testid="login-button"
              className="w-full btn-origin flex items-center justify-center space-x-2"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  <span>Access Fleet</span>
                </>
              )}
            </button>
          </form>

          {/* Demo info */}
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
            <p className="text-xs text-center text-gray-400">
              <strong className="text-cyan-500">Demo Mode:</strong> Use any email and token to explore the app
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;