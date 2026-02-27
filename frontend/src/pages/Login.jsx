import { useState } from 'react';
import { useAuth } from '../App';
import { Lock, User, Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';

const Login = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      toast.error('Please fill in all fields');
      return;
    }
    setLoading(true);
    try {
      await login(username.trim(), password);
    } catch {
      toast.error(isRegister ? 'Registration failed' : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 via-gray-900 to-blue-950 p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <img
            src="https://media.robertsspaceindustries.com/logo/SC-Logo-white-transparent.png"
            alt="Star Citizen"
            className="h-16 mx-auto mb-4 opacity-90"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <h1
            className="text-3xl font-bold uppercase tracking-wider"
            style={{ fontFamily: 'Rajdhani, sans-serif', color: '#00D4FF' }}
          >
            Fleet Manager
          </h1>
          <p className="text-gray-500 mt-2 text-sm">Track your ships, loadouts, and fleet</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-8 space-y-6">
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Username</label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                data-testid="username-input"
                className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                autoComplete="username"
              />
            </div>
          </div>

          <div>
            <label className="text-sm text-gray-400 mb-2 block">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                data-testid="password-input"
                className="w-full pl-12 pr-12 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                autoComplete={isRegister ? 'new-password' : 'current-password'}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                data-testid="toggle-password"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            data-testid="login-button"
            className="w-full py-3 rounded-xl font-bold text-black uppercase tracking-wider transition-all disabled:opacity-50"
            style={{
              background: 'linear-gradient(135deg, #00D4FF, #00A8CC)',
              fontFamily: 'Rajdhani, sans-serif',
            }}
          >
            {loading ? 'Connecting...' : (isRegister ? 'Create Account' : 'Access Fleet')}
          </button>

          <p className="text-center text-gray-500 text-sm">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              type="button"
              onClick={() => setIsRegister(!isRegister)}
              className="text-cyan-500 hover:text-cyan-400 transition-colors"
              data-testid="toggle-auth-mode"
            >
              {isRegister ? 'Sign In' : 'Register'}
            </button>
          </p>

          <p className="text-center text-gray-600 text-xs">
            New users are automatically registered on first login
          </p>
        </form>
      </div>
    </div>
  );
};

export default Login;
