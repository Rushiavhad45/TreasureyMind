/**
 * TreasuryMind AI - Alerts Page
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { alertAPI } from '../services/api';
import { Bell, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';

const severityConfig = {
  critical: { icon: XCircle, color: 'var(--accent-red)', badge: 'tm-badge-red', label: 'Critical' },
  warning: { icon: AlertTriangle, color: 'var(--accent-amber)', badge: 'tm-badge-amber', label: 'Warning' },
  info: { icon: Info, color: 'var(--accent-cyan)', badge: 'tm-badge-cyan', label: 'Info' },
};

const fmtTime = (d) => new Date(d).toLocaleString();

export default function AlertsPage() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['alerts', filter],
    queryFn: () => alertAPI.list({ severity: filter || undefined, is_resolved: false }).then(r => r.data),
    refetchInterval: 30_000,
  });

  const { data: stats } = useQuery({
    queryKey: ['alert-stats'],
    queryFn: () => alertAPI.stats().then(r => r.data),
  });

  const ackMutation = useMutation({
    mutationFn: alertAPI.acknowledge,
    onSuccess: () => { qc.invalidateQueries(['alerts']); qc.invalidateQueries(['alert-stats']); toast.success('Alert acknowledged'); },
  });

  const alerts = data?.results || [];

  return (
    <div>
      <div className="tm-page-header">
        <div>
          <h1 className="tm-page-title">Alerts & Notifications</h1>
          <p className="tm-page-sub">{stats?.unread || 0} unread · {stats?.critical || 0} critical</p>
        </div>
        <Bell size={20} color="var(--accent-amber)" />
      </div>

      {/* Stat row */}
      <div className="tm-grid-3" style={{ marginBottom: 20 }}>
        {[
          { label: 'Total Active', value: stats?.total || 0, color: 'var(--text-secondary)' },
          { label: 'Unread', value: stats?.unread || 0, color: 'var(--accent-amber)' },
          { label: 'Critical', value: stats?.critical || 0, color: 'var(--accent-red)' },
        ].map(({ label, value, color }) => (
          <div key={label} className="tm-metric" style={{ textAlign: 'center' }}>
            <div className="tm-metric-label">{label}</div>
            <div className="tm-metric-value" style={{ color }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="tm-card" style={{ marginBottom: 16, padding: '12px 16px' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {['', 'critical', 'warning', 'info'].map(s => (
            <button key={s} className={`tm-btn ${filter === s ? 'tm-btn-primary' : 'tm-btn-ghost'} tm-btn-sm`}
              onClick={() => setFilter(s)}>
              {s || 'All'}
            </button>
          ))}
        </div>
      </div>

      {/* Alert list */}
      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}><div className="tm-spinner" /></div>
      ) : alerts.length === 0 ? (
        <div className="tm-card" style={{ textAlign: 'center', padding: 48 }}>
          <CheckCircle size={32} color="var(--accent-green)" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ color: 'var(--text-secondary)' }}>All clear</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 6 }}>No active alerts matching your filter</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {alerts.map(alert => {
            const cfg = severityConfig[alert.severity] || severityConfig.info;
            const SevIcon = cfg.icon;
            return (
              <div key={alert.id} className="tm-card" style={{
                borderLeftWidth: 3, borderLeftColor: cfg.color,
                opacity: alert.is_read ? 0.6 : 1,
                transition: 'opacity 0.2s'
              }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, flex: 1 }}>
                    <SevIcon size={18} color={cfg.color} style={{ flexShrink: 0, marginTop: 2 }} />
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{alert.title}</span>
                        <span className={`tm-badge ${cfg.badge}`}>{cfg.label}</span>
                        {!alert.is_read && <span className="tm-badge tm-badge-cyan" style={{ fontSize: 10 }}>New</span>}
                      </div>
                      <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{alert.message}</p>
                      <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>{fmtTime(alert.created_at)}</p>
                    </div>
                  </div>
                  {!alert.is_read && (
                    <button className="tm-btn tm-btn-ghost tm-btn-sm" style={{ flexShrink: 0 }}
                      onClick={() => ackMutation.mutate(alert.id)}>
                      <CheckCircle size={13} /> Acknowledge
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
