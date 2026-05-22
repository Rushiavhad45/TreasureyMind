/**
 * TreasuryMind AI - Login Page
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import useAuthStore from '../store/authStore';
import { Lock, Mail, Eye, EyeOff } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('admin@treasurymind.ai');
  const [password, setPassword] = useState('TreasuryMind2024!');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const login = useAuthStore(s => s.login);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome to TreasuryMind AI');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at 20% 50%, #0f2040 0%, #0a0e1a 50%, #080c18 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 24
    }}>
      {/* Decorative grid */}
      <div style={{
        position: 'fixed', inset: 0, opacity: 0.03,
        backgroundImage: 'linear-gradient(var(--accent-cyan) 1px, transparent 1px), linear-gradient(90deg, var(--accent-cyan) 1px, transparent 1px)',
        backgroundSize: '48px 48px', pointerEvents: 'none'
      }} />

      <div style={{ width: '100%', maxWidth: 420, position: 'relative' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <div style={{
            width: 56, height: 56,
            background: 'linear-gradient(135deg, #22d3ee, #14b8a6)',
            borderRadius: 14, margin: '0 auto 16px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 22, fontWeight: 800, color: '#0a0e1a',
            boxShadow: '0 0 30px rgba(34,211,238,0.3)'
          }}>TM</div>
          <h1 style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6 }}>
            TreasuryMind AI
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Multi-Agent Treasury & Cash Flow Platform
          </p>
        </div>

        {/* Card */}
        <div className="tm-card" style={{ border: '1px solid #1e3a5f' }}>
          <h2 style={{ fontSize: 17, marginBottom: 20, color: 'var(--text-primary)' }}>Sign in</h2>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: 14 }}>
              <label className="tm-label">Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="email" className="tm-input" value={email}
                  onChange={e => setEmail(e.target.value)}
                  style={{ paddingLeft: 32 }} required
                />
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label className="tm-label">Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type={showPass ? 'text' : 'password'}
                  className="tm-input" value={password}
                  onChange={e => setPassword(e.target.value)}
                  style={{ paddingLeft: 32, paddingRight: 36 }} required
                />
                <button type="button" onClick={() => setShowPass(!showPass)} style={{
                  position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)'
                }}>
                  {showPass ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>

            <button type="submit" className="tm-btn tm-btn-primary" disabled={loading}
              style={{ width: '100%', justifyContent: 'center', height: 40, fontSize: 14 }}>
              {loading ? <span className="tm-spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> : 'Sign in'}
            </button>
          </form>

          <div style={{ marginTop: 20, padding: '12px', background: 'rgba(34,211,238,0.05)', borderRadius: 8, border: '1px solid rgba(34,211,238,0.15)' }}>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Demo credentials:</p>
            {[
              ['admin@treasurymind.ai', 'Admin'],
              ['treasury@treasurymind.ai', 'Treasury Manager'],
              ['approver@treasurymind.ai', 'Approver'],
            ].map(([e, role]) => (
              <div key={e} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                <span style={{ fontSize: 11, color: 'var(--accent-cyan)', cursor: 'pointer' }} onClick={() => setEmail(e)}>{e}</span>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{role}</span>
              </div>
            ))}
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>Password: TreasuryMind2024!</p>
          </div>
        </div>
      </div>
    </div>
  );
}
