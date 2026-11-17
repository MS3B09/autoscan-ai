import { Icon } from './icon';

export function SiteHeader({ detector = false }: { detector?: boolean }) {
  return <header className="shell topbar">
    <a className="wordmark" href="/">
      <svg viewBox="0 0 32 24" aria-hidden="true"><path fill="currentColor" d="m7 3-3 7-2 2v8h3v2h4v-2h14v2h4v-2h3v-8l-2-2-3-7a4 4 0 0 0-4-3H11a4 4 0 0 0-4 3Zm4 0h10l3 7H8Zm-4 10a2 2 0 1 1 0 4 2 2 0 0 1 0-4Zm18 0a2 2 0 1 1 0 4 2 2 0 0 1 0-4Z" /></svg>
      AutoScan AI
    </a>
    <nav aria-label="Main navigation">
      <a href="/" aria-current={!detector ? 'page' : undefined}>Project</a>
      <a href="/detect" aria-current={detector ? 'page' : undefined}>Detector</a>
      <a href="https://github.com/MS3B09/autoscan-ai">GitHub <Icon name="external" /></a>
    </nav>
  </header>;
}

export function SiteFooter() {
  return <footer className="shell">
    <span>AutoScan AI <small>Model and dataset licensing remains unverified.</small></span>
    <a href="https://github.com/MS3B09/autoscan-ai#about-the-project-and-authors">Original contributors and datasets <Icon name="external" /></a>
  </footer>;
}
