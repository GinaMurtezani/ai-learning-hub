import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1/',
  headers: { 'Content-Type': 'application/json' },
});

export function setAuthHeader(username: string, password: string) {
  const encoded = btoa(`${username}:${password}`);
  apiClient.defaults.headers.common['Authorization'] = `Basic ${encoded}`;
}

export function clearAuthHeader() {
  delete apiClient.defaults.headers.common['Authorization'];
}

export default apiClient;
