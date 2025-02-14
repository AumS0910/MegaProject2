import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080';  // Changed from 8006 to 8080

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        // Don't add Bearer prefix if it's already there
        config.headers.Authorization = token;
    }
    return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 403 && error.response?.data?.message === 'Expired JWT token') {
            localStorage.clear();
            window.location.href = '/LoginPage';
        }
        return Promise.reject(error);
    }
);

// User Profile API endpoints
export const userAPI = {
    // Get user profile
    getUserProfile: async () => {
        try {
            const response = await api.get('/api/user/profile');
            return response.data;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            throw error;
        }
    },

    // Update user profile
    updateUserProfile: async (data) => {
        try {
            const response = await api.put('/api/user/profile', data);
            return response.data;
        } catch (error) {
            console.error('Error updating user profile:', error);
            throw error;
        }
    }
};

// Brochure API endpoints
export const brochureAPI = {
    // Generate a new brochure
    generateBrochure: async (data) => {
        try {
            // Start brochure generation
            const response = await api.post('/generate-brochure', {
                hotel_name: data.hotelName,
                location: data.location || "Not specified",
                layout: data.layout || "full_bleed"
            });

            // Get task ID from response
            const { task_id } = response.data;
            
            // Poll for task completion
            let status = 'processing';
            while (status === 'processing') {
                // Wait for 2 seconds before next poll
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Check task status
                const statusResponse = await api.get(`/task-status/${task_id}`);
                status = statusResponse.data.status;
                
                if (status === 'completed') {
                    return statusResponse.data;
                } else if (status === 'failed') {
                    throw new Error('Brochure generation failed');
                }
            }
        } catch (error) {
            console.error('Error generating brochure:', error);
            throw error;
        }
    },

    generateBrochureFromPrompt: async (data) => {
        try {
            const response = await axios.post(
                `${API_BASE_URL}/generate-brochure-from-prompt`,
                data,
                {
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.detail || 'Failed to generate brochure');
        }
    },

    // Get brochure preview
    getBrochurePreview: async (taskId) => {
        try {
            const response = await api.get(`/task-status/${taskId}`);
            return response.data;
        } catch (error) {
            console.error('Get preview error:', error);
            throw error.response?.data?.message || 'Failed to get preview';
        }
    },

    // Get recent brochures
    getRecentBrochures: async (limit = 10) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_BASE_URL}/api/brochures/recent?limit=${limit}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token
                },
                withCredentials: true
            });
            return response.data;
        } catch (error) {
            console.error('Get recent brochures error:', error);
            if (error.response?.status === 401 || error.response?.status === 403) {
                // Token expired or invalid, redirect to login
                localStorage.clear();
                window.location.href = '/LoginPage';
            }
            throw error.response?.data?.message || 'Failed to fetch recent brochures';
        }
    },

    // Download generated brochure
    downloadBrochure: async (filePath) => {
        try {
            const response = await api.get(`/download-brochure/${filePath}`, {
                responseType: 'blob'
            });
            return response.data;
        } catch (error) {
            console.error('Download brochure error:', error);
            throw error.response?.data?.message || 'Failed to download brochure';
        }
    }
};

export default api;
