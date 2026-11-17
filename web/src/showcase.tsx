import { useEffect, useRef, useState } from 'react';
import original from '../../imgs/home-image.png';
import detected from '../../imgs/home-image-detected.png';
import logos from '../../imgs/logos.jpg';
import { SiteFooter, SiteHeader } from './site';
import './showcase.css';

const images = [
  { title: 'Original', src: original, alt: 'White Nissan SUV on a rocky desert road' },
  { title: 'Detections', src: detected, alt: 'Nissan SUV with bounding boxes for car at 87%, Nissan logo at 91%, and plate at 63%' },
];
const detections = [
  { type: 'vehicle', label: 'car', confidence: '87%' },
  { type: 'logo', label: 'nissan', confidence: '91%' },
  { type: 'plate', label: 'Plate', confidence: '63%' },
];

export function Showcase() {
  const [expanded, setExpanded] = useState<typeof images[number] | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    if (expanded) dialog.current?.showModal();
  }, [expanded]);

  return <>
    <a className="skip" href="#project">Skip to project</a>
    <SiteHeader />
    <main id="project" className="shell showcase" tabIndex={-1}>
      <section className="showcase-intro" aria-labelledby="showcase-heading">
        <h1 id="showcase-heading">See what the models detect.</h1>
        <p>Detect vehicles, logos and Moroccan plates in images and short videos.</p>
        <div className="showcase-actions">
          <a className="entry" href="/detect#image">Open image detector</a>
          <a className="video-entry" href="/detect#video">Try a video</a>
        </div>
      </section>
      <section className="showcase-comparison" aria-label="Detection example">
        {images.map(image => <figure key={image.title}>
          <figcaption><h2>{image.title}</h2></figcaption>
          <div className="sample-image">
            <img src={image.src} width="648" height="432" fetchPriority="high" alt={image.alt} />
            <button className="expand-image" aria-label={`View ${image.title.toLowerCase()} full size`}
              aria-haspopup="dialog" onClick={() => setExpanded(image)}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <path d="M9 3H3v6m12-6h6v6M3 15v6h6m12-6v6h-6M3 3l6 6m12-6-6 6M3 21l6-6m12 6-6-6" />
              </svg>
            </button>
          </div>
        </figure>)}
        <aside className="example-legend" aria-labelledby="legend-heading">
          <h2 id="legend-heading">Legend</h2>
          <ul>{detections.map(detection => <li key={detection.type}>
            <span className={'legend-label ' + detection.type}>{detection.label}</span>
            <span>{detection.confidence}</span>
          </li>)}</ul>
          <p>Example detections. Confidence is not a measure of accuracy.</p>
        </aside>
      </section>
      <section className="workflow-section" aria-labelledby="workflow-heading">
        <h2 id="workflow-heading">From detections to data</h2>
        <ol className="workflow">
          <li><h3>Choose your media</h3><p>Upload an image or a short video.</p></li>
          <li><h3>Make your selection</h3><p>Pick object types and set your confidence.</p></li>
          <li><h3>Detect and explore</h3><p>Review the results and download what you need.</p></li>
        </ol>
      </section>
      <section className="project-facts" aria-labelledby="capabilities-heading">
        <div><h2 id="capabilities-heading">Three detectors. Your selection.</h2>
          <p>Run one detector, or combine all three.</p>
          <dl>
            <div><dt>Vehicles</dt><dd>Cars, trucks and buses.</dd></div>
            <div><dt>Brand logos</dt><dd>24 vehicle brands.</dd></div>
            <div><dt>Moroccan plates</dt><dd>Locate plates, without reading the text.</dd></div>
          </dl>
        </div>
        <img className="brand-image" src={logos} width="1920" height="1080" loading="lazy"
          alt="24 supported vehicle brands: Audi, BMW, Chevrolet, Citroën, Dacia, Fiat, Ford, Honda, Hyundai, Kia, Lexus, Mazda, Mercedes-Benz, Mitsubishi, Nissan, Opel, Peugeot, Renault, Seat, Škoda, Suzuki, Toyota, Volkswagen and Volvo" />
      </section>
      <section className="project-invite" aria-labelledby="try-heading">
        <div><h2 id="try-heading">See it on your own media.</h2>
          <p>Try the detector, or explore how it works on GitHub.</p></div>
        <div className="invite-actions">
          <a className="entry" href="/detect#image">Open the detector</a>
          <a className="text-action" href="https://github.com/MS3B09/autoscan-ai">Explore the source code</a>
        </div>
      </section>
    </main>
    <SiteFooter />
    <dialog ref={dialog} className="image-dialog" aria-labelledby="expanded-title"
      onClose={() => setExpanded(null)} onClick={event => { if (event.target === event.currentTarget) dialog.current?.close(); }}>
      <div className="image-dialog-heading"><h2 id="expanded-title">{expanded?.title}</h2>
        <button aria-label="Close full-size image" onClick={() => dialog.current?.close()} autoFocus>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6" /></svg>
        </button>
      </div>
      {expanded && <img src={expanded.src} alt={expanded.alt} width="648" height="432" />}
    </dialog>
  </>;
}
