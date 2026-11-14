import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource/red-hat-display/latin-600.css';
import '@fontsource/red-hat-text/latin-400.css';
import '@fontsource/red-hat-text/latin-500.css';
import { APIError, jobPath, request, type Capability, type Job, type ObjectType } from './api';
import './style.css';

const objectTypes: { value: ObjectType; label: string; note: string }[] = [
  { value: 'vehicle', label: 'Vehicles', note: 'Cars, trucks, buses' },
  { value: 'logo', label: 'Logos', note: '24 vehicle brands' },
  { value: 'plate', label: 'Plates', note: 'Detection, not transcription' },
];
const states = {
  queued: 'Queued. Your image is waiting for the single inference slot.',
  processing: 'Processing. The free GPU may need to start or wait for capacity.',
  cancelling: 'Cancelling. Waiting for the current detector to reach a safe stopping point.',
  success: 'Detection complete.',
  empty: 'Detection complete. No objects matched your selection and confidence.',
  error: 'Detection failed. This is not an empty result.',
  cancelled: 'Cancelled. Server-side source and partial results have been removed.',
};
const activeStates: Job['state'][] = ['queued', 'processing', 'cancelling'];

function Workspace() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState('');
  const [ready, setReady] = useState(false);
  const [types, setTypes] = useState<ObjectType[]>(['vehicle', 'logo', 'plate']);
  const [confidence, setConfidence] = useState(40);
  const [capability, setCapability] = useState<Capability | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [annotated, setAnnotated] = useState('');
  const [error, setError] = useState('');
  const [working, setWorking] = useState(false);
  const [retry, setRetry] = useState(0);
  const [pollFailed, setPollFailed] = useState(false);
  const [notice, setNotice] = useState('Choose an image to begin. Nothing runs until you select Detect image.');
  const input = useRef<HTMLInputElement>(null);
  const focusUpload = useRef(false);
  const locked = !!capability || working;
  const active = capability && (!job || activeStates.includes(job.state));

  useEffect(() => {
    if (!locked && focusUpload.current) {
      input.current?.focus();
      focusUpload.current = false;
    }
  }, [locked]);

  function forgetJob(message: string) {
    setCapability(null); setJob(null); setAnnotated(''); setPollFailed(false); setNotice(message);
  }

  useEffect(() => {
    if (!file) { setPreview(''); setReady(false); return; }
    const controller = new AbortController();
    const urls: string[] = [];
    setPreview('');
    setReady(false);
    setNotice('Validating the image and preparing its orientation. No inference has started.');
    request('/preview?' + new URLSearchParams({ filename: file.name }),
      { method: 'POST', body: file, signal: controller.signal })
      .then(response => response.blob())
      .then(blob => {
        if (controller.signal.aborted) return;
        const url = URL.createObjectURL(blob);
        urls.push(url);
        setPreview(url);
        setReady(true);
        setNotice('Image ready. Choose object types and confidence, then Detect image.');
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
        setNotice(states[next.state]);
        if (activeStates.includes(next.state)) {
          timer = setTimeout(poll, 1200);
        } else if (next.state === 'success' || next.state === 'empty') {
          timer = setTimeout(() => {
            forgetJob('Results expired and are no longer available. You can run a new detection.');
          }, Math.max(0, (next.expires_at! * 1000) - Date.now()));
          const image = await request(jobPath(capability!) + '/image', { signal: controller.signal }, capability!);
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
    } catch (reason) { setError((reason as Error).message); }
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

  async function remove(keepSource = false) {
    if (!capability || !window.confirm('Delete this job and its remaining server-side results? This cannot be undone.')) return;
    setWorking(true); setError('');
    try {
      try { await request(jobPath(capability), { method: 'DELETE' }, capability); }
      catch (reason) { if (!(reason instanceof APIError && reason.status === 404)) throw reason; }
      forgetJob(keepSource ? 'Server results cleared. Change your image or settings, then select Detect image.' :
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
    <header className="shell topbar">
      <a className="wordmark" href="/detect">AutoScan AI</a>
      <nav aria-label="Main navigation">
        <a href="/detect" aria-current="page">Detector</a>
        <a href="https://github.com/MS3B09/autoscan-ai">GitHub</a>
      </nav>
    </header>
    <main id="workspace" className="shell">
      <div className="intro"><h1>See what your image holds.</h1>
        <p>Detect vehicles, brand logos, and plates. Inspect the real model results.</p></div>
      <section className="controls" aria-label="Image and detection settings">
        <div className="upload">
          <label htmlFor="image">Source image</label>
          <input ref={input} id="image" type="file" accept=".png,.jpg,.jpeg,.bmp,.webp" disabled={locked}
            aria-describedby="image-help" onChange={event => {
              const next = event.target.files?.[0];
              setError('');
              if (!next) return;
              if (next.size > 10_000_000 || !/\.(png|jpe?g|bmp|webp)$/i.test(next.name)) {
                setFile(null); setError('Choose a PNG, JPG, BMP, or WebP image up to 10 MB.'); return;
              }
              setFile(next);
            }} />
          <p id="image-help">PNG, JPG, BMP, WebP. Up to 10 MB and 12 megapixels.</p>
        </div>
        <fieldset disabled={locked}>
          <legend>Object types</legend>
          <div className="types">{objectTypes.map(type => <label key={type.value}>
            <input type="checkbox" checked={types.includes(type.value)} onChange={event => {
              setTypes(event.target.checked ? [...types, type.value] : types.filter(value => value !== type.value));
            }} /><span>{type.label}<small>{type.note}</small></span>
          </label>)}</div>
        </fieldset>
        <div className="confidence">
          <label htmlFor="confidence">Confidence <output htmlFor="confidence">{confidence}%</output></label>
          <input id="confidence" type="range" min="25" max="100" step="1" value={confidence} disabled={locked}
            onChange={event => setConfidence(Number(event.target.value))} />
          <p>25% to 100%</p>
        </div>
        <div className="actions">
          <button className="primary" onClick={() => void detect()} disabled={!ready || !types.length || locked}>
            {working && !capability ? 'Uploading…' : 'Detect image'}</button>
          {active && <button onClick={() => void cancel()} disabled={working || job?.state === 'cancelling'}>Cancel</button>}
          {capability && <button onClick={() => void remove()} disabled={working}>Delete now</button>}
        </div>
      </section>
      <div className="feedback">
        <p role="status" aria-live="polite">{!types.length ? 'Select at least one object type.' : notice}</p>
        {error && <p role="alert" className="error">{error}</p>}
        {pollFailed && <button onClick={() => { setError(''); setRetry(value => value + 1); }}>Retry job status</button>}
        {file && !ready && error && <button onClick={() => { setError(''); setFile(new File([file], file.name)); }}>Retry image validation</button>}
      </div>
      <section className="comparison" aria-label="Source and detection comparison" aria-busy={!!active}>
        <figure><figcaption><h2>Original</h2><span>{file?.name || 'Your selected image'}</span></figcaption>
          <div className="image-stage">{preview ? <img src={preview} alt="Selected source, normalized for detection" /> :
            <p>Choose your image above.<br />Its preview will appear here.</p>}</div></figure>
        <figure><figcaption><h2>Detections</h2><span>{job ? `${job.width} × ${job.height} pixels` : 'Actual inference, no example boxes'}</span></figcaption>
          <div className="image-stage">{annotated ? <img src={annotated} alt={`Annotated result with ${job?.detections.length ?? 0} detections`} /> :
            <p>{job ? states[job.state] : 'Your annotated image will appear here after detection.'}</p>}</div></figure>
      </section>
      {job && <section className="results" aria-labelledby="result-heading">
        <div className="result-heading"><h2 id="result-heading">Detection details</h2>
          <p>{job.detections.length} detections at {job.settings.confidence}% minimum confidence</p></div>
        {job.error && <p className="error">{job.error}</p>}
        {job.state === 'empty' && <p>No matching objects found. Use Change image or settings to try another image or lower confidence.</p>}
        {!activeStates.includes(job.state) &&
          <button onClick={() => void remove(true)} disabled={working}>Change image or settings</button>}
        {job.detections.length > 0 && <table>
          <caption>Pixel coordinates refer to the {job.width} × {job.height} oriented input, measured from its top-left corner.</caption>
          <thead><tr><th>Object</th><th>Model class</th><th>Confidence</th><th>Box (x1, y1, x2, y2)</th></tr></thead>
          <tbody>{job.detections.map((detection, index) => <tr key={index}>
            <td data-label="Object"><span className={'type-label ' + detection.object_type}>{detection.label}</span></td>
            <td data-label="Model class">{detection.class_name} (ID {detection.class_id})</td>
            <td data-label="Confidence">{(detection.confidence * 100).toFixed(1)}%</td>
            <td data-label="Box" className="coordinates">{detection.bbox.map(value => value.toFixed(1)).join(', ')}</td>
          </tr>)}</tbody>
        </table>}
        {job.expires_at && <p>Server results expire at <time dateTime={new Date(job.expires_at * 1000).toISOString()}>
          {new Date(job.expires_at * 1000).toLocaleTimeString()}</time>, 30 minutes after completion.</p>}
      </section>}
      <section className="privacy" aria-labelledby="privacy-heading"><h2 id="privacy-heading">Temporary by design.</h2>
        <p>Your image is sent to the Python service for validation; inference starts only on your command.
          Sources are removed when no longer needed. Results expire automatically after 30 minutes.
          Delete now revokes access immediately and removes remaining files at a safe boundary.
          Refreshing this page loses your job key; a server restart also loses jobs.</p>
        <p>Shared free GPU capacity can mean queues, cold starts, or quota errors. Plate detection does not read plate text.</p>
      </section>
    </main>
    <footer className="shell"><span>AutoScan AI</span><a href="https://github.com/MS3B09/autoscan-ai#about-the-project-and-authors">Original contributors and datasets</a></footer>
  </>;
}

createRoot(document.getElementById('root')!).render(<Workspace />);
