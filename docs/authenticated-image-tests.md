# Developer-only authenticated image checks

Use the READ token named `autoscan-inference` for manual developer verification.
Keep the WRITE token `autoscan-validation` for deployment. These instructions do
not change the saved Hugging Face login, write a token file, expose a token to
the frontend, or enable paid hardware/credits. Tokens share their account's quota;
creating another token does not create another allowance.

## Local browser testing

Use two local PowerShell terminals. Install the backend/test environment described
in [image-workspace.md](image-workspace.md) first; the adapter uses the existing
FastAPI, HTTPX, AnyIO, and Uvicorn dependencies. It never reads cached HF credentials.

**Terminal 1**, from `E:\autoscan-ai`:

```powershell
python -m scripts.dev_api
```

Enter the dedicated `autoscan-inference` READ token at the hidden prompt, not in
chat or the command itself. Startup verifies the free `MS3B09` personal account
and READ role without running inference. The token stays in process memory;
Ctrl+C stops the adapter. Do not expose or deploy it, tunnel its port, enable
paid GPU usage, or share this local frontend with untrusted code/users.

**Terminal 2**, from `E:\autoscan-ai\web`:

```powershell
$env:VITE_AUTOSCAN_API = 'http://127.0.0.1:7862'
npm run dev -- --port 5173 --strictPort
```

Open **http://127.0.0.1:5173/detect**, not `localhost`. The notice identifies local
developer mode. Selecting media only validates/previews it. Detect submits one
job and can consume your personal free quota; do not repeatedly retry failures.
The adapter checks quota before every submission, requiring the Space's full
60-second reservation and a remaining run. Known exhaustion returns the latest
required platform reset time; missing timing remains explicitly unavailable.
Quota checks are a preflight, not a reservation or a GPU-availability guarantee.

Only new-job submissions receive HF authentication. Preview stays anonymous;
status, media, exports, cancellation, and deletion retain the per-job key. The
adapter accepts only loopback requests with the exact frontend Origin and API
Host, forwards only known routes to the fixed HTTPS Space, and never retries a
submission. These browser protections do not defend against malicious local
processes or code running on the trusted frontend origin.

When done, stop both terminals with Ctrl+C. Before restarting the ordinary public
frontend, replace the URL with
`https://ms3b09-autoscan-ai-images.hf.space` or remove the temporary variable.
Never use the loopback adapter URL in a public build or any token in `VITE_*`.
Public visitors remain anonymous; developer mode adds no public login flow.

## Command-line hosted check

Run these commands in **one local PowerShell terminal** from `E:\autoscan-ai`.
Do not paste the token into chat, a command argument, a repository file, or any
`VITE_` variable. Close the terminal or remove the environment variable afterward.
The hidden prompt keeps the token out of command history; the resulting process
environment is still a secret, not encrypted storage.

### 1. Enter the token and verify identity (no GPU use)

```powershell
$env:AUTOSCAN_TEST_HF_TOKEN = [System.Net.NetworkCredential]::new('', (Read-Host 'Paste autoscan-inference token (hidden)' -AsSecureString)).Password
python -c "import os; from huggingface_hub import HfApi; info=HfApi(token=os.environ['AUTOSCAN_TEST_HF_TOKEN']).whoami(); token=info['auth']['accessToken']; print('Account:', info['name']); print('Token name:', token['displayName']); print('Role:', token['role']); assert info['name']=='MS3B09', 'Unexpected account'; assert token['displayName']=='autoscan-inference', 'Unexpected token'; assert token['role']=='read', 'Use the dedicated READ token'"
```

Continue only if the command exits successfully and identifies account `MS3B09`,
token name `autoscan-inference`, and role `read`. This calls the Hub identity API,
not an inference endpoint; it does not establish remaining GPU quota or verify
that the platform attributes a custom image-job invocation to that account.

### 2. Run one hosted inference/export check

This requests inference using your token and can spend your account's free quota. Do not
run the entire hosted suite or repeatedly retry a quota failure. The command
selects one test, submits one image, checks its result/downloads, and deletes it.

```powershell
$env:AUTOSCAN_IMAGE_URL = 'https://ms3b09-autoscan-ai-images.hf.space'
try {
    python -m unittest discover -s tests -p test_hosted_image_api.py -k test_a_real -v
} finally {
    Remove-Item Env:AUTOSCAN_TEST_HF_TOKEN -ErrorAction SilentlyContinue
}
```

If identity verification fails or you stop before step 2, clear the secret with:

```powershell
Remove-Item Env:AUTOSCAN_TEST_HF_TOKEN -ErrorAction SilentlyContinue
```

## Authentication boundaries

- `AUTOSCAN_TEST_HF_TOKEN` is optional and used only for image-job **submission**.
  Authenticated submissions are restricted to the exact HTTPS AutoScan image
  Space URL above, not arbitrary locally configured hosts.
- The HF gateway supplies the quota-attribution header already forwarded through
  the service's GPU request context. No backend deployment is needed for this
  client change. Actual authenticated quota attribution still needs a hosted run.
- Status, images, exports, cancellation, and deletion continue using only the
  per-job capability, **not** the HF token. Missing/wrong-capability probes stay
  unauthenticated, so owner authentication cannot mask an isolation failure.
- Without this dedicated environment variable, image submissions remain
  anonymous. Tests never automatically borrow `HF_TOKEN` or the cached WRITE
  deployment credential. This preserves explicit anonymous-visitor testing.
- Diagnostic Space tests (`test_hosted_validation.py`) remain anonymous; this
  change is limited to the production image-job checks.

Local `test_hosted_image_client.py` checks outgoing HTTP credential selection
with fake tokens at the external HTTP boundary. Those checks consume no GPU and
are not hosted-authentication evidence. `test_dev_api.py` checks the local adapter
at its HTTP boundary with fake Hub/Space responses. The developer browser replay
checks preview, explicit submission, result, keyboard download, and deletion;
it does **not** prove live HF authentication or quota attribution.
