// Zustand store for global state management
import { create } from 'zustand';
import { projectsApi, agentsApi, tasksApi, filesApi, buildsApi } from '../services/api';

export const useProjectStore = create((set, get) => ({
  projects: [],
  currentProject: null,
  loading: false,
  error: null,

  fetchProjects: async () => {
    set({ loading: true, error: null });
    try {
      const response = await projectsApi.getAll();
      set({ projects: response.data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  selectProject: async (projectId) => {
    set({ loading: true });
    try {
      const response = await projectsApi.getOne(projectId);
      set({ currentProject: response.data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  createProject: async (data) => {
    set({ loading: true });
    try {
      const response = await projectsApi.create(data);
      const projects = [...get().projects, response.data];
      set({ projects, loading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  clearCurrentProject: () => set({ currentProject: null }),
}));

export const useAgentStore = create((set) => ({
  agents: [],
  selectedAgent: null,
  loading: false,

  fetchAgents: async () => {
    set({ loading: true });
    try {
      const response = await agentsApi.getAll();
      set({ agents: response.data, loading: false });
    } catch (error) {
      set({ loading: false });
    }
  },

  selectAgent: (agent) => set({ selectedAgent: agent }),
}));

export const useTaskStore = create((set, get) => ({
  tasks: [],
  loading: false,

  fetchTasks: async (projectId) => {
    set({ loading: true });
    try {
      const response = await tasksApi.getByProject(projectId);
      set({ tasks: response.data, loading: false });
    } catch (error) {
      set({ loading: false });
    }
  },

  createTask: async (data) => {
    try {
      const response = await tasksApi.create(data);
      const tasks = [...get().tasks, response.data];
      set({ tasks });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
}));

export const useFileStore = create((set, get) => ({
  files: [],
  selectedFile: null,
  loading: false,

  fetchFiles: async (projectId) => {
    set({ loading: true });
    try {
      const response = await filesApi.getByProject(projectId);
      set({ files: response.data, loading: false });
    } catch (error) {
      set({ loading: false });
    }
  },

  selectFile: (file) => set({ selectedFile: file }),
}));

export const useBuildStore = create((set) => ({
  builds: [],
  currentBuild: null,
  loading: false,

  fetchBuilds: async (projectId) => {
    set({ loading: true });
    try {
      const response = await buildsApi.getByProject(projectId);
      set({ builds: response.data || [], loading: false });
    } catch (error) {
      set({ loading: false });
    }
  },

  triggerBuild: async (projectId, buildType) => {
    try {
      const response = await buildsApi.trigger(projectId, buildType);
      set({ currentBuild: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
}));

export const useVoiceStore = create((set) => ({
  isRecording: false,
  isProcessing: false,
  lastCommand: null,
  lastTranscription: null,

  setRecording: (value) => set({ isRecording: value }),
  setProcessing: (value) => set({ isProcessing: value }),
  setLastCommand: (command) => set({ lastCommand: command }),
  setLastTranscription: (text) => set({ lastTranscription: text }),
}));
