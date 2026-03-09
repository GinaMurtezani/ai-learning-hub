import apiClient from './client';

export async function fetchPaths() {
  const resp = await apiClient.get('paths/');
  return resp.data;
}

export async function fetchPath(slug: string) {
  const resp = await apiClient.get(`paths/${slug}/`);
  return resp.data;
}

export async function fetchLesson(slug: string) {
  const resp = await apiClient.get(`lessons/${slug}/`);
  return resp.data;
}

export async function completeLesson(slug: string) {
  const resp = await apiClient.post(`lessons/${slug}/complete/`);
  return resp.data;
}

export async function sendChatMessage(message: string, lessonId?: number, agentSlug?: string) {
  const body: { message: string; lesson_id?: number; agent_slug?: string } = { message };
  if (lessonId !== undefined) body.lesson_id = lessonId;
  if (agentSlug !== undefined) body.agent_slug = agentSlug;
  const resp = await apiClient.post('chat/', body);
  return resp.data;
}

export interface ChatAgentData {
  slug: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

export async function fetchAgents(): Promise<ChatAgentData[]> {
  const resp = await apiClient.get('chat/agents/');
  return resp.data;
}

export async function fetchProfile() {
  const resp = await apiClient.get('profile/');
  return resp.data;
}

export async function fetchLeaderboard() {
  const resp = await apiClient.get('leaderboard/');
  return resp.data;
}

export async function fetchAchievements() {
  const resp = await apiClient.get('achievements/');
  return resp.data;
}

export async function login(username: string, password: string) {
  const resp = await apiClient.post('auth/login/', { username, password });
  return resp.data;
}

export async function fetchDemoUsers() {
  const resp = await apiClient.get('auth/demo-users/');
  return resp.data;
}
