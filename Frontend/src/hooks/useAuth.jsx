import { useState, useEffect, createContext, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://localhost:8000';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    // Load user from localStorage on mount
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    // Login function
    const login = async (email, password) => {
        try {
            const response = await fetch(`${API_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                const errorMessage = Array.isArray(data.detail)
                    ? data.detail.map(err => err.msg).join(', ')
                    : (data.detail || 'Login failed');
                throw new Error(errorMessage);
            }

            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            setToken(data.access_token);
            setUser(data.user);

            return data;
        } catch (err) {
            console.error("Login error:", err);
            if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
                throw new Error('Unable to connect to the server. Is the backend running?');
            }
            throw err;
        }
    };

    // Register function
    const register = async (email, password, name) => {
        try {
            const response = await fetch(`${API_URL}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, name }),
            });

            const data = await response.json();

            if (!response.ok) {
                const errorMessage = Array.isArray(data.detail)
                    ? data.detail.map(err => err.msg).join(', ')
                    : (data.detail || 'Registration failed');
                throw new Error(errorMessage);
            }

            // We do NOT set the token here anymore, to allow the user to log in manually.
            // If auto-login is desired in the future, uncomment these lines:
            // localStorage.setItem('token', data.access_token);
            // localStorage.setItem('user', JSON.stringify(data.user));
            // setToken(data.access_token);
            // setUser(data.user);

            return data;
        } catch (err) {
            console.error("Registration error:", err);
            if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
                throw new Error('Unable to connect to the server. Is the backend running?');
            }
            throw err;
        }
    };

    // Logout function
    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setToken(null);
        setUser(null);
        navigate('/auth');
    };

    // Get current user info
    const getCurrentUser = async () => {
        if (!token) return null;

        const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            logout();
            return null;
        }

        const data = await response.json();
        setUser(data);
        localStorage.setItem('user', JSON.stringify(data));
        return data;
    };

    // Authenticated fetch wrapper
    const authFetch = async (url, options = {}) => {
        if (!token) {
            throw new Error('No authentication token');
        }

        const response = await fetch(`${API_URL}${url}`, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (response.status === 401) {
            logout();
            throw new Error('Session expired');
        }

        return response;
    };

    const value = {
        user,
        token,
        loading,
        login,
        register,
        logout,
        getCurrentUser,
        authFetch,
        isAuthenticated: !!token,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
