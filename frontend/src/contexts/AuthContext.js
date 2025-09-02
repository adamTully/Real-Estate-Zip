import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  // Configure axios interceptor for auth token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/me`);
          setUser(response.data);
          console.log('Auth check successful, user role:', response.data.role);
        } catch (error) {
          console.error('Auth check failed:', error);
          // Token might be expired, remove it
          localStorage.removeItem('auth_token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [API]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password
      });

      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('auth_token', access_token);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);

      const { access_token, user: newUser } = response.data;
      
      setToken(access_token);
      setUser(newUser);
      localStorage.setItem('auth_token', access_token);
      
      return { success: true, user: newUser };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const assignTerritory = async (zipCode) => {
    if (user && !user.owned_territories.includes(zipCode)) {
      try {
        // Call backend to assign territory
        await axios.post(`${API}/users/assign-territory`, {
          zip_code: zipCode
        });
        
        // Update local user state
        const updatedUser = {
          ...user,
          owned_territories: [...user.owned_territories, zipCode]
        };
        setUser(updatedUser);
        
        // Update localStorage to reflect the new ZIP
        localStorage.setItem('zipintel:last_zip', zipCode);
        
        // Clear any previous analysis data so dashboard loads data for the new ZIP
        localStorage.removeItem('zipintel:analysis_data');
        
        return { success: true };
      } catch (error) {
        console.error('Error assigning territory:', error);
        return { success: false, error: error.response?.data?.detail || 'Failed to assign territory' };
      }
    }
    return { success: true }; // Already assigned
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    assignTerritory
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};