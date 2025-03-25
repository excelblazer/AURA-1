import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (userData) => api.put('/auth/profile', userData)
};

// Files API
export const filesAPI = {
  uploadFiles: (formData) => api.post('/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  getUploadHistory: () => api.get('/files/history')
};

// Validation API
export const validationAPI = {
  getValidationData: (jobId) => api.get(`/validation/${jobId}`),
  resolveIssue: (issueId, resolution) => api.post(`/validation/resolve/${issueId}`, { resolution })
};

// Templates API
export const templatesAPI = {
  getAllTemplates: () => api.get('/templates'),
  getTemplate: (templateId) => api.get(`/templates/${templateId}`),
  createTemplate: (templateData) => api.post('/templates', templateData),
  updateTemplate: (templateId, templateData) => api.put(`/templates/${templateId}`, templateData),
  deleteTemplate: (templateId) => api.delete(`/templates/${templateId}`),
  previewTemplate: (templateData) => api.post('/templates/preview', templateData)
};

// Processing API
export const processingAPI = {
  getJobs: () => api.get('/processing/jobs'),
  getJob: (jobId) => api.get(`/processing/jobs/${jobId}`),
  startProcessing: (jobId) => api.post(`/processing/start/${jobId}`),
  getDocuments: (jobId) => api.get(`/processing/documents/${jobId}`),
  downloadDocument: (jobId, documentId) => api.get(`/processing/documents/${jobId}/${documentId}/download`, {
    responseType: 'blob'
  }),
  previewDocumentUrl: (jobId, documentId) => `/api/processing/documents/${jobId}/${documentId}/preview`,
  getProcessingStats: () => api.get('/processing/stats'),
  getProcessingStages: () => api.get('/processing/stages'),
  getEstimatedTime: (jobId) => api.get(`/processing/estimated-time/${jobId}`)
};

// Dashboard API
export const dashboardAPI = {
  getDashboardData: () => api.get('/dashboard')
};

// OCR API
export const ocrAPI = {
  extractText: (fileId) => api.get(`/ocr/extract-text/${fileId}`),
  parsePayroll: (fileId) => api.get(`/ocr/parse-payroll/${fileId}`),
  extractTable: (fileId, pageNumber = 0) => api.get(`/ocr/extract-table/${fileId}`, {
    params: { page: pageNumber }
  })
};

export default api;
