/**
 * TreasuryMind AI - Layout Component
 * Sidebar + Topbar shell
 */

import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import useAuthStore from '../../store/authStore';
import {
  LayoutDashboard, ArrowLeftRight, TrendingUp, PieChart,
  Bell, CheckSquare, Bot, LogOut, ChevronRight, Settings
} from 'lucide-react';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'Transactions', path: '/transactions', icon: ArrowLeftRight },
  { label: 'Forecasting', path: '/forecasting', icon: TrendingUp },
  { label: 'Fund Allocation', path: '/allocation', icon: PieChart },
  { label: 'Alerts', path: '/alerts', icon: Bell },
  { label: 'Approvals', path: '/approvals', icon: CheckSquare },
  { label: 'Agent Status', path: '/agents', icon: Bot },
];

export default function Layout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  return (
    <div style={{ display: 'flex' }}>
      {/* Sidebar */}
      <nav className="tm-sidebar">
        <div className="tm-sidebar-logo">
          <div className="tm-sidebar-logo-mark">TM</div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
              TreasuryMind
            </div>
            <div style={{ fontSize: '10px', color: 'var(--accent-cyan)', letterSpacing: '0.1em' }}>
              AI PLATFORM
            </div>
          </div>
        </div>

        <div className="tm-sidebar-nav">
          <div className="tm-nav-section">Main</div>
          {navItems.slice(0, 4).map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) => `tm-nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={15} />
              {label}
            </NavLink>
          ))}

          <div className="tm-nav-section" style={{ marginTop: '8px' }}>Workflow</div>
          {navItems.slice(4).map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) => `tm-nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={15} />
              {label}
            </NavLink>
          ))}
        </div>

        {/* User section */}
        <div style={{ padding: '16px', borderTop: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: 'linear-gradient(135deg, #22d3ee, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 12, fontWeight: 700, color: '#fff', flexShrink: 0
            }}>
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', truncate: true }}>
                {user?.first_name} {user?.last_name}
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                {user?.role?.replace('_', ' ')}
              </div>
            </div>
          </div>
          <button onClick={handleLogout} className="tm-btn tm-btn-ghost" style={{ width: '100%', justifyContent: 'center', fontSize: 12 }}>
            <LogOut size={13} /> Sign out
          </button>
        </div>
      </nav>

      {/* Main area */}
      <div className="tm-main">
        {/* Topbar */}
        <div className="tm-topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: 13 }}>
            <div className="tm-pulse" />
            <span style={{ color: 'var(--accent-green)', fontSize: 12 }}>All systems operational</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
          </div>
        </div>

        <div className="tm-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
