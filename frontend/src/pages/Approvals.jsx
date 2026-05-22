/**
 * TreasuryMind AI - Approvals Page
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { approvalAPI } from '../services/api';
import useAuthStore from '../store/authStore';
import { CheckSquare, CheckCircle, XCircle, Clock, FileText } from 'lucide-react';

const fmtTime = (d) => d ? new Date(d).toLocaleString() : '—';

const statusConfig = {
  pending: { badge: 'tm-badge-amber', icon: Clock },
  approved: { badge: 'tm-badge-green', icon: CheckCircle },
  rejected: { badge: 'tm-badge-red', icon: XCircle },
  escalated: { badge: 'tm-badge-purple', icon: FileText },
};

function DecisionModal({ approval, onClose, onDecide }) {
  const [decision, setDecision] = useState('approved');
  const [comments, setComments] = useState('');

  return (
    <div className="tm-modal-overlay" onClick={onClose}>
      <div className="tm-modal" onClick={e => e.stopPropagation()}>
        <h3 style={{ fontSize: 16, marginBottom: 8 }}>Review Approval</h3>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>{approval.title}</p>
        <div style={{ marginBottom: 14 }}>
          <label className="tm-label">Decision</label>
          <div style={{ display: 'flex', gap: 10 }}>
            {['approved', 'rejected'].map(d => (
              <button key={d} onClick={() => setDecision(d)}
                className={`tm-btn ${decision === d ? (d === 'approved' ? 'tm-btn-primary' : 'tm-btn-danger') : 'tm-btn-ghost'}`}
                style={{ flex: 1, justifyContent: 'center', textTransform: 'capitalize' }}>
                {d === 'approved' ? <CheckCircle size={13} /> : <XCircle size={13} />}
                {d}
              </button>
            ))}
          </div>
        </div>
        <div style={{ marginBottom: 20 }}>
          <label className="tm-label">Comments</label>
          <textarea className="tm-input" value={comments} onChange={e => setComments(e.target.value)}
            style={{ resize: 'vertical', minHeight: 80 }} placeholder="Optional comments..." />
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
          <button className="tm-btn tm-btn-ghost" onClick={onClose}>Cancel</button>
          <button className="tm-btn tm-btn-primary" onClick={() => onDecide(approval.id, decision, comments)}>
            Submit Decision
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Approvals() {
  const qc = useQueryClient();
  const user = useAuthStore(s => s.user);
  const [filter, setFilter] = useState('pending');
  const [modal, setModal] = useState(null);

  const { data, isLoading } = useQuery({
    queryKey: ['approvals', filter],
    queryFn: () => approvalAPI.list({ status: filter || undefined }).then(r => r.data),
  });

  const decideMutation = useMutation({
    mutationFn: ({ id, decision, comments }) => approvalAPI.decide(id, decision, comments),
    onSuccess: (_, { decision }) => {
      qc.invalidateQueries(['approvals']);
      setModal(null);
      toast.success(`Approval ${decision}`);
    },
    onError: () => toast.error('Failed to submit decision'),
  });

  const canDecide = user?.role === 'admin' || user?.role === 'approver';
  const approvals = data?.results || [];

  return (
    <div>
      {modal && (
        <DecisionModal
          approval={modal}
          onClose={() => setModal(null)}
          onDecide={(id, decision, comments) => decideMutation.mutate({ id, decision, comments })}
        />
      )}

      <div className="tm-page-header">
        <div>
          <h1 className="tm-page-title">Approval Workflow</h1>
          <p className="tm-page-sub">Review and act on AI-generated recommendations</p>
        </div>
        <CheckSquare size={20} color="var(--accent-cyan)" />
      </div>

      {/* Filter tabs */}
      <div className="tm-card" style={{ marginBottom: 16, padding: '10px 16px' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {['pending', 'approved', 'rejected', ''].map(s => (
            <button key={s} className={`tm-btn ${filter === s ? 'tm-btn-primary' : 'tm-btn-ghost'} tm-btn-sm`}
              onClick={() => setFilter(s)}>
              {s || 'All'}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}><div className="tm-spinner" /></div>
      ) : approvals.length === 0 ? (
        <div className="tm-card" style={{ textAlign: 'center', padding: 48 }}>
          <CheckSquare size={32} color="var(--text-muted)" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ color: 'var(--text-secondary)' }}>No approvals found</h3>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {approvals.map(appr => {
            const cfg = statusConfig[appr.status] || statusConfig.pending;
            const StatusIcon = cfg.icon;
            return (
              <div key={appr.id} className="tm-card">
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <StatusIcon size={15} color={appr.status === 'approved' ? 'var(--accent-green)' : appr.status === 'rejected' ? 'var(--accent-red)' : 'var(--accent-amber)'} />
                      <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{appr.title}</span>
                      <span className={`tm-badge ${cfg.badge}`}>{appr.status}</span>
                      <span className="tm-badge tm-badge-gray" style={{ fontSize: 10 }}>{appr.approval_type?.replace('_', ' ')}</span>
                    </div>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8, lineHeight: 1.5 }}>{appr.description}</p>
                    <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--text-muted)' }}>
                      <span>Requested: {fmtTime(appr.created_at)}</span>
                      {appr.decided_at && <span>Decided: {fmtTime(appr.decided_at)}</span>}
                      {appr.approved_by_name && <span>By: {appr.approved_by_name}</span>}
                    </div>
                    {appr.comments && (
                      <div style={{ marginTop: 8, padding: '8px 12px', background: 'var(--bg-secondary)', borderRadius: 6, fontSize: 12, color: 'var(--text-secondary)' }}>
                        "{appr.comments}"
                      </div>
                    )}
                  </div>
                  {canDecide && appr.status === 'pending' && (
                    <button className="tm-btn tm-btn-primary tm-btn-sm" style={{ marginLeft: 16, flexShrink: 0 }}
                      onClick={() => setModal(appr)}>
                      Review
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
