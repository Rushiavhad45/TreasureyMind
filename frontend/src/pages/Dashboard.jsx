/**
 * TreasuryMind AI - Dashboard Page
 * Main overview with KPIs, charts, and quick stats
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import { transactionAPI, alertAPI, agentAPI } from '../services/api';
import { TrendingUp, TrendingDown, DollarSign, Activity, Bell, Bot, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { format, subDays } from 'date-fns';

const fmt = (n) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 1 }).format(n);
const fmtFull = (n) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);

function MetricCard({ label, value, sub, accent, icon: Icon, trend }) {
  return (
    <div className="tm-metric">
      <div className="tm-metric-accent" style={{ background: accent }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingRight: 8 }}>
        <div>
          <div className="tm-metric-label">{label}</div>
          <div className="tm-metric-value">{value}</div>
          {sub && <div className="tm-metric-sub">{sub}</div>}
        </div>
        <div style={{ width: 36, height: 36, borderRadius: 10, background: `${accent}20`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon size={18} color={accent} />
        </div>
      </div>
      {trend !== undefined && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 10, fontSize: 12 }}>
          {trend >= 0
            ? <><ArrowUpRight size={12} color="var(--accent-green)" /><span style={{ color: 'var(--accent-green)' }}>+{trend}%</span></>
            : <><ArrowDownRight size={12} color="var(--accent-red)" /><span style={{ color: 'var(--accent-red)' }}>{trend}%</span></>
          }
          <span style={{ color: 'var(--text-muted)' }}>vs last period</span>
        </div>
      )}
    </div>
  );
}

function LiquidityGauge({ score }) {
  const color = score >= 70 ? 'var(--accent-green)' : score >= 40 ? 'var(--accent-amber)' : 'var(--accent-red)';
  const label = score >= 70 ? 'Healthy' : score >= 40 ? 'Moderate' : 'Critical';
  const circumference = 2 * Math.PI * 45;
  const offset = circumference * (1 - score / 100);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '12px 0' }}>
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="45" fill="none" stroke="var(--border)" strokeWidth="10" />
        <circle cx="60" cy="60" r="45" fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 60 60)"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
        <text x="60" y="54" textAnchor="middle" fill={color} fontSize="22" fontWeight="700" fontFamily="JetBrains Mono">{score}</text>
        <text x="60" y="72" textAnchor="middle" fill="var(--text-muted)" fontSize="11">{label}</text>
      </svg>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', marginTop: 4 }}>Liquidity Score</div>
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="tm-card" style={{ padding: '10px 14px', border: '1px solid var(--border-bright)', minWidth: 160 }}>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, fontSize: 12 }}>
          <span style={{ color: p.color }}>{p.name}</span>
          <span style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-primary)' }}>{fmt(p.value)}</span>
        </div>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['summary', 30],
    queryFn: () => transactionAPI.summary({ period: 30 }).then(r => r.data),
    refetchInterval: 60_000,
  });

  const { data: alertStats } = useQuery({
    queryKey: ['alert-stats'],
    queryFn: () => alertAPI.stats().then(r => r.data),
  });

  const { data: agentStatus } = useQuery({
    queryKey: ['agent-status'],
    queryFn: () => agentAPI.status().then(r => r.data),
    refetchInterval: 30_000,
  });

  // Transform daily trend for chart
  const chartData = React.useMemo(() => {
    if (!summary?.daily_trend) return [];
    const byDate = {};
    summary.daily_trend.forEach(({ date, transaction_type, total }) => {
      const d = format(new Date(date), 'MMM d');
      if (!byDate[d]) byDate[d] = { date: d, inflow: 0, outflow: 0 };
      byDate[d][transaction_type] = Number(total);
    });
    return Object.values(byDate).slice(-14);
  }, [summary]);

  // Category pie data
  const pieData = React.useMemo(() => {
    if (!summary?.category_breakdown) return [];
    return summary.category_breakdown.slice(0, 5).map(item => ({
      name: item.category.replace('_', ' '),
      value: Number(item.total),
    }));
  }, [summary]);

  const PIE_COLORS = ['#22d3ee', '#14b8a6', '#3b82f6', '#8b5cf6', '#f59e0b'];

  const agentList = agentStatus ? Object.entries(agentStatus) : [];
  const runningAgents = agentList.filter(([, v]) => v.status === 'running').length;
  const completedAgents = agentList.filter(([, v]) => v.status === 'completed').length;

  return (
    <div>
      <div className="tm-page-header">
        <div>
          <h1 className="tm-page-title">Treasury Dashboard</h1>
          <p className="tm-page-sub">Real-time cash flow intelligence · Last 30 days</p>
        </div>
        <div className="tm-badge tm-badge-cyan" style={{ fontSize: 12, padding: '6px 12px' }}>
          <span className="tm-pulse" style={{ width: 6, height: 6 }} />
          Live Monitoring
        </div>
      </div>

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
          <div className="tm-spinner" />
        </div>
      ) : (
        <>
          {/* KPI Row */}
          <div className="tm-grid-4" style={{ marginBottom: 20 }}>
            <MetricCard label="Total Inflow" value={fmt(summary?.total_inflow || 0)}
              sub="Last 30 days" accent="var(--accent-green)" icon={TrendingUp} trend={12.4} />
            <MetricCard label="Total Outflow" value={fmt(summary?.total_outflow || 0)}
              sub="Last 30 days" accent="var(--accent-red)" icon={TrendingDown} trend={-3.2} />
            <MetricCard label="Net Cash Flow" value={fmt(summary?.net_cashflow || 0)}
              sub="Surplus / Deficit" accent="var(--accent-cyan)" icon={DollarSign} trend={8.1} />
            <MetricCard label="Transactions" value={summary?.transaction_count || 0}
              sub="Completed" accent="var(--accent-purple)" icon={Activity} />
          </div>

          {/* Charts row */}
          <div className="tm-grid-2" style={{ marginBottom: 20 }}>
            {/* Inflow vs Outflow chart */}
            <div className="tm-card">
              <div className="tm-card-header">
                <span className="tm-card-title">Inflow vs Outflow</span>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>14-day view</span>
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="gi" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="go" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                  <YAxis tickFormatter={v => fmt(v)} tick={{ fontSize: 10 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="inflow" name="Inflow" stroke="#10b981" fill="url(#gi)" strokeWidth={2} />
                  <Area type="monotone" dataKey="outflow" name="Outflow" stroke="#ef4444" fill="url(#go)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Category breakdown + liquidity */}
            <div className="tm-card">
              <div className="tm-card-header">
                <span className="tm-card-title">Category Breakdown</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <LiquidityGauge score={summary?.liquidity_score || 0} />
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={75}
                      dataKey="value" stroke="none">
                      {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => fmtFull(v)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 12px', marginTop: 8 }}>
                {pieData.map((item, i) => (
                  <div key={item.name} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11 }}>
                    <div style={{ width: 8, height: 8, borderRadius: 2, background: PIE_COLORS[i] }} />
                    <span style={{ color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{item.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom row: Alerts + Agents */}
          <div className="tm-grid-2">
            {/* Alert stats */}
            <div className="tm-card">
              <div className="tm-card-header">
                <span className="tm-card-title">Alert Summary</span>
                <Bell size={15} color="var(--text-muted)" />
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                {[
                  { label: 'Total', value: alertStats?.total || 0, color: 'var(--text-secondary)' },
                  { label: 'Unread', value: alertStats?.unread || 0, color: 'var(--accent-amber)' },
                  { label: 'Critical', value: alertStats?.critical || 0, color: 'var(--accent-red)' },
                ].map(({ label, value, color }) => (
                  <div key={label} style={{
                    flex: 1, padding: '16px', background: 'var(--bg-secondary)',
                    borderRadius: 10, textAlign: 'center'
                  }}>
                    <div style={{ fontSize: 26, fontWeight: 700, color, fontFamily: 'JetBrains Mono' }}>{value}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>{label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Agent status */}
            <div className="tm-card">
              <div className="tm-card-header">
                <span className="tm-card-title">AI Agent Status</span>
                <Bot size={15} color="var(--text-muted)" />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {agentList.slice(0, 4).map(([key, data]) => (
                  <div key={key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{data.label}</span>
                    <span className={`tm-badge ${data.status === 'completed' ? 'tm-badge-green' : data.status === 'running' ? 'tm-badge-cyan' : data.status === 'failed' ? 'tm-badge-red' : 'tm-badge-gray'}`}>
                      {data.status}
                    </span>
                  </div>
                ))}
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, textAlign: 'right' }}>
                  {completedAgents}/{agentList.length} completed
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
