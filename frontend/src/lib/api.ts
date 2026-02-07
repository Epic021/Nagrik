import axios from 'axios';
import { toast } from 'sonner';

const API_BASE_URL = `http://${window.location.hostname}:8000/api/v1`;

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add the JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('nagrik_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        let message = 'An unexpected error occurred';

        if (error.response?.data?.detail) {
            const detail = error.response.data.detail;
            if (typeof detail === 'string') {
                message = detail;
            } else if (Array.isArray(detail)) {
                // Handle FastAPI validation error format
                message = detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ');
            } else {
                message = JSON.stringify(detail);
            }
        }

        // Don't show toast for 401 on "me" endpoint (session check)
        const isMeEndpoint = error.config.url === '/auth/me';
        if (error.response?.status === 401 && !isMeEndpoint) {
            localStorage.removeItem('nagrik_token');
            localStorage.removeItem('nagrik_user');
            // Redirect to login if not already there
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
        } else if (!isMeEndpoint) {
            toast.error(message);
        }

        return Promise.reject(error);
    }
);

export default api;
