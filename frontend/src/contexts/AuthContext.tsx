import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';
import { setAuthHeader, clearAuthHeader } from '../api/client';
import { login as apiLogin } from '../api/endpoints';

interface AuthState {
  isAuthenticated: boolean;
  username: string | null;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const saved = sessionStorage.getItem('auth');
    return saved ? JSON.parse(saved) : { isAuthenticated: false, username: null };
  });

  // Restore auth header on mount
  useEffect(() => {
    const creds = sessionStorage.getItem('authCreds');
    if (creds) {
      const { username, password } = JSON.parse(creds);
      setAuthHeader(username, password);
    }
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setAuthHeader(username, password);
    await apiLogin(username, password);
    const newState = { isAuthenticated: true, username };
    setState(newState);
    sessionStorage.setItem('auth', JSON.stringify(newState));
    sessionStorage.setItem('authCreds', JSON.stringify({ username, password }));
  }, []);

  const logout = useCallback(() => {
    clearAuthHeader();
    setState({ isAuthenticated: false, username: null });
    sessionStorage.removeItem('auth');
    sessionStorage.removeItem('authCreds');
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
