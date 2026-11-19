# Run and deploy AutoScan

For the local web interface, follow the [README](../README.md#run-locally). Clicking **Detect** submits media to the configured API.

## Runtime and dependencies

- **Web:** Node.js 24 and npm. In `web/`, run `npm ci` and `npm run build`. Set `VITE_AUTOSCAN_API` to the public backend origin before building. Never put credentials in `VITE_*` variables.
- **Detection service:** Python 3.10.13 and a compatible CUDA/ZeroGPU environment. Install `image_service/requirements.txt` and the system libraries in `image_service/packages.txt`. From the repo root, run `python -m image_service.app`. This loads models onto CUDA at startup and is not a CPU development server.
- **Model files:** `models/logo.pt` and `models/plate.pt` use Git LFS. If your checkout contains LFS pointers, hydrate them with `git lfs pull` before running the service. The service provisions absent checkpoints from a pinned source and verifies all three SHA-256 digests before loading.

## Deploy your own detection backend

1. [Create a Hugging Face Space](https://huggingface.co/new-space) with the Gradio SDK and [ZeroGPU hardware](https://huggingface.co/docs/hub/spaces-zerogpu), if eligible. The backend requires CUDA; it does not run on the default CPU hardware.
2. Commit the files in the [backend file mapping](image-workspace.md#space-packaging) to your Space repository.
3. In your Space settings, add the `AUTOSCAN_ORIGINS` variable. Set it to `http://127.0.0.1:5173` for local development. For a published frontend, add its exact origin to the comma-separated list.
4. When your Space is running, check `/api/health` on its `*.hf.space` URL. Set `VITE_AUTOSCAN_API` to that base URL, without `/api` or any credentials.

## Deploy the frontend

On Netlify, build and publish `web/dist` with the rewrites and headers in [`netlify.toml`](../netlify.toml). The current demo site is not Git-linked; pushing to GitHub does not publish it.

Check `/`, `/detect`, and the service’s `/api/health` after deployment. A health response does not verify inference or GPU availability. Follow the [release constraints](release-checklist.md) before running hosted checks or changing a deployment.
