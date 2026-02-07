import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { User, UserRole } from '@/types';

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
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper function to generate unique citizen ID
const generateCitizenId = (): string => {
  return `citizen-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// Mock users for demo
const MOCK_USERS: Record<string, { password: string; user: User }> = {
  '9999999999': {
    password: 'admin123',
    user: {
      id: 'super-admin-1',
      name: 'Super Admin',
      phone: '9999999999',
      role: 'super_admin',
    },
  },
  '9876543211': {
    password: 'mcd123',
    user: {
      id: 'mcd-admin-1',
      name: 'MCD Admin',
      phone: '9876543211',
      role: 'department_admin',
      department_id: 'mcd',
    },
  },
  '9876543210': {
    password: 'citizen123',
    user: {
      id: 'citizen-1',
      name: 'Rahul Kumar',
      phone: '9876543210',
      role: 'citizen',
    },
  },
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('nagrik_user');
    return stored ? JSON.parse(stored) : null;
  });
  
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('nagrik_token');
  });

  const login = useCallback(async (phone: string, password: string) => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 800));

    const mockUser = MOCK_USERS[phone];
    if (!mockUser || mockUser.password !== password) {
      throw new Error('Invalid phone number or password');
    }

    const mockToken = `mock-token-${Date.now()}`;
    
    localStorage.setItem('nagrik_user', JSON.stringify(mockUser.user));
    localStorage.setItem('nagrik_token', mockToken);
    
    setUser(mockUser.user);
    setToken(mockToken);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('nagrik_user');
    localStorage.removeItem('nagrik_token');
    setUser(null);
    setToken(null);
  }, []);

  const register = useCallback(async (name: string, phone: string, password: string) => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Check if user already exists
    if (MOCK_USERS[phone]) {
      throw new Error('Phone number already registered');
    }

    // Generate unique citizen ID
    const citizenId = generateCitizenId();
    
    // Create new citizen user
    const newUser: User = {
      id: citizenId,
      name,
      phone,
      role: 'citizen',
    };

    // Store in mock users
    MOCK_USERS[phone] = {
      password,
      user: newUser,
    };

    // Create mock token
    const mockToken = `mock-token-${Date.now()}`;
    
    // Save to localStorage
    localStorage.setItem('nagrik_user', JSON.stringify(newUser));
    localStorage.setItem('nagrik_token', mockToken);
    
    setUser(newUser);
    setToken(mockToken);
  }, []);

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
      }}
    >
      {children}
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
