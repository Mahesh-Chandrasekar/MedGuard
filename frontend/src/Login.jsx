import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Activity, Lock, User, AlertCircle, Sparkles } from 'lucide-react';

export default function Login() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isRegistering ? 'http://127.0.0.1:8000/register' : 'http://127.0.0.1:8000/login';

    try {
      const payload = { username, password };
      if (isRegistering) payload.hospital_name = 'General Hospital';

      const response = await axios.post(endpoint, payload);

      if (response.data.status === 'success') {
        if (isRegistering) {
            // Automatically switch back to login after reg
            setIsRegistering(false);
            setError('');
            setUsername('');
            setPassword('');
            alert("Account created successfully. Please log in.");
        } else {
            localStorage.setItem('medguard_user', response.data.username);
            navigate('/dashboard');
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to secure server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-glass-card">
        
        <div className="login-header">
          <div className="logo-container">
             <Activity size={32} color="var(--accent)" />
          </div>
          <h1>{isRegistering ? 'Doctor Registration' : 'Welcome to MedGuard'}</h1>
          <p>Clinical Intelligence System</p>
        </div>

        {error && (
          <div className="error-box">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-field">
            <User size={20} className="input-icon" />
            <input 
              type="text" 
              placeholder="Doctor Username" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="input-field">
            <Lock size={20} className="input-icon" />
            <input 
              type="password" 
              placeholder="Secure Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? 'AUTHENTICATING...' : (isRegistering ? 'CREATE ACCOUNT' : 'SECURE LOGIN')}
          </button>
        </form>

        <div className="toggle-mode">
            <p>
                {isRegistering ? "Already authorized?" : "No clinical access yet?"}{" "}
                <span onClick={() => setIsRegistering(!isRegistering)}>
                    {isRegistering ? "Return to Login" : "Initialize Auth Profile"}
                </span>
            </p>
        </div>
      </div>

      <style jsx="true">{`
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: radial-gradient(circle at center, var(--bg) 0%, #000 150%);
            /* Using CSS variables from index.css */
            color: var(--text);
            position: relative;
            overflow: hidden;
        }

        /* Ambient background glow */
        .login-container::before {
            content: '';
            position: absolute;
            width: 600px;
            height: 600px;
            background: var(--accent-bg);
            border-radius: 50%;
            filter: blur(100px);
            z-index: 0;
            animation: pulse-glow 8s infinite alternate;
        }

        @keyframes pulse-glow {
            0% { transform: scale(1); opacity: 0.5; }
            100% { transform: scale(1.2); opacity: 0.8; }
        }

        .login-glass-card {
            position: relative;
            z-index: 1;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 50px 40px;
            border-radius: 20px;
            border: 1px solid var(--accent-border);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 420px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .login-glass-card:hover {
            box-shadow: 0 10px 40px 0 var(--accent-bg);
            border: 1px solid var(--accent);
        }

        .logo-container {
            background: var(--code-bg);
            width: 64px;
            height: 64px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 15px var(--accent-bg);
        }

        .login-header h1 {
            font-size: 28px;
            color: var(--text-h);
            margin: 0 0 5px 0;
            font-weight: 600;
            letter-spacing: -1px;
        }

        .login-header p {
            font-size: 14px;
            color: var(--text);
            margin-top: 0;
            margin-bottom: 30px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .error-box {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background: rgba(220, 38, 38, 0.1);
            border: 1px solid rgba(220, 38, 38, 0.5);
            color: #ef4444;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .login-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .input-field {
            position: relative;
            display: flex;
            align-items: center;
        }

        .input-icon {
            position: absolute;
            left: 16px;
            color: var(--text);
            opacity: 0.7;
        }

        .input-field input {
            width: 100%;
            padding: 16px 16px 16px 50px;
            background: var(--code-bg);
            border: 1px solid var(--border);
            color: var(--text-h);
            border-radius: 12px;
            font-size: 15px;
            outline: none;
            transition: 0.3s;
            box-sizing: border-box;
        }

        .input-field input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-bg);
        }

        .login-btn {
            background: var(--accent);
            color: #ffffff;
            padding: 16px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 10px;
            background-size: 200% auto;
            text-transform: tracking;
            letter-spacing: 2px;
        }

        .login-btn:hover {
            box-shadow: 0 0 20px var(--accent-border);
            transform: translateY(-2px);
            filter: brightness(1.2);
        }
        
        .login-btn:active {
            transform: translateY(1px);
        }

        .toggle-mode {
            margin-top: 25px;
            font-size: 14px;
            color: var(--text);
        }

        .toggle-mode span {
            color: var(--accent);
            cursor: pointer;
            font-weight: 500;
            transition: 0.2s;
        }

        .toggle-mode span:hover {
            text-decoration: underline;
            text-shadow: 0 0 10px var(--accent-bg);
        }
      `}</style>
    </div>
  );
}