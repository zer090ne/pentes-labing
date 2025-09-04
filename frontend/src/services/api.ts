import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized, redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const scanApi = {
  create: (data: any) => api.post('/scans/', data),
  getAll: (params?: any) => api.get('/scans/', { params }),
  getById: (id: number) => api.get(`/scans/${id}`),
  getResults: (id: number) => api.get(`/scans/${id}/results`),
  stop: (id: number) => api.post(`/scans/${id}/stop`),
  delete: (id: number) => api.delete(`/scans/${id}`),
  getRecommendations: (id: number) => api.get(`/scans/${id}/recommendations`),
};

export const toolApi = {
  runNmap: (data: any) => api.post('/tools/nmap', data),
  runNikto: (data: any) => api.post('/tools/nikto', data),
  runHydra: (data: any) => api.post('/tools/hydra', data),
  runSqlmap: (data: any) => api.post('/tools/sqlmap', data),
  runGobuster: (data: any) => api.post('/tools/gobuster', data),
  getStatus: (taskId: string) => api.get(`/tools/status/${taskId}`),
  getAvailable: () => api.get('/tools/available'),
};

export const reportApi = {
  create: (data: any) => api.post('/reports/', data),
  getAll: (params?: any) => api.get('/reports/', { params }),
  getById: (id: number) => api.get(`/reports/${id}`),
  download: (id: number) => api.get(`/reports/${id}/download`, { responseType: 'blob' }),
  getByScan: (scanId: number) => api.get(`/reports/scan/${scanId}`),
  delete: (id: number) => api.delete(`/reports/${id}`),
};

export const authApi = {
  login: (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  register: (data: any) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
};
