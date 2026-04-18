import type { Application } from './types';

const BASE = 'http://localhost:8001';

export async function getApplications(): Promise<Application[]> {
  const res = await fetch(`${BASE}/applications`);
  if (!res.ok) throw new Error('Failed to fetch applications');
  return res.json();
}

export async function createApplication(data: Omit<Application, 'id' | 'last_updated' | 'is_manual'>): Promise<Application> {
  const res = await fetch(`${BASE}/applications`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateApplication(id: number, data: Partial<Application>): Promise<Application> {
  const res = await fetch(`${BASE}/applications/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteApplication(id: number): Promise<void> {
  const res = await fetch(`${BASE}/applications/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete');
}

export async function syncEmails(): Promise<{ added: number; updated: number; skipped: number }> {
  const res = await fetch(`${BASE}/sync`, { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getAuthStatus(): Promise<{ connected: boolean; reason?: string }> {
  const res = await fetch(`${BASE}/auth/status`);
  return res.json();
}

export async function getAuthUrl(): Promise<string> {
  const res = await fetch(`${BASE}/auth/login`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail ?? 'Failed to get auth URL');
  if (!data.url) throw new Error('Backend did not return an auth URL');
  return data.url;
}
