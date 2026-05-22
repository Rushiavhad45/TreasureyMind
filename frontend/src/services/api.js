/**
 * TreasuryMind AI - API Service Layer
 * Centralized Axios instance with auth interceptors
 */

import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Request interceptor: attach JWT ─────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ─── Response interceptor: auto-refresh token ────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_BASE}/auth/token/refresh/`, { refresh });
          localStorage.setItem('access_token', data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  login: (email, password) => api.post('/auth/login/', { email, password }),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  profile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  users: (params) => api.get('/auth/users/', { params }),
  createUser: (data) => api.post('/auth/users/', data),
};

// ─── Transactions ─────────────────────────────────────────────────────────────
export const transactionAPI = {
  list: (params) => api.get('/transactions/', { params }),
  create: (data) => api.post('/transactions/', data),
  get: (id) => api.get(`/transactions/${id}/`),
  update: (id, data) => api.patch(`/transactions/${id}/`, data),
  delete: (id) => api.delete(`/transactions/${id}/`),
  summary: (params) => api.get('/transactions/summary/', { params }),
};

// ─── Forecasting ──────────────────────────────────────────────────────────────
export const forecastAPI = {
  list: () => api.get('/forecasting/'),
  latest: () => api.get('/forecasting/latest/'),
  trigger: (data) => api.post('/forecasting/trigger/', data),
};

// ─── Allocation ───────────────────────────────────────────────────────────────
export const allocationAPI = {
  list: (params) => api.get('/allocation/', { params }),
  get: (id) => api.get(`/allocation/${id}/`),
};

// ─── Alerts ───────────────────────────────────────────────────────────────────
export const alertAPI = {
  list: (params) => api.get('/alerts/', { params }),
  stats: () => api.get('/alerts/stats/'),
  acknowledge: (id) => api.post(`/alerts/${id}/acknowledge/`),
};

// ─── Approvals ────────────────────────────────────────────────────────────────
export const approvalAPI = {
  list: (params) => api.get('/approvals/', { params }),
  decide: (id, decision, comments) => api.post(`/approvals/${id}/decide/`, { decision, comments }),
  auditLogs: (params) => api.get('/approvals/audit-logs/', { params }),
};

// ─── Agents ───────────────────────────────────────────────────────────────────
export const agentAPI = {
  status: () => api.get('/agents/status/'),
  logs: (params) => api.get('/agents/logs/', { params }),
  trigger: () => api.post('/agents/trigger/'),
};

export default api;
