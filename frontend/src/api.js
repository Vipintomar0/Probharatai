const API_BASE = '/api';

export async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(error.error || `HTTP ${response.status}`);
    }
    return response.json();
}

// Prompt & Tasks
export const executePrompt = (prompt, provider) =>
    apiRequest('/prompt', { method: 'POST', body: JSON.stringify({ prompt, provider }) });

export const getTasks = (limit = 50) => apiRequest(`/tasks?limit=${limit}`);
export const getTask = (id) => apiRequest(`/tasks/${id}`);

// Chat
export const sendChat = (message, provider) =>
    apiRequest('/chat', { method: 'POST', body: JSON.stringify({ message, provider }) });

// Jobs
export const getJobs = (limit = 100) => apiRequest(`/jobs?limit=${limit}`);

// Logs
export const getLogs = (limit = 100, level) =>
    apiRequest(`/logs?limit=${limit}${level ? `&level=${level}` : ''}`);

// Settings
export const getSettings = () => apiRequest('/settings');
export const updateSettings = (settings) =>
    apiRequest('/settings', { method: 'POST', body: JSON.stringify(settings) });

// API Keys
export const saveApiKey = (provider, api_key) =>
    apiRequest('/api-keys', { method: 'POST', body: JSON.stringify({ provider, api_key }) });
export const checkApiKey = (provider) => apiRequest(`/api-keys/${provider}`);

// Approvals
export const getApprovals = () => apiRequest('/approvals');
export const handleApproval = (id, action) =>
    apiRequest(`/approvals/${id}`, { method: 'POST', body: JSON.stringify({ action }) });

// Telegram
export const testTelegram = () => apiRequest('/telegram/test', { method: 'POST' });

// Health
export const getHealth = () => apiRequest('/health');
