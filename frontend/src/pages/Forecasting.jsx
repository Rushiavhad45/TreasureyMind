/**
 * TreasuryMind AI - Forecasting Page
 */

import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import toast from 'react-hot-toast';
import { forecastAPI } from '../services/api';
import { Zap, TrendingUp, Brain } from 'lucide-react';
import { format } from 'date-fns';

const fmt = (n) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact' }).format(n);

export default function Forecasting() {
  const { data: forecast, isLoading, refetch } = useQuery({
    queryKey: ['forecast-latest'],
    queryFn: () => forecastAPI.latest().then(r => r.data),
  });

  const triggerMutation = useMutation({
    mutationFn: () => forecastAPI.trigger({ horizon_days: 30 }),
    onSuccess: () => {
      toast.success('Forecast initiated — results in ~30 seconds');
      setTimeout(refetch, 30000);
    },
    onError: () => toast.error('Failed to trigger forecast'),
  });

  const chartData = forecast?.data_points?.map(dp => ({
    date: format(new Date(dp.date), 'MMM d'),
    net: Number(dp.predicted_net),
    inflow: Number(dp.predicted_inflow),
    outflow: Number(dp.predicted_outflow),
    upper: Number(dp.upper_bound),
    lower: Number(dp.lower_bound),
  })) || [];

  return (
    <div>
      <div className="tm-page-header">
        <div>
          <h1 className="tm-page-title">Cash Flow Forecasting</h1>
          <p className="tm-page-sub">AI-powered 30-day prediction with confidence intervals</p>
        </div>
        <button className="tm-btn tm-btn-primary" onClick={() => triggerMutation.mutate()} disabled={triggerMutation.isPending}>
          <Zap size={14} /> {triggerMutation.isPending ? 'Running...' : 'Run Forecast'}
        </button>
      </div>

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="tm-spinner" /></div>
      ) : forecast ? (
        <>
          <div className="tm-grid-3" style={{ marginBottom: 20 }}>
            {[
              { label: 'Model', value: forecast.model_type?.replace('_', ' '), color: 'var(--accent-cyan)' },
              { label: 'Horizon', value: `${forecast.horizon_days} days`, color: 'var(--accent-purple)' },
              { label: 'Status', value: forecast.status, color: forecast.status === 'completed' ? 'var(--accent-green)' : 'var(--accent-amber)' },
            ].map(({ label, value, color }) => (
              <div key={label} className="tm-card" style={{ textAlign: 'center' }}>
                <div className="tm-metric-label">{label}</div>
                <div style={{ fontSize: 20, fontWeight: 700, color, marginTop: 6, textTransform: 'capitalize' }}>{value}</div>
              </div>
            ))}
          </div>

          {/* Main forecast chart */}
          <div className="tm-card" style={{ marginBottom: 20 }}>
            <div className="tm-card-header">
              <span className="tm-card-title">30-Day Net Cash Flow Forecast</span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Generated {new Date(forecast.run_date).toLocaleDateString()}
              </span>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="fg-net" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={4} />
                <YAxis tickFormatter={fmt} tick={{ fontSize: 10 }} />
                <Tooltip formatter={(v, n) => [fmt(v), n]} />
                <ReferenceLine y={0} stroke="var(--border-bright)" strokeDasharray="4 4" />
                <Area type="monotone" dataKey="upper" name="Upper bound" stroke="none" fill="#22d3ee" fillOpacity={0.07} />
                <Area type="monotone" dataKey="net" name="Net forecast" stroke="#22d3ee" fill="url(#fg-net)" strokeWidth={2} />
                <Area type="monotone" dataKey="lower" name="Lower bound" stroke="none" fill="#22d3ee" fillOpacity={0.07} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* AI Reasoning */}
          {forecast.ai_reasoning && (
            <div className="tm-card" style={{ borderColor: 'rgba(34,211,238,0.2)' }}>
              <div className="tm-card-header">
                <span className="tm-card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Brain size={15} color="var(--accent-cyan)" /> AI Reasoning
                </span>
                <span className="tm-badge tm-badge-cyan">Gemini AI</span>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                {forecast.ai_reasoning}
              </p>
            </div>
          )}
        </>
      ) : (
        <div className="tm-card" style={{ textAlign: 'center', padding: 48 }}>
          <TrendingUp size={32} color="var(--text-muted)" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 8 }}>No forecast available</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: 20, fontSize: 13 }}>Click "Run Forecast" to generate your first AI forecast</p>
          <button className="tm-btn tm-btn-primary" onClick={() => triggerMutation.mutate()}>
            <Zap size={14} /> Generate Forecast
          </button>
        </div>
      )}
    </div>
  );
}
