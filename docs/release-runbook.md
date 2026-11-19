# Run and deploy AutoScan

For the local web interface, follow the [README](../README.md#run-locally). Clicking **Detect** submits media to the configured API and uses shared quota if you use the hosted service.

## Runtime and dependencies

- **Web:** Node.js 24 and npm. In `web/`, run `npm ci` and `npm run build`. Set `VITE_AUTOSCAN_API` to the public backend origin before building. Never put credentials in `VITE_*` variables.
- **Detection service:** Python 3.10.13 and a compatible CUDA/ZeroGPU environment. Install `image_service/requirements.txt` and the system libraries in `image_service/packages.txt`. From the repo root, run `python -m image_service.app`. This loads models onto CUDA at startup and is not a CPU development server.
- **Model files:** `models/logo.pt` and `models/plate.pt` use Git LFS. If your checkout contains LFS pointers, hydrate them with `git lfs pull` before running the service. The service provisions absent checkpoints from a pinned source and verifies all three SHA-256 digests before loading.

## Deploy

- **Netlify:** build and publish `web/dist` with the rewrites and headers in [`netlify.toml`](../netlify.toml). The current site is not Git-linked; pushing to GitHub does not publish the frontend.
- **Hugging Face Spaces:** use the [backend file mapping](image-workspace.md#space-packaging). Configure `AUTOSCAN_ORIGINS` with exact frontend origins, including the scheme and port where applicable. Use free ZeroGPU only; do not enable a paid fallback.

Check `/`, `/detect`, and the service’s `/api/health` after deployment. A health response does not verify inference or GPU availability. Follow the [release constraints](release-checklist.md) before running hosted checks or changing a deployment.
