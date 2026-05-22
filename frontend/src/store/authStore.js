/**
 * TreasuryMind AI - Auth Store (Zustand)
 */

import { create } from 'zustand';
import { authAPI } from '../services/api';

const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  initialize: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isLoading: false });
      return;
    }
    try {
      const { data } = await authAPI.profile();
      set({ user: data, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.clear();
      set({ isLoading: false });
    }
  },

  login: async (email, password) => {
    const { data } = await authAPI.login(email, password);
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    set({ user: data.user, isAuthenticated: true });
    return data;
  },

  logout: async () => {
    const refresh = localStorage.getItem('refresh_token');
    try { await authAPI.logout(refresh); } catch {}
    localStorage.clear();
    set({ user: null, isAuthenticated: false });
  },

  updateUser: (userData) => set({ user: { ...get().user, ...userData } }),
}));

export default useAuthStore;
