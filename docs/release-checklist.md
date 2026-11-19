# Release checks

- Use the [deployment runbook](release-runbook.md). Keep deployments on the existing free services. Do not enable paid resources or run hosted inference tests without the owner's approval; the owner reserves the final hosted video test.
- Before publishing frontend changes, check TypeScript, the production build, and the affected browser workflow. Local API tests with fake compute do not verify hosted inference, quota, or retention.
- Keep the repository license and original credits, dataset notices, and checkpoint digests. Third-party licensing compliance remains [unverified under the recorded owner decision](evidence/release-licensing.md#owner-directed-workflow-decision--2026-11-16).
- Previous release decisions and verification records are available in the [archived evidence](https://github.com/MS3B09/autoscan-ai/tree/ebad2718a90baddfddb1edc9205b8fdf1dc7f057/docs/evidence).
