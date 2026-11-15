import example from '../public/examples/lexus.json';
import csv from '../public/examples/lexus.csv?raw';
import { SiteFooter, SiteHeader } from './site';
import './showcase.css';

const jsonPreview = JSON.stringify({ filename: example.filename, width: example.width, height: example.height,
  settings: example.settings, detections: example.detections }, null, 2);

export function Showcase() {
  return <>
    <a className="skip" href="#project">Skip to project</a>
    <SiteHeader />
    <main id="project" className="shell showcase" tabIndex={-1}>
      <section className="showcase-intro" aria-labelledby="showcase-heading">
        <h1 id="showcase-heading">See what the models detect.</h1>
        <p>Detect vehicles, logos and Moroccan plates in images and short videos.</p>
        <div className="showcase-actions">
          <a className="entry" href="/detect#image">Open image detector</a>
          <a className="video-entry" href="/detect#image">Try a video</a>
        </div>
      </section>
      <section className="showcase-comparison" aria-label="Real inference example">
        <figure>
          <figcaption><h2>Original</h2><a href="/examples/lexus-lx570.jpg" aria-label="View original full size">Full size</a></figcaption>
          <img src="/examples/lexus-lx570.jpg" width="1280" height="915" fetchPriority="high"
            alt="Black Lexus LX 570 photographed from the rear, with no license plate fitted" />
        </figure>
        <figure>
          <figcaption><h2>Detections</h2><a href="/examples/lexus-detections.png" aria-label="View detections full size">Full size</a></figcaption>
          <img src="/examples/lexus-detections.png" width="1280" height="915"
            alt="Actual output: the Lexus is classified as truck, a background car and Lexus logo are detected, and a side step is incorrectly marked Plate" />
        </figure>
        <aside className="example-legend" aria-labelledby="legend-heading">
          <h2 id="legend-heading">Legend</h2>
          <ul>{example.detections.map((detection, index) => <li key={index}>
            <span className={'legend-label ' + detection.object_type}>{detection.label}</span>
            <span>{(detection.confidence * 100).toFixed(1)}%</span>
          </li>)}</ul>
          <p>Real model output at 40% minimum confidence. Not an accuracy benchmark.</p>
        </aside>
      </section>
      <section className="data-section" aria-labelledby="data-heading">
        <div><h2 id="data-heading">From detections to data</h2>
          <p>Inspect this image’s real JSON and CSV. A published sample, not a live job.</p></div>
        <div className="data-preview"><h3>JSON (detection excerpt)</h3>
          <pre role="region" aria-label="JSON sample preview" tabIndex={0}><code>{jsonPreview}</code></pre></div>
        <div className="data-preview"><h3>CSV (complete sample)</h3>
          <pre role="region" aria-label="CSV sample preview" tabIndex={0}><code>{csv.trimStart()}</code></pre></div>
        <div className="data-downloads">
          <a className="entry" href="/examples/lexus.json" download="autoscan-example.json">Download sample JSON</a>
          <a className="entry" href="/examples/lexus.csv" download="autoscan-example.csv">Download sample CSV</a>
        </div>
      </section>
      <section className="example-context" aria-labelledby="example-heading">
        <h2 id="example-heading">Predictions, imperfections included.</h2>
        <div><p>The model labels this Lexus SUV as “truck” and mistakes a side step for a plate.
          This German photograph contains no Moroccan plate. Confidence is not a measure of accuracy.</p>
          <p className="photo-credit" data-credits="photography">Photograph: <a href="https://commons.wikimedia.org/wiki/File:Lexus_LX_570_20090620_rear.JPG">Lexus LX 570</a> by <a href="https://commons.wikimedia.org/wiki/User:M_93">M 93</a>.
            {' '}<a href="https://commons.wikimedia.org/wiki/Template:Attribution">Attribution-only permission</a> via Wikimedia Commons.
            Resized; detector annotations added. <a href="/examples/attribution.txt">Provenance and usage notes</a>.</p></div>
      </section>
      <section className="project-facts" aria-labelledby="capabilities-heading">
        <h2 id="capabilities-heading">Three detectors. Your selection.</h2>
        <div><dl>
          <div><dt>Vehicles</dt><dd>Bounding boxes for cars, trucks and buses.</dd></div>
          <div><dt>Brand logos</dt><dd>24 logo classes from the original checkpoint.</dd></div>
          <div><dt>Moroccan plates</dt><dd>Locates plates, without reading their text. No OCR.</dd></div>
        </dl>
          <details><summary>View all 24 supported logo brands</summary>
            <ul className="brand-list">{Object.values(example.models.logo.classes).map(brand => <li key={brand}>{brand}</li>)}</ul>
          </details>
        </div>
      </section>
      <section className="project-facts" aria-labelledby="try-heading">
        <h2 id="try-heading">Try your own media.</h2>
        <div><p>Choose your file inside the detector. Nothing runs until you select Detect.
          Adjust confidence from 25% to 100%, then download annotated media, JSON or CSV.</p>
          <p>Live results expire after 30 minutes; Delete now removes them earlier.
            Refresh or restart can lose a job. Free GPU quotas, queues and cold starts can interrupt processing.</p>
          <a className="text-action" href="/detect">Open the detector</a></div>
      </section>
      <section className="project-facts contributors" aria-labelledby="credits-heading">
        <h2 id="credits-heading">The original project team.</h2>
        <div><ul className="contributor-list">
          <li><a href="https://github.com/zayd8890">El-Ouaragli Zayd</a></li>
          <li><a href="https://github.com/ou4abs">El-Abbass Ossama</a></li>
          <li><a href="https://github.com/MS3B09">Nassiri Mosab</a></li>
          <li><a href="https://github.com/HaFares">Hassan Fares</a></li>
          <li><a href="https://github.com/Guinga6">Aly Guinga</a></li>
        </ul>
          <p>Datasets: <a href="https://universe.roboflow.com/ms3b/logos-teamx/dataset/1">Logos</a>,
            {' '}<a href="https://universe.roboflow.com/plate-detection/plate_detection-tp5h9">Moroccan plates</a>.
            {' '}Detection uses <a href="https://github.com/ultralytics/ultralytics">Ultralytics YOLO</a>.</p>
          <p>Model and dataset licensing is not yet cleared for public release.
            {' '}<a href="https://github.com/MS3B09/autoscan-ai">Inspect the project source</a>.</p></div>
      </section>
    </main>
    <SiteFooter />
  </>;
}
