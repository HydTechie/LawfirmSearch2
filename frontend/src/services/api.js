const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  constructor() {
    this.controller = new AbortController();

    // Bind methods so `this` always refers to the instance
    this.request = this.request.bind(this);
    this.abortRequests = this.abortRequests.bind(this);
    this.checkHealth = this.checkHealth.bind(this);
    this.ingestDocuments = this.ingestDocuments.bind(this);
    this.queryDocuments = this.queryDocuments.bind(this);
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      signal: this.controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
        return null;
      }
      throw error;
    }
  }

  abortRequests() {
    this.controller.abort();
    this.controller = new AbortController();
  }

  // Health endpoint
  async checkHealth() {
    return this.request('/health', { method: 'GET' });
  }

  // Ingest endpoint
  async ingestDocuments(data) {
    return this.request('/ingest', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Query endpoint
  async queryDocuments(data) {
    return this.request('/query', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Always use the instance
export const apiService = new ApiService();
