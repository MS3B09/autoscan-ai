const paths = {
  image: 'M4 4h16v16H4z M4 16l5-5 4 4 3-3 4 4 M15 8h.01',
  video: 'M4 5h16v14H4z M10 9l5 3-5 3z',
  upload: 'M12 16V4m-4 4 4-4 4 4 M4 16v4h16v-4',
  tune: 'M4 6h6m4 0h6 M4 12h10m4 0h2 M4 18h2m4 0h10 M10 4v4m4 2v4M6 16v4',
  scan: 'M4 9V4h5m6 0h5v5M4 15v5h5m6 0h5v-5 M8 8h8v8H8z',
  vehicle: 'm5 11 2-5h10l2 5m-1 7v2M6 18v2 M4 11h16v7H4z M7 14h1m8 0h1',
  logo: 'm12 3 8 4v10l-8 4-8-4V7z M9 12l2 2 4-4',
  plate: 'M3 6h18v12H3z M6 12h2m3 0h2m3 0h2',
  arrow: 'M4 12h15m-6-6 6 6-6 6',
  external: 'M14 4h6v6m0-6-9 9m-1-8H5v14h14v-5',
  code: 'm8 7-5 5 5 5m8-10 5 5-5 5m-3-13-2 16',
  check: 'm5 12 4 4L19 6',
  info: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z M12 11v5m0-8h.01',
  alert: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z M12 7v6m0 4h.01',
  download: 'M12 4v12m-4-4 4 4 4-4 M4 16v4h16v-4',
  expand: 'M9 4H4v5m11-5h5v5M4 15v5h5m11-5v5h-5',
  close: 'm6 6 12 12M6 18 18 6',
};

export function Icon({ name, className = '' }: { name: keyof typeof paths; className?: string }) {
  return <svg className={`icon ${className}`} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d={paths[name]} />
  </svg>;
}
