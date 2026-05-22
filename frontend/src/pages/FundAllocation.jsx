/**
 * TreasuryMind AI - Fund Allocation Page
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { allocationAPI } from '../services/api';
import { PieChart as PieIcon, Shield, TrendingUp, Brain } from 'lucide-react';

const fmt = (n) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
const COLORS = ['#22d3ee', '#14b8a6', '#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'];

export default function FundAllocation() {
  const { data, isLoading } = useQuery({
    queryKey: ['allocations'],
    queryFn: () => allocationAPI.list().then(r => r.data),
  });

  const allocations = data?.results || [];
  const latest = allocations[0];

  const pieData = latest?.allocation_breakdown?.map(item => ({
    name: item.category,
    value: Number(item.amount) || (Number(latest.surplus_amount) * (item.percentage / 100)),
  })) || [];

  return (
    <div>
      <div className="tm-page-header">
        <div>
          <h1 className="tm-page-title">Fund Allocation</h1>
          <p className="tm-page-sub">AI-generated surplus fund allocation recommendations</p>
        </div>
      </div>

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="tm-spinner" /></div>
      ) : latest ? (
        <>
          {/* Summary cards */}
          <div className="tm-grid-3" style={{ marginBottom: 20 }}>
            <div className="tm-metric">
              <div className="tm-metric-accent" style={{ background: 'var(--accent-cyan)' }} />
              <div className="tm-metric-label">Surplus Amount</div>
              <div className="tm-metric-value">{fmt(latest.surplus_amount)}</div>
            </div>
            <div className="tm-metric">
              <div className="tm-metric-accent" style={{ background: 'var(--accent-purple)' }} />
              <div className="tm-metric-label">AI Confidence</div>
              <div className="tm-metric-value">{(latest.ai_confidence_score * 100).toFixed(0)}%</div>
            </div>
            <div className="tm-metric">
              <div className="tm-metric-accent" style={{ background: latest.risk_level === 'low' ? 'var(--accent-green)' : latest.risk_level === 'high' ? 'var(--accent-red)' : 'var(--accent-amber)' }} />
              <div className="tm-metric-label">Risk Level</div>
              <div className="tm-metric-value" style={{ textTransform: 'capitalize' }}>{latest.risk_level}</div>
            </div>
          </div>

          <div className="tm-grid-2" style={{ marginBottom: 20 }}>
            {/* Pie chart */}
            <div className="tm-card">
              <div className="tm-card-header">
                <span className="tm-card-title">Allocation Breakdown</span>
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip formatter={(v) => fmt(v)} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Breakdown table */}
            <div className="tm-card" style={{ padding: 0 }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
                <span className="tm-card-title">Recommended Allocations</span>
              </div>
              <table className="tm-table">
                <thead>
                  <tr><th>Category</th><th>Amount</th><th>%</th></tr>
                </thead>
                <tbody>
                  {latest.allocation_breakdown?.map((item, i) => (
                    <tr key={i}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ width: 8, height: 8, borderRadius: 2, background: COLORS[i] }} />
                          <span style={{ color: 'var(--text-primary)' }}>{item.category}</span>
                        </div>
                      </td>
                      <td className="font-mono">{fmt(item.amount || 0)}</td>
                      <td>{item.percentage}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* AI Reasoning */}
          {latest.ai_reasoning && (
            <div className="tm-card" style={{ borderColor: 'rgba(34,211,238,0.2)' }}>
              <div className="tm-card-header">
                <span className="tm-card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Brain size={15} color="var(--accent-cyan)" /> AI Reasoning
                </span>
                <span className={`tm-badge ${latest.status === 'pending' ? 'tm-badge-amber' : latest.status === 'approved' ? 'tm-badge-green' : 'tm-badge-gray'}`}>
                  {latest.status}
                </span>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7 }}>{latest.ai_reasoning}</p>
            </div>
          )}
        </>
      ) : (
        <div className="tm-card" style={{ textAlign: 'center', padding: 48 }}>
          <PieIcon size={32} color="var(--text-muted)" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 8 }}>No allocation suggestions yet</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Run the agent pipeline from the Agent Status page to generate recommendations.</p>
        </div>
      )}
    </div>
  );
}
