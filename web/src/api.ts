export type Capability = { id: string; token: string };
export type ObjectType = 'vehicle' | 'logo' | 'plate';
export type Detection = {
  object_type: ObjectType;
  class_name: string;
  label: string;
  confidence: number;
  bbox: [number, number, number, number];
  frame_index?: number;
  timestamp_seconds?: number;
};
export type Job = {
  state: 'queued' | 'processing' | 'cancelling' | 'success' | 'empty' | 'error' | 'cancelled';
  width: number;
  height: number;
  filename: string;
  settings: { types: ObjectType[]; confidence: number };
  detections: Detection[];
  error: string | null;
  retry_at?: number;
  expires_at: number | null;
  media_type: 'image' | 'video';
  frame_count?: number;
  processed_frames?: number;
  duration_seconds?: number;
  queue_position: number | null;
};

const base = (import.meta.env.VITE_AUTOSCAN_API ?? '').replace(/\/$/, '');
export const developerMode = base === 'http://127.0.0.1:7862';

export class APIError extends Error {
  constructor(readonly status: number, message: string, readonly retry_at?: number) { super(message); }
}

export async function request(path: string, init: RequestInit = {}, capability?: Capability) {
  if (!base) throw new Error('The detection backend is not configured. Set VITE_AUTOSCAN_API before building.');
  let response: Response;
  try {
    response = await fetch(base + '/api' + path, {
      ...init,
      credentials: 'omit',
      cache: 'no-store',
      referrerPolicy: 'no-referrer',
      signal: init.signal ? AbortSignal.any([init.signal, AbortSignal.timeout(65_000)]) : AbortSignal.timeout(65_000),
      headers: { ...init.headers, ...(capability ? { Authorization: 'Bearer ' + capability.token } : {}) },
    });
  } catch (error) {
    if (init.signal?.aborted) throw error;
    throw new Error('Cannot reach the free backend. It may be waking up or unavailable. Wait, then try again.');
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new APIError(response.status, typeof body?.detail === 'string' ? body.detail :
      response.status === 404 ? 'Job unavailable, deleted, or expired.' :
      response.status === 429 ? 'The free backend quota is exhausted. Try again later.' :
      'The free backend is busy, starting, or unavailable. Try again later.',
      response.status === 429 && typeof body?.retry_at === 'number' && body.retry_at > 0 &&
        Number.isFinite(new Date(body.retry_at * 1000).getTime()) ? body.retry_at : undefined);
  }
  return response;
}

export function jobPath(capability: Capability) {
  return '/jobs/' + capability.id;
}
