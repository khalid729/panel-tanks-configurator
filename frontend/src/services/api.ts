import { TankConfigRequest, TankConfigResponse, TankOptions } from '@/types/tank';

const API_BASE = '/api';

export async function calculateTank(request: TankConfigRequest): Promise<TankConfigResponse> {
  const response = await fetch(`${API_BASE}/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error ${response.status}`);
  }

  return response.json();
}

export async function getInputOptions(): Promise<TankOptions> {
  const response = await fetch(`${API_BASE}/options`);

  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }

  return response.json();
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
