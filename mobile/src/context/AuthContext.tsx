import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  UserProfile,
  STORAGE_KEYS,
  loginMobile,
  registerMobile,
  getMeMobile,
  logoutMobile,
} from '../api/index';

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  quickDemoLogin: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize auth state from storage on startup
  useEffect(() => {
    const initAuth = async () => {
      try {
        const savedToken = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
        if (savedToken) {
          setToken(savedToken);
          try {
            const profile = await getMeMobile();
            setUser(profile);
          } catch {
            // Token might be expired or server unreachable, keep cached profile if available
            const cachedUser = await AsyncStorage.getItem(STORAGE_KEYS.USER_PROFILE);
            if (cachedUser) {
              setUser(JSON.parse(cachedUser));
            }
          }
        }
      } catch (e) {
        console.log('Failed to restore auth session:', e);
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const data = await loginMobile(email, pass);
      setToken(data.access_token);
      const profile = await getMeMobile();
      setUser(profile);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, pass: string, name: string) => {
    setIsLoading(true);
    try {
      await registerMobile(email, pass, name);
      // Automatically login after successful registration
      await login(email, pass);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await logoutMobile();
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const quickDemoLogin = async () => {
    // Quick login for testing with default admin account
    await login('admin@travelagent.ai', 'admin123');
  };

  const refreshProfile = async () => {
    try {
      const profile = await getMeMobile();
      setUser(profile);
    } catch {
      // Ignore
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!token,
        login,
        register,
        logout,
        quickDemoLogin,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
