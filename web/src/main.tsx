import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource/red-hat-display/latin-600.css';
import '@fontsource/red-hat-display/latin-900.css';
import '@fontsource/red-hat-text/latin-400.css';
import '@fontsource/red-hat-text/latin-500.css';
import { APIError, developerMode, jobPath, request, type Capability, type Job, type ObjectType } from './api';
import { Showcase } from './showcase';
import { Icon } from './icon';
import { SiteFooter, SiteHeader } from './site';
import './style.css';

const objectTypes: { value: ObjectType; label: string; note: string }[] = [
  { value: 'vehicle', label: 'Vehicles', note: 'Cars, trucks, buses' },
  { value: 'logo', label: 'Logos', note: '24 vehicle brands' },
  { value: 'plate', label: 'Plates', note: 'Detection, not transcription' },
];
const resultTypes: Record<ObjectType, string> = { vehicle: 'Vehicle', logo: 'Brand', plate: 'Plate' };
const states = {
  queued: 'Queued. Your media is waiting for the single inference slot.',
  processing: 'Processing. The free GPU may need to start or wait for capacity.',
  cancelling: 'Cancelling. Waiting for the current detector to reach a safe stopping point.',
  success: 'Detection complete.',
  empty: 'Detection complete. No objects matched your selection and confidence.',
  error: 'Detection failed. This is not an empty result.',
  cancelled: 'Cancelled. Server-side source and partial results have been removed.',
};
const activeStates: Job['state'][] = ['queued', 'processing', 'cancelling'];
const pageSize = 25;
const idleNotice = 'Detection starts only when you select Detect.';

function QuotaReset({ retryAt }: { retryAt: number }) {
  const reset = new Date(retryAt * 1000);
  return <>Free GPU quota is exhausted. Try again after <time dateTime={reset.toISOString()}>
    {reset.toLocaleString(undefined, { timeZoneName: 'short' })}</time> (your local time).
    {' '}GPU availability is not guaranteed.</>;
}

function Workspace() {
  const [media, setMedia] = useState<'image' | 'video'>(() => window.location.hash === '#video' ? 'video' : 'image');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState('');
  const [ready, setReady] = useState(false);
  const [types, setTypes] = useState<ObjectType[]>(['vehicle', 'logo', 'plate']);
  const [confidence, setConfidence] = useState(40);
  const [capability, setCapability] = useState<Capability | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [annotated, setAnnotated] = useState('');
  const [error, setError] = useState<string | APIError>('');
  const [working, setWorking] = useState(false);
  const [retry, setRetry] = useState(0);
  const [pollFailed, setPollFailed] = useState(false);
  const [downloading, setDownloading] = useState('');
  const [page, setPage] = useState(0);
  const [notice, setNotice] = useState(idleNotice);
  const input = useRef<HTMLInputElement>(null);
  const settings = useRef<HTMLElement>(null);
  const focusUpload = useRef(false);
  const downloadController = useRef<AbortController | null>(null);
  const downloadURL = useRef('');
  const locked = !!capability || working;
  const active = capability && (!job || activeStates.includes(job.state));
  const video = media === 'video';

  function selectMedia(next: 'image' | 'video') {
    if (next === media) return;
    if (locked) { window.history.replaceState(null, '', '#' + media); return; }
    setMedia(next); setFile(null); setReady(false); setPreview(''); setError('');
    if (input.current) input.current.value = '';
    setNotice(idleNotice);
  }

  useEffect(() => {
    function syncMedia() {
      const hash = window.location.hash;
      if (hash !== '#image' && hash !== '#video' && hash !== '') return;
      selectMedia(hash === '#video' ? 'video' : 'image');
    }
    window.addEventListener('hashchange', syncMedia);
    return () => window.removeEventListener('hashchange', syncMedia);
  }, [media, locked]);

  useEffect(() => {
    setDownloading('');
    return () => {
      downloadController.current?.abort();
      URL.revokeObjectURL(downloadURL.current);
      downloadURL.current = '';
    };
  }, [capability]);

  useEffect(() => {
    if (!locked && focusUpload.current) {
      input.current?.focus({ preventScroll: true });
      settings.current?.scrollIntoView({ block: 'start' });
      focusUpload.current = false;
    }
  }, [locked]);

  function forgetJob(message: string) {
    downloadController.current?.abort();
    setCapability(null); setJob(null); setAnnotated(''); setPage(0); setPollFailed(false); setNotice(message);
  }

  useEffect(() => {
    if (!file) { setPreview(''); setReady(false); return; }
    const controller = new AbortController();
    const urls: string[] = [];
    setPreview('');
    setReady(false);
    setNotice('Validating the file and preparing its preview. No inference has started.');
    request('/preview?' + new URLSearchParams({ filename: file.name }),
      { method: 'POST', body: file, signal: controller.signal })
      .then(response => response.blob())
      .then(blob => {
        if (controller.signal.aborted) return;
        const url = URL.createObjectURL(blob);
        urls.push(url);
        setPreview(url);
        setReady(true);
        setNotice(`${video ? 'Video' : 'Image'} ready. Choose object types and confidence, then Detect ${media}.`);
      })
      .catch((reason: Error) => { if (!controller.signal.aborted) setError(reason.message); });
    return () => { controller.abort(); urls.forEach(url => URL.revokeObjectURL(url)); };
  }, [file]);

  useEffect(() => {
    if (!capability) return;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout>;
    let url = '';
    setPollFailed(false);
    async function poll() {
      try {
        const response = await request(jobPath(capability!), { signal: controller.signal }, capability!);
        const next: Job = await response.json();
        if (controller.signal.aborted) return;
        setJob(next);
        setNotice(next.state === 'queued' ? `Queued. Position ${next.queue_position ?? 1} in the pending queue.` :
          next.media_type === 'video' && next.state === 'processing' ?
            next.processed_frames === next.frame_count ? 'All frames processed. Finalizing and verifying the complete MP4.' :
            next.processed_frames ? `Processing frame ${next.processed_frames} of ${next.frame_count}. Every frame is included.` :
            'Waiting for the free GPU or preparing the first frame. No frames processed yet.' : states[next.state]);
        if (activeStates.includes(next.state)) {
          timer = setTimeout(poll, 1200);
        } else if (next.state === 'success' || next.state === 'empty') {
          timer = setTimeout(() => {
            forgetJob('Results expired and are no longer available. You can run a new detection.');
          }, Math.max(0, (next.expires_at! * 1000) - Date.now()));
          const image = await request(jobPath(capability!) + (next.media_type === 'video' ? '/video' : '/image'), { signal: controller.signal }, capability!);
          const blob = await image.blob();
          if (controller.signal.aborted) return;
          url = URL.createObjectURL(blob);
          setAnnotated(url);
        }
      } catch (reason) {
        if (!controller.signal.aborted) {
          if (reason instanceof APIError && reason.status === 404) {
            forgetJob('This job is no longer available. It may have expired or the backend restarted.');
            return;
          }
          setError((reason as Error).message);
          setPollFailed(true);
        }
      }
    }
    void poll();
    return () => { controller.abort(); clearTimeout(timer); if (url) URL.revokeObjectURL(url); };
  }, [capability, retry]);

  async function detect() {
    if (!file || !ready || !types.length || locked) return;
    setWorking(true); setError(''); setNotice('Uploading for detection. A cold start can take a while.');
    try {
      const response = await request('/jobs?' + new URLSearchParams({
        filename: file.name, types: types.join(','), confidence: String(confidence),
      }), { method: 'POST', body: file });
      setCapability(await response.json());
    } catch (reason) { setError(reason instanceof APIError ? reason : (reason as Error).message); }
    finally { setWorking(false); }
  }

  async function cancel() {
    if (!capability) return;
    setWorking(true); setError('');
    try {
      await request(jobPath(capability) + '/cancel', { method: 'POST' }, capability);
      setRetry(value => value + 1);
    } catch (reason) { setError((reason as Error).message); }
    finally { setWorking(false); }
  }

  async function download(format: 'image' | 'video' | 'json' | 'csv') {
    if (!capability || !file || downloading) return;
    const controller = new AbortController();
    downloadController.current = controller;
    const label = format === 'image' || format === 'video' ? `Annotated ${format}` : format.toUpperCase();
    setDownloading(format); setError(''); setNotice(`Preparing ${label} download…`);
    try {
      const response = await request(jobPath(capability) + '/download/' + format,
        { signal: controller.signal }, capability);
      const blob = await response.blob();
      if (controller.signal.aborted) return;
      URL.revokeObjectURL(downloadURL.current);
      downloadURL.current = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadURL.current;
      const sourceName = file.name.replace(/\.[^.]+$/, '').replace(/[<>:"/\\|?*\p{Cc}]/gu, '_').trim() || 'autoscan';
      link.download = format === 'video' ? `autoscan-${capability.id}.mp4` :
        `${sourceName}_${format === 'image' ? 'annotated.png' : `detections.${format}`}`;
      document.body.append(link);
      link.click();
      link.remove();
      setNotice(`${label} download sent to your browser.`);
    } catch (reason) {
      if (controller.signal.aborted) return;
      if (reason instanceof APIError && reason.status === 404) {
        forgetJob('Downloads are no longer available. The job was deleted, expired, or lost on restart. Run a new detection.');
      } else {
        setError(`${label} download failed. ${(reason as Error).message} Select the download again to retry.`);
      }
    } finally {
      if (!controller.signal.aborted) setDownloading('');
    }
  }

  async function remove(keepSource = false) {
    if (!capability || !window.confirm('Delete this job and its remaining server-side results? This cannot be undone.')) return;
    setWorking(true); setError('');
    try {
      try { await request(jobPath(capability), { method: 'DELETE' }, capability); }
      catch (reason) { if (!(reason instanceof APIError && reason.status === 404)) throw reason; }
      forgetJob(keepSource ? `Server results cleared. Change your media or settings, then select Detect ${media}.` :
        'Job deleted or already unavailable. Its access key no longer works. Active compute stops at the next safe boundary.');
      if (!keepSource) {
        setFile(null);
        if (input.current) input.current.value = '';
      }
      focusUpload.current = true;
    } catch (reason) { setError((reason as Error).message); }
    finally { setWorking(false); }
  }

  return <>
    <a className="skip" href="#workspace">Skip to detector</a>
    <SiteHeader detector />
    <main id="workspace" className="shell" tabIndex={-1}>
      <div className="intro"><h1>Image &amp; video detector</h1>
        <p>Find vehicles, brand logos and Moroccan plates in your own media.</p>
        {developerMode && <p>Local developer mode. Detection uses your personal Hugging Face quota.</p>}</div>
      <section ref={settings} id="settings" className="controls" aria-label="Media and detection settings">
        <h2 className="controls-heading">Detection setup</h2>
        <div className="upload">
          <fieldset className="media-choice" disabled={locked}>
            <legend>Input file</legend>
            <div className="media-options">{(['image', 'video'] as const).map(type => <label key={type}>
              <input className="choice-input" type="radio" name="media-type" value={type} checked={media === type}
                onChange={() => { selectMedia(type); window.location.hash = type; }} />
              <Icon name={type} />{type === 'image' ? 'Image' : 'Video'}
            </label>)}</div>
          </fieldset>
          <label htmlFor="image" className="sr-only">Source {media}</label>
          <div className="file-picker">
            <span className="file-icon" aria-hidden="true"><Icon name={file ? media : 'upload'} /></span>
            <span className="file-copy" aria-hidden="true"><strong>{file?.name ?? `Choose ${video ? 'a video' : 'an image'}`}</strong>
              {file && <small>{locked ? 'Source selected' : 'Choose a different file'}</small>}</span>
            <input ref={input} id="image" type="file" accept={video ? '.mp4,.mov,.avi,.asf,.m4v,.mpeg' : '.png,.jpg,.jpeg,.bmp,.webp'} disabled={locked}
            aria-describedby="image-help" onChange={event => {
              const next = event.target.files?.[0];
              setError('');
              if (!next) return;
              if (next.size > (video ? 20_000_000 : 10_000_000) ||
                !(video ? /\.(mp4|mov|avi|asf|m4v|mpeg)$/i : /\.(png|jpe?g|bmp|webp)$/i).test(next.name)) {
                setFile(null); setReady(false); event.target.value = '';
                setError(`Choose a supported ${media} up to ${video ? 20 : 10} MB.`); return;
              }
              setReady(false); setFile(next);
            }} />
          </div>
          <p id="image-help">{video ? 'MP4, MOV, AVI, ASF, M4V or MPEG. Up to 20 MB, 10 seconds, 1080p and 600 frames. Video output is silent.' :
            'PNG, JPG, BMP or WebP. Up to 10 MB and 12 megapixels.'}</p>
        </div>
        <fieldset disabled={locked}>
          <legend>Object types</legend>
          <div className="types">{objectTypes.map(type => <label className={`type-choice ${type.value}`} key={type.value}>
            <input className="choice-input" type="checkbox" aria-label={type.label} aria-describedby={`${type.value}-help`} checked={types.includes(type.value)} onChange={event => {
              setTypes(event.target.checked ? [...types, type.value] : types.filter(value => value !== type.value));
            }} /><Icon name={type.value} /><span>{type.label}<small id={`${type.value}-help`}>{type.note}</small></span>
            <span className="choice-mark"><Icon name="check" /></span>
          </label>)}</div>
        </fieldset>
        <div className="confidence">
          <div className="confidence-heading"><label htmlFor="confidence">Confidence</label><output htmlFor="confidence">{confidence}%</output></div>
          <input id="confidence" type="range" min="25" max="100" step="1" value={confidence} aria-valuetext={`${confidence}%`} disabled={locked}
            onChange={event => setConfidence(Number(event.target.value))} />
          <div className="range-limits" aria-hidden="true"><span>25%</span><span>100%</span></div>
          <p>Lower the threshold to include more predictions.</p>
        </div>
        <div className="actions">
          <button className="primary" onClick={() => void detect()} disabled={!ready || !types.length || locked}>
            <Icon name="scan" />{working && !capability ? 'Uploading…' : `Detect ${media}`}</button>
          {active && <button onClick={() => void cancel()} disabled={working || job?.state === 'cancelling'}>Cancel</button>}
          {capability && <button onClick={() => void remove()} disabled={working}>Delete now</button>}
        </div>
        <div className="feedback">
          <p role="status" aria-live="polite"><Icon name={job?.state === 'success' || job?.state === 'empty' ? 'check' : 'info'} /><span>{!types.length ? 'Select at least one object type.' : notice}</span></p>
          {job?.media_type === 'video' && job.state === 'processing' && !!job.processed_frames &&
            <progress aria-label="Frames processed" value={job.processed_frames} max={job.frame_count} />}
          {error && <p role="alert" className="error"><Icon name="alert" /><span>{error instanceof APIError ?
            error.retry_at ? <QuotaReset retryAt={error.retry_at} /> : error.message : error}</span></p>}
          {pollFailed && <button onClick={() => { setError(''); setRetry(value => value + 1); }}>Retry job status</button>}
          {file && !ready && error && <button onClick={() => { setError(''); setFile(new File([file], file.name)); }}>Retry {media} validation</button>}
        </div>
      </section>
      <section className="comparison" aria-label="Source and detection comparison" aria-busy={!!active}>
        <figure><figcaption><Icon name={media} /><h2>Original</h2><span>{file?.name || 'Source preview'}</span></figcaption>
          <div className="image-stage">{preview ? video ?
            <video src={preview} controls playsInline preload="metadata" aria-label="Source video preview"
              onError={() => setError('Your browser could not play the video preview. Try another browser or re-export the clip.')} /> :
            <img src={preview} alt="Selected source, normalized for detection" /> :
            <p className="stage-message"><Icon name={media} /><strong>{file ? error ? 'Preview unavailable' : 'Preparing preview' : `No ${media} selected`}</strong></p>}</div></figure>
        <figure><figcaption><Icon name="scan" /><h2>Detections</h2><span>{job ? `${job.width} × ${job.height} pixels` : 'Annotated result'}</span></figcaption>
          <div className="image-stage">{annotated ? job?.media_type === 'video' ?
            <video src={annotated} controls playsInline preload="metadata" aria-label="Annotated silent video"
              onError={() => setError('Your browser could not play the annotated MP4. Try another browser; JSON and CSV remain available.')} /> :
            <img src={annotated} alt={`Annotated result with ${job?.detections.length ?? 0} detections`} /> :
            <p className="stage-message"><Icon name="scan" /><strong>{job ? 'Detection output' : 'No results yet'}</strong><span>{job ? states[job.state] : 'Run detection to see what the models find.'}</span></p>}</div></figure>
      </section>
      {job && <section className="results" aria-labelledby="result-heading">
        <div className="result-heading"><h2 id="result-heading">Detection details</h2>
          <div className="result-summary"><span><strong>{job.detections.length}</strong> detections</span><span><strong>{job.settings.confidence}%</strong> min. confidence</span></div></div>
        {job.error && <p className="error" role="alert">{job.retry_at ? <QuotaReset retryAt={job.retry_at} /> : job.error}</p>}
        {job.media_type === 'video' && <p>{job.frame_count} frames, {job.duration_seconds?.toFixed(3)} seconds.
          Frame-level observations are repeated detections, not tracked or unique objects. Frame indices start at zero; timestamps start at the first source frame.</p>}
        {job.state === 'empty' && <p>No matching objects found. Change your media or settings to try another source or lower confidence.</p>}
        {(job.state === 'success' || job.state === 'empty') && <div className="downloads">
          <h3 id="download-heading">Download results</h3>
          <div className="actions" role="group" aria-labelledby="download-heading" aria-describedby="download-help" aria-busy={!!downloading}>
            <button onClick={() => void download(job.media_type === 'video' ? 'video' : 'image')} disabled={working || !!downloading}><Icon name="download" />
              {downloading === 'image' || downloading === 'video' ? 'Preparing media…' :
                job.media_type === 'video' ? 'Download annotated video (MP4)' : 'Download annotated image (PNG)'}</button>
            <button onClick={() => void download('json')} disabled={working || !!downloading}><Icon name="download" />
              {downloading === 'json' ? 'Preparing JSON…' : 'Download JSON'}</button>
            <button onClick={() => void download('csv')} disabled={working || !!downloading}><Icon name="download" />
              {downloading === 'csv' ? 'Preparing CSV…' : 'Download CSV'}</button>
          </div>
          <p id="download-help">Includes all {job.detections.length} selected {job.detections.length === 1 ? 'detection' : 'detections'}. Saved files stay on your device after Delete now.</p>
        </div>}
        {!activeStates.includes(job.state) &&
           <button className="change-settings" onClick={() => void remove(true)} disabled={working}><Icon name="tune" />Change {media} or settings</button>}
        {job.detections.length > pageSize && <div className="actions pagination" aria-label="Detection pages">
          <button disabled={page === 0} onClick={() => setPage(value => value - 1)}>Previous detections</button>
           <span>Page {page + 1} of {Math.ceil(job.detections.length / pageSize)}</span>
          <button disabled={(page + 1) * pageSize >= job.detections.length} onClick={() => setPage(value => value + 1)}>Next detections</button>
        </div>}
        {job.detections.length > 0 && <table>
          <caption>Pixel coordinates refer to the {job.width} × {job.height} oriented input, measured from its top-left corner.</caption>
          <thead><tr><th>Object</th><th>Model class</th><th>Confidence</th>{job.media_type === 'video' && <th>Frame / time</th>}<th>Box (x1, y1, x2, y2)</th></tr></thead>
          <tbody>{job.detections.slice(page * pageSize, (page + 1) * pageSize).map((detection, index) => <tr key={index}>
            <td data-label="Object"><span className={'type-label ' + detection.object_type}>{resultTypes[detection.object_type]}</span></td>
            <td data-label="Model class" className="model-class">{detection.object_type === 'plate' ? 'Plate' :
              detection.class_name === 'bmw' || detection.class_name === 'kia' ? detection.class_name.toUpperCase() : detection.class_name}</td>
            <td data-label="Confidence">{(detection.confidence * 100).toFixed(1)}%</td>
            {job.media_type === 'video' && <td data-label="Frame / time">{detection.frame_index} / {detection.timestamp_seconds?.toFixed(3)} s</td>}
            <td data-label="Box" className="coordinates">{detection.bbox.map(value => value.toFixed(1)).join(', ')}</td>
          </tr>)}</tbody>
        </table>}
         {job.expires_at && <p className="result-expiry">Server results expire at <time dateTime={new Date(job.expires_at * 1000).toISOString()}>
          {new Date(job.expires_at * 1000).toLocaleTimeString()}</time>, 30 minutes after completion.</p>}
      </section>}
    </main>
    <SiteFooter />
  </>;
}

const detector = window.location.pathname.replace(/\/$/, '') === '/detect';
document.title = 'AutoScan AI | Image & Video Detector';
createRoot(document.getElementById('root')!).render(detector ? <Workspace /> : <Showcase />);
