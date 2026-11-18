import { useEffect, useRef, useState } from 'react';
import original from '../../imgs/home-image.png';
import detected from '../../imgs/home-image-detected.png';
import logos from '../../imgs/logos.jpg';
import { Icon } from './icon';
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
const workflow = [
  { icon: 'upload', title: 'Choose your media', text: 'Add an image or short video.' },
  { icon: 'tune', title: 'Set what to find', text: 'Pick object types and a confidence threshold.' },
  { icon: 'scan', title: 'Review detections', text: 'See what was found and save the results (Annotated Image, CSV & JSON Data)' },
] as const;
const classes = [
  { icon: 'vehicle', title: 'Vehicles', text: 'Cars, trucks and buses' },
  { icon: 'logo', title: 'Brand logos', text: '24 vehicle brands' },
  { icon: 'plate', title: 'Moroccan plates', text: 'Plate location, not transcription' },
] as const;

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
          <a className="button primary" href="/detect#image"><Icon name="image" />Open image detector</a>
          <a className="button" href="/detect#video"><Icon name="video" />Try a video</a>
        </div>
      </section>
      <section className="showcase-comparison" aria-label="Detection example">
        {images.map(image => <figure key={image.title}>
          <figcaption><Icon name={image.title === 'Original' ? 'image' : 'scan'} /><h2>{image.title}</h2></figcaption>
          <div className="sample-image">
            <img src={image.src} width="648" height="432" fetchPriority="high" alt={image.alt} />
            <button className="expand-image" aria-label={`View ${image.title.toLowerCase()} full size`}
              aria-haspopup="dialog" onClick={() => setExpanded(image)}>
              <Icon name="expand" />
            </button>
          </div>
        </figure>)}
        <aside className="example-legend" aria-labelledby="legend-heading">
          <h2 id="legend-heading">Legend</h2>
          <ul>{detections.map(detection => <li key={detection.type}>
            <span className={'legend-label ' + detection.type}>{detection.label}</span>
            <strong>{detection.confidence}</strong>
          </li>)}</ul>
          <p>Scores show model confidence, not measured accuracy.</p>
        </aside>
      </section>
      <section className="workflow-section" aria-labelledby="workflow-heading">
        <h2 id="workflow-heading">From detections to data</h2>
        <ol className="workflow" role="list">{workflow.map((step, index) => <li key={step.icon}>
          <span className="workflow-icon"><Icon name={step.icon} /></span>
          <div><h3>{step.title}</h3><p>{step.text}</p></div>
          {index < workflow.length - 1 && <Icon name="arrow" className="workflow-arrow" />}
        </li>)}</ol>
      </section>
      <section className="project-facts" aria-labelledby="capabilities-heading">
        <div><h2 id="capabilities-heading">Three detectors. Your selection.</h2>
          <p>Run one detector, or combine all three.</p>
          <dl>{classes.map(item => <div className={`class-row ${item.icon}`} key={item.icon}>
            <dt><Icon name={item.icon} />{item.title}</dt><dd>{item.text}</dd>
          </div>)}</dl>
        </div>
        <img className="brand-image" src={logos} width="1920" height="1080" loading="lazy"
          alt="24 supported vehicle brands: Audi, BMW, Chevrolet, Citroën, Dacia, Fiat, Ford, Honda, Hyundai, Kia, Lexus, Mazda, Mercedes-Benz, Mitsubishi, Nissan, Opel, Peugeot, Renault, Seat, Škoda, Suzuki, Toyota, Volkswagen and Volvo" />
      </section>
      <section className="project-invite" aria-labelledby="try-heading">
        <div><h2 id="try-heading">See it on your own media.</h2>
          <p>Try the detector, or explore how it works on GitHub.</p></div>
        <div className="invite-actions">
          <a className="button primary" href="/detect#image">Open the detector <Icon name="arrow" /></a>
          <a className="button" href="https://github.com/MS3B09/autoscan-ai"><Icon name="code" />Explore the source code</a>
        </div>
      </section>
    </main>
    <SiteFooter />
    <dialog ref={dialog} className="image-dialog" aria-labelledby="expanded-title"
      onClose={() => setExpanded(null)} onClick={event => { if (event.target === event.currentTarget) dialog.current?.close(); }}>
      <div className="image-dialog-heading"><h2 id="expanded-title">{expanded?.title}</h2>
        <button aria-label="Close full-size image" onClick={() => dialog.current?.close()} autoFocus>
          <Icon name="close" />
        </button>
      </div>
      {expanded && <img src={expanded.src} alt={expanded.alt} width="648" height="432" />}
    </dialog>
  </>;
}
