/**
 * TreasuryMind AI - Transactions Page
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { transactionAPI } from '../services/api';
import { Plus, Search, Trash2, Edit2, X, ChevronUp, ChevronDown } from 'lucide-react';

const fmt = (n) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
const fmtDate = (d) => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

const CATEGORIES = [
  'revenue', 'investment', 'loan_receipt', 'receivable_collection', 'grant',
  'payroll', 'vendor_payment', 'loan_repayment', 'capex', 'opex', 'tax', 'utility', 'other'
];

function TransactionModal({ onClose, onSave, initial }) {
  const [form, setForm] = useState(initial || {
    title: '', amount: '', transaction_type: 'inflow', category: 'revenue',
    transaction_date: new Date().toISOString().split('T')[0], counterparty: '', description: ''
  });

  const set = (k, v) => setForm(p => ({ ...p, [k]: v }));

  return (
    <div className="tm-modal-overlay" onClick={onClose}>
      <div className="tm-modal" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 style={{ fontSize: 16 }}>{initial ? 'Edit Transaction' : 'New Transaction'}</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div style={{ gridColumn: '1 / -1' }}>
            <label className="tm-label">Title *</label>
            <input className="tm-input" value={form.title} onChange={e => set('title', e.target.value)} placeholder="Transaction title" />
          </div>
          <div>
            <label className="tm-label">Amount (USD) *</label>
            <input className="tm-input" type="number" value={form.amount} onChange={e => set('amount', e.target.value)} placeholder="0.00" />
          </div>
          <div>
            <label className="tm-label">Date *</label>
            <input className="tm-input" type="date" value={form.transaction_date} onChange={e => set('transaction_date', e.target.value)} />
          </div>
          <div>
            <label className="tm-label">Type *</label>
            <select className="tm-input tm-select" value={form.transaction_type} onChange={e => set('transaction_type', e.target.value)}>
              <option value="inflow">Inflow</option>
              <option value="outflow">Outflow</option>
            </select>
          </div>
          <div>
            <label className="tm-label">Category *</label>
            <select className="tm-input tm-select" value={form.category} onChange={e => set('category', e.target.value)}>
              {CATEGORIES.map(c => <option key={c} value={c}>{c.replace('_', ' ')}</option>)}
            </select>
          </div>
          <div style={{ gridColumn: '1 / -1' }}>
            <label className="tm-label">Counterparty</label>
            <input className="tm-input" value={form.counterparty} onChange={e => set('counterparty', e.target.value)} placeholder="Client or vendor name" />
          </div>
          <div style={{ gridColumn: '1 / -1' }}>
            <label className="tm-label">Description</label>
            <textarea className="tm-input" value={form.description} onChange={e => set('description', e.target.value)}
              style={{ resize: 'vertical', minHeight: 70 }} placeholder="Optional notes..." />
          </div>
        </div>

        <div style={{ display: 'flex', gap: 10, marginTop: 20, justifyContent: 'flex-end' }}>
          <button className="tm-btn tm-btn-ghost" onClick={onClose}>Cancel</button>
          <button className="tm-btn tm-btn-primary" onClick={() => onSave(form)}>
            {initial ? 'Update' : 'Create'} Transaction
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Transactions() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [modal, setModal] = useState(null); // null | 'new' | { ...transaction }
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['transactions', page, search, typeFilter],
    queryFn: () => transactionAPI.list({
      page, search, transaction_type: typeFilter || undefined
    }).then(r => r.data),
    keepPreviousData: true,
  });

  const createMutation = useMutation({
    mutationFn: transactionAPI.create,
    onSuccess: () => { qc.invalidateQueries(['transactions']); setModal(null); toast.success('Transaction created'); },
    onError: () => toast.error('Failed to create transaction'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => transactionAPI.update(id, data),
    onSuccess: () => { qc.invalidateQueries(['transactions']); setModal(null); toast.success('Transaction updated'); },
    onError: () => toast.error('Failed to update transaction'),
  });

  const deleteMutation = useMutation({
    mutationFn: transactionAPI.delete,
    onSuccess: () => { qc.invalidateQueries(['transactions']); toast.success('Transaction deleted'); },
    onError: () => toast.error('Failed to delete'),
  });

  const handleSave = (formData) => {
    if (modal && modal.id) {
      updateMutation.mutate({ id: modal.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (id) => {
    if (window.confirm('Delete this transaction?')) deleteMutation.mutate(id);
  };

  return (
    <div>
      {modal !== null && (
        <TransactionModal
          onClose={() => setModal(null)}
          onSave={handleSave}
          initial={modal === 'new' ? null : modal}
        />
      )}

      <div className="tm-page-header">
        <div>
          <h1 className="tm-page-title">Transactions</h1>
          <p className="tm-page-sub">{data?.count || 0} total records</p>
        </div>
        <button className="tm-btn tm-btn-primary" onClick={() => setModal('new')}>
          <Plus size={14} /> New Transaction
        </button>
      </div>

      {/* Filters */}
      <div className="tm-card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
            <Search size={13} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input className="tm-input" style={{ paddingLeft: 30 }} placeholder="Search transactions..."
              value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} />
          </div>
          <select className="tm-input tm-select" style={{ width: 160 }} value={typeFilter}
            onChange={e => { setTypeFilter(e.target.value); setPage(1); }}>
            <option value="">All Types</option>
            <option value="inflow">Inflow</option>
            <option value="outflow">Outflow</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="tm-card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}><div className="tm-spinner" /></div>
        ) : (
          <table className="tm-table">
            <thead>
              <tr>
                <th>Title</th><th>Type</th><th>Category</th><th>Amount</th>
                <th>Date</th><th>Counterparty</th><th>Status</th><th></th>
              </tr>
            </thead>
            <tbody>
              {data?.results?.map(tx => (
                <tr key={tx.id}>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{tx.title}</td>
                  <td>
                    <span className={`tm-badge ${tx.transaction_type === 'inflow' ? 'tm-badge-green' : 'tm-badge-red'}`}>
                      {tx.transaction_type === 'inflow' ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
                      {tx.transaction_type}
                    </span>
                  </td>
                  <td style={{ textTransform: 'capitalize' }}>{tx.category?.replace('_', ' ')}</td>
                  <td>
                    <span className="font-mono" style={{ color: tx.transaction_type === 'inflow' ? 'var(--accent-green)' : 'var(--accent-red)', fontWeight: 600 }}>
                      {tx.transaction_type === 'outflow' ? '−' : '+'}{fmt(tx.amount)}
                    </span>
                  </td>
                  <td>{fmtDate(tx.transaction_date)}</td>
                  <td>{tx.counterparty || '—'}</td>
                  <td>
                    <span className={`tm-badge ${tx.status === 'completed' ? 'tm-badge-green' : tx.status === 'pending' ? 'tm-badge-amber' : 'tm-badge-gray'}`}>
                      {tx.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button className="tm-btn tm-btn-ghost tm-btn-sm" onClick={() => setModal(tx)}>
                        <Edit2 size={11} />
                      </button>
                      <button className="tm-btn tm-btn-danger tm-btn-sm" onClick={() => handleDelete(tx.id)}>
                        <Trash2 size={11} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination */}
        {data && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderTop: '1px solid var(--border)' }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Page {page} · {data.count} total
            </span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="tm-btn tm-btn-ghost tm-btn-sm" disabled={!data.previous} onClick={() => setPage(p => p - 1)}>← Prev</button>
              <button className="tm-btn tm-btn-ghost tm-btn-sm" disabled={!data.next} onClick={() => setPage(p => p + 1)}>Next →</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
