'use client';

import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';
import api from '../lib/api';
import { User, AuthTokens } from '../types/auth';
import { ApiResponse } from '../types/api';

interface AuthContextType {
  user: User | null;
  permissions: Set<string>;
  isLoading: boolean;
  login: (tokens: AuthTokens) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const res = await api.get<ApiResponse<User>>('/auth/me');
      if (res.data.data) {
        setUser(res.data.data);
      }
    } catch {
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchProfile();
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (tokens: AuthTokens) => {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    await fetchProfile();
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsLoading(false);
  };

  const permissions = useMemo(() => {
    if (!user) return new Set<string>();
    if (user.is_superuser) return new Set<string>(['*']);
    const set = new Set<string>();
    user.roles.forEach((r) => r.permissions.forEach((p) => set.add(p.name)));
    return set;
  }, [user]);

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    if (user.is_superuser || permissions.has('*')) return true;
    return permissions.has(permission);
  };

  return (
    <AuthContext.Provider value={{ user, permissions, isLoading, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
