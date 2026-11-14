# Developer-only authenticated image checks

Use the READ token named `autoscan-inference` for manual developer verification.
Keep the WRITE token `autoscan-validation` for deployment. These instructions do
not change the saved Hugging Face login, write a token file, expose a token to
the frontend, or enable paid hardware/credits. Tokens share their account's quota;
creating another token does not create another allowance.

Run these commands in **one local PowerShell terminal** from `E:\autoscan-ai`.
Do not paste the token into chat, a command argument, a repository file, or any
`VITE_` variable. Close the terminal or remove the environment variable afterward.
The hidden prompt keeps the token out of command history; the resulting process
environment is still a secret, not encrypted storage.

## 1. Enter the token and verify identity (no GPU use)

```powershell
$env:AUTOSCAN_TEST_HF_TOKEN = [System.Net.NetworkCredential]::new('', (Read-Host 'Paste autoscan-inference token (hidden)' -AsSecureString)).Password
python -c "import os; from huggingface_hub import HfApi; info=HfApi(token=os.environ['AUTOSCAN_TEST_HF_TOKEN']).whoami(); token=info['auth']['accessToken']; print('Account:', info['name']); print('Token name:', token['displayName']); print('Role:', token['role']); assert info['name']=='MS3B09', 'Unexpected account'; assert token['displayName']=='autoscan-inference', 'Unexpected token'; assert token['role']=='read', 'Use the dedicated READ token'"
```

Continue only if the command exits successfully and identifies account `MS3B09`,
token name `autoscan-inference`, and role `read`. This calls the Hub identity API,
not an inference endpoint; it does not establish remaining GPU quota or verify
that the platform attributes a custom image-job invocation to that account.

## 2. Run one hosted inference/export check

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
are not hosted-authentication evidence. The public frontend remains unchanged.
