/**
 * TreasuryMind AI - Main App
 * React Router setup with protected routes
 */

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import useAuthStore from './store/authStore';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Forecasting from './pages/Forecasting';
import FundAllocation from './pages/FundAllocation';
import AlertsPage from './pages/Alerts';
import Approvals from './pages/Approvals';
import AgentStatus from './pages/AgentStatus';
import Layout from './components/common/Layout';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
});

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuthStore();
  if (isLoading) return <LoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

function LoadingScreen() {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      minHeight: '100vh', background: '#0a0e1a', flexDirection: 'column', gap: '16px'
    }}>
      <div className="tm-spinner" />
      <p style={{ color: '#6b7280', fontSize: '14px' }}>Initializing TreasuryMind AI...</p>
    </div>
  );
}

export default function App() {
  const initialize = useAuthStore(s => s.initialize);

  useEffect(() => { initialize(); }, [initialize]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: '#1a2035', color: '#e2e8f0', border: '1px solid #2d3748' },
            success: { iconTheme: { primary: '#22d3ee', secondary: '#0a0e1a' } },
            error: { iconTheme: { primary: '#f87171', secondary: '#0a0e1a' } },
          }}
        />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="transactions" element={<Transactions />} />
            <Route path="forecasting" element={<Forecasting />} />
            <Route path="allocation" element={<FundAllocation />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="approvals" element={<Approvals />} />
            <Route path="agents" element={<AgentStatus />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
