import axios from 'axios';

// API base URLs
const TRIFOLD_API_URL = 'http://localhost:8009';  // For brochure generation
const AUTH_API_URL = 'http://localhost:8080';     // For authentication

// Create axios instance with default config
const api = axios.create({
    baseURL: TRIFOLD_API_URL,  // Default to trifold API
    headers: {
        'Content-Type': 'application/json',
    },
});

// Create auth API instance
export const authApi = axios.create({
    baseURL: AUTH_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
const addAuthToken = (config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = token;
    }
    return config;
};

api.interceptors.request.use(addAuthToken);
authApi.interceptors.request.use(addAuthToken);

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

// Helper functions for image and brochure URLs
const getImageUrl = (imagePath) => {
    if (!imagePath) return 'https://via.placeholder.com/400x300?text=No+Preview';
    return `${TRIFOLD_API_URL}/images/${imagePath}`;
};

const getBrochureUrl = (brochurePath) => {
    if (!brochurePath) return '#';
    return `${TRIFOLD_API_URL}/brochures/${brochurePath}`;
};

// User Profile API endpoints
export const userAPI = {
    // Get user profile
    getUserProfile: async () => {
        try {
            const response = await authApi.get('/api/user/profile');
            return response.data;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            throw error;
        }
    },

    // Update user profile
    updateUserProfile: async (data) => {
        try {
            const response = await authApi.put('/api/user/profile', data);
            return response.data;
        } catch (error) {
            console.error('Error updating user profile:', error);
            throw error;
        }
    }
};

// Brochure API endpoints
export const brochureAPI = {
    // Get recent brochures
    getRecentBrochures: async (limit = 10) => {
        try {
            const response = await api.get('/recent-brochures', { 
                params: { limit } 
            });
            
            // Transform the response to include full URLs
            return response.data.map(brochure => ({
                ...brochure,
                exteriorImage: getImageUrl(brochure.exteriorImage),
                filePath: getBrochureUrl(brochure.filePath)
            }));
        } catch (error) {
            console.error('Error fetching recent brochures:', error);
            throw error;
        }
    },

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
                    return {
                        ...statusResponse.data,
                        filePath: getBrochureUrl(statusResponse.data.filePath),
                        exteriorImage: getImageUrl(statusResponse.data.exteriorImage)
                    };
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
                `${TRIFOLD_API_URL}/generate-brochure-from-prompt`,
                data,
                {
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );
            return {
                ...response.data,
                filePath: getBrochureUrl(response.data.filePath),
                exteriorImage: getImageUrl(response.data.exteriorImage)
            };
        } catch (error) {
            throw new Error(error.response?.data?.detail || 'Failed to generate brochure');
        }
    },

    // Get brochure preview
    getBrochurePreview: async (taskId) => {
        try {
            const response = await api.get(`/task-status/${taskId}`);
            return {
                ...response.data,
                filePath: getBrochureUrl(response.data.filePath),
                exteriorImage: getImageUrl(response.data.exteriorImage)
            };
        } catch (error) {
            console.error('Get preview error:', error);
            throw error.response?.data?.message || 'Failed to get preview';
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
