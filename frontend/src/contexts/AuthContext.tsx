import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { User } from '@/types';
import api from '@/lib/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (phone: string, password: string) => Promise<void>;
  logout: () => void;
  isAdmin: boolean;
  isSuperAdmin: boolean;
  isCitizen: boolean;
  register: (name: string, phone: string, password: string) => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('nagrik_token'));
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('nagrik_token');
      if (storedToken) {
        try {
          const response = await api.get('/auth/me');
          setUser(response.data);
          setToken(storedToken);
        } catch (error) {
          console.error('[AUTH] Failed to restore session:', error);
          localStorage.removeItem('nagrik_token');
          localStorage.removeItem('nagrik_user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = useCallback(async (phone: string, password: string) => {
    const response = await api.post('/auth/login', { phone, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('nagrik_token', access_token);
    localStorage.setItem('nagrik_user', JSON.stringify(userData));

    setUser(userData);
    setToken(access_token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('nagrik_user');
    localStorage.removeItem('nagrik_token');
    setUser(null);
    setToken(null);
  }, []);

  const register = useCallback(async (name: string, phone: string, password: string) => {
    // 1. Register
    await api.post('/auth/register', { name, phone, password });

    // 2. Auto-login after registration
    await login(phone, password);
  }, [login]);

  const isAdmin = user?.role === 'department_admin' || user?.role === 'super_admin';
  const isSuperAdmin = user?.role === 'super_admin';
  const isCitizen = user?.role === 'citizen';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        login,
        logout,
        isAdmin,
        isSuperAdmin,
        isCitizen,
        register,
        isLoading
      }}
    >
      {!isLoading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
