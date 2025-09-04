import { api } from './api';

// AI API endpoints
export const aiApi = {
  // Analyze scan with AI
  analyzeScan: (scanId: number) => 
    api.post(`/ai/analyze/${scanId}`),

  // Get AI insights for dashboard
  getInsights: (scanId: number) => 
    api.get(`/ai/insights/${scanId}`),

  // Generate AI report
  generateReport: (scanId: number) => 
    api.post(`/ai/generate-report/${scanId}`),

  // Enhance recommendations with AI
  enhanceRecommendations: (scanId: number) => 
    api.post(`/ai/enhance-recommendations/${scanId}`),

  // Get AI service status
  getStatus: () => 
    api.get('/ai/status'),
};
