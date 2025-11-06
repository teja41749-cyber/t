import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);

    // Handle different types of errors
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;

      switch (status) {
        case 400:
          throw new Error(data.error || 'Bad request. Please check your input.');
        case 429:
          throw new Error('Too many requests. Please wait and try again.');
        case 500:
          throw new Error(data.error || 'Server error. Please try again later.');
        default:
          throw new Error(data.error || `Request failed with status ${status}`);
      }
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error. Please check your connection.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred.');
    }
  }
);

// API endpoints
export const nlpAPI = {
  // Extract UML from requirements text
  extractUML: async (text) => {
    const response = await api.post('/extract', { text });
    return response.data;
  },

  // Validate requirements text before processing
  validateText: async (text) => {
    const response = await api.post('/validate', { text });
    return response.data;
  },

  // Preload models to reduce first-request latency
  preloadModels: async () => {
    const response = await api.post('/models/preload');
    return response.data;
  },

  // Health check for NLP services
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export const diagramAPI = {
  // Update diagram based on user modifications
  updateDiagram: async (umlModel, changes) => {
    const response = await api.post('/update', {
      uml_model: umlModel,
      changes: changes
    });
    return response.data;
  },

  // Export diagram in various formats
  exportDiagram: async (umlModel, format) => {
    const response = await api.post('/export', {
      uml_model: umlModel,
      format: format
    });
    return response.data;
  },

  // Validate UML diagram structure
  validateDiagram: async (umlModel) => {
    const response = await api.post('/validate', {
      uml_model: umlModel
    });
    return response.data;
  },

  // Get diagram statistics
  getStatistics: async (umlModel) => {
    const response = await api.post('/statistics', {
      uml_model: umlModel
    });
    return response.data;
  },
};

export const chatAPI = {
  // Send message to Rasa chatbot
  sendMessage: async (message, senderId) => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_RASA_URL || 'http://localhost:5005'}/webhooks/rest/webhook`,
        {
          sender: senderId,
          message: message
        },
        {
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Chat API Error:', error);
      throw new Error('Chat service is currently unavailable.');
    }
  }
};

// Utility function to download files
export const downloadFile = (data, filename, type = 'text/plain') => {
  const blob = new Blob([data], { type });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export default api;