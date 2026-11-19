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

export async function request(path: string, { upload, ...init }: RequestInit & { upload?: 'image' | 'video' } = {}, capability?: Capability) {
  if (!base) throw new Error('The detection backend is not configured. Set VITE_AUTOSCAN_API before building.');
  const timeout = AbortSignal.timeout(upload === 'video' ? 120_000 : 65_000);
  const uploadFailure = upload && (path.startsWith('/preview?') ? `Could not validate the ${upload}.` : `Could not confirm the ${upload} submission.`);
  let response: Response;
  try {
    response = await fetch(base + '/api' + path, {
      ...init,
      credentials: 'omit',
      cache: 'no-store',
      referrerPolicy: 'no-referrer',
      signal: init.signal ? AbortSignal.any([init.signal, timeout]) : timeout,
      headers: { ...init.headers, ...(capability ? { Authorization: 'Bearer ' + capability.token } : {}) },
    });
  } catch (error) {
    if (init.signal?.aborted) throw error;
    if (timeout.aborted) throw new Error(uploadFailure
      ? `${uploadFailure} The browser timed out waiting for the server. Check your connection and try again.`
      : 'The browser timed out waiting for the server. Try again.');
    if (uploadFailure) throw new Error(`${uploadFailure} The connection to the server failed. Check your connection or try again later.`);
    throw new Error('Cannot reach the free backend. It may be waking up or unavailable. Wait, then try again.');
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new APIError(response.status, typeof body?.detail === 'string' ? body.detail :
      uploadFailure && (response.status === 408 || response.status === 504) ? `${uploadFailure} The server timed out. Check your connection and try again.` :
       upload && response.status === 413 ? `The server rejected the ${upload} because it exceeds a size limit. Check the limits above.` :
      upload && response.status === 415 ? `The server does not support this ${upload} format. Choose one of the listed formats.` :
      upload && response.status === 422 ? `The server could not validate this ${upload}. Check the file and settings, then try again.` :
      response.status === 404 ? 'Job unavailable, deleted, or expired.' :
       response.status === 429 ? 'The server is limiting requests. Wait and try again.' :
      'The free backend is busy, starting, or unavailable. Try again later.',
      response.status === 429 && typeof body?.retry_at === 'number' && body.retry_at > 0 &&
        Number.isFinite(new Date(body.retry_at * 1000).getTime()) ? body.retry_at : undefined);
  }
  return response;
}

export function jobPath(capability: Capability) {
  return '/jobs/' + capability.id;
}
