// API Service for AgentForge Mobile App
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_URL = 'https://ai-agent-team.preview.emergentagent.com/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Projects
export const projectsApi = {
  getAll: () => api.get('/projects'),
  getOne: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

// Agents
export const agentsApi = {
  getAll: () => api.get('/agents'),
  getOne: (id) => api.get(`/agents/${id}`),
};

// Tasks
export const tasksApi = {
  getByProject: (projectId) => api.get(`/tasks?project_id=${projectId}`),
  create: (data) => api.post('/tasks', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
};

// Files
export const filesApi = {
  getByProject: (projectId) => api.get(`/files?project_id=${projectId}`),
  getOne: (id) => api.get(`/files/${id}`),
  create: (data) => api.post('/files', data),
  update: (id, data) => api.put(`/files/${id}`, data),
  delete: (id) => api.delete(`/files/${id}`),
};

// Builds
export const buildsApi = {
  list: () => api.get('/god-mode/sessions'),
  getByProject: (projectId) => api.get(`/builds/${projectId}`),
  trigger: (projectId, buildType) => api.post('/celery/jobs/submit', null, { 
    params: { project_id: projectId, job_type: buildType || 'build' }
  }),
  getStatus: (jobId) => api.get(`/celery/jobs/${jobId}`),
  createGodMode: (prompt, template) => api.post('/god-mode/create', { prompt, template }),
};

// Voice Commands
export const voiceApi = {
  getCommands: () => api.get('/voice/commands'),
  transcribe: async (audioUri) => {
    const formData = new FormData();
    formData.append('file', {
      uri: audioUri,
      type: 'audio/m4a',
      name: 'recording.m4a',
    });
    return api.post('/voice/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  processCommand: async (audioUri, projectId) => {
    const formData = new FormData();
    formData.append('file', {
      uri: audioUri,
      type: 'audio/m4a',
      name: 'recording.m4a',
    });
    return api.post(`/voice/command?project_id=${projectId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  parseText: (text) => api.post('/voice/parse', null, { params: { text } }),
};

// Deploy
export const deployApi = {
  getPlatforms: () => api.get('/deploy/platforms'),
  getDeployments: (projectId) => api.get(`/cloud-deploy/deployments?project_id=${projectId}`),
  deploy: (projectId, platform) => api.post('/cloud-deploy/instant', null, {
    params: { project_id: projectId, platform }
  }),
};

// Chat
export const chatApi = {
  send: (projectId, message, agentId) => api.post('/chat', { 
    project_id: projectId, 
    message, 
    agent_id: agentId 
  }),
  getHistory: (projectId) => api.get(`/chat/history?project_id=${projectId}`),
};

// Health
export const healthApi = {
  check: () => api.get('/health'),
  getFeatures: () => api.get('/'),
};

export default api;
