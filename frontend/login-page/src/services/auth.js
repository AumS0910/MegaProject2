import api from './api';

export const authAPI = {
    login: async (email, password) => {
        try {
            const response = await api.post('/auth/login', {
                email,
                password
            });
            
            // Store the token and user data
            if (response.data.accessToken) {
                const userData = {
                    token: response.data.accessToken,
                    id: response.data.userId,
                    name: response.data.name,
                    email: response.data.email,
                    createdDate: response.data.createdDate,
                    lastLoginDate: new Date().toISOString()
                };
                localStorage.setItem('token', `Bearer ${response.data.accessToken}`);
                localStorage.setItem('user', JSON.stringify(userData));
                
                // Set the token in axios defaults
                api.defaults.headers.common['Authorization'] = `Bearer ${response.data.accessToken}`;
                return userData;
            }
            throw new Error('Invalid response format');
        } catch (error) {
            console.error('Login error:', error);
            throw error.response?.data?.message || 'Login failed';
        }
    },

    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    register: async (userData) => {
        try {
            const response = await api.post('/auth/signup', {
                ...userData,
                createdDate: new Date().toISOString()
            });
            return response.data;
        } catch (error) {
            throw error.response?.data?.message || 'Registration failed';
        }
    },

    // Check if user is authenticated
    isAuthenticated: () => {
        const token = localStorage.getItem('token');
        return !!token;
    },

    // Get current user
    getCurrentUser: () => {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            return JSON.parse(userStr);
        }
        return null;
    },

    // Get current token
    getToken: () => {
        return localStorage.getItem('token');
    },

    // Google OAuth login
    googleLogin: async (credential) => {
        try {
            const response = await api.post('/auth/google', { credential });
            
            if (response.data.accessToken) {
                const userData = {
                    token: response.data.accessToken,
                    id: response.data.userId,
                    name: response.data.name,
                    email: response.data.email,
                    createdDate: response.data.createdDate,
                    lastLoginDate: new Date().toISOString()
                };
                localStorage.setItem('token', `Bearer ${response.data.accessToken}`);
                localStorage.setItem('user', JSON.stringify(userData));
                
                api.defaults.headers.common['Authorization'] = `Bearer ${response.data.accessToken}`;
                return userData;
            }
            throw new Error('Invalid response format');
        } catch (error) {
            console.error('Google login error:', error);
            throw error.response?.data?.message || 'Google login failed';
        }
    },

    // Facebook OAuth login
    facebookLogin: async (accessToken) => {
        try {
            const response = await api.post('/auth/facebook', { accessToken });
            
            if (response.data.accessToken) {
                const userData = {
                    token: response.data.accessToken,
                    id: response.data.userId,
                    name: response.data.name,
                    email: response.data.email,
                    createdDate: response.data.createdDate,
                    lastLoginDate: new Date().toISOString()
                };
                localStorage.setItem('token', `Bearer ${response.data.accessToken}`);
                localStorage.setItem('user', JSON.stringify(userData));
                
                api.defaults.headers.common['Authorization'] = `Bearer ${response.data.accessToken}`;
                return userData;
            }
            throw new Error('Invalid response format');
        } catch (error) {
            console.error('Facebook login error:', error);
            throw error.response?.data?.message || 'Facebook login failed';
        }
    }
};
