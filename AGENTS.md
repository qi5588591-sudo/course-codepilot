# CodePilot AI continuation instructions

## Start here

Read `docs/HANDOFF.md`, `docs/ROADMAP.md`, then `README.md` before changing code.
This is a personal intelligent applications coursework project, topic 32. Keep the VS Code
extension + Python backend design and the four-language assistance / Python-only execution boundary.
The user has deliberately stopped feature work for now. Do not start roadmap tasks merely on opening this repository.

## Working agreements

- Prefer a small reviewable change addressing the user's current request.
- Python business logic belongs in `backend/`; VS Code interaction belongs in `extension/src/`.
- Do not introduce model training, a separate website, IntelliJ support, vector databases or autonomous workspace scanning without a new request.
- Never read or print `.env` secrets. Configuration names and `.env.example` are enough for inspection.
- Cloud calls can cost money. Use fixtures for tests, and follow the user's explicit evaluation scope before running live experiments.
- Execute model-produced Python only through Docker. Never add a host execution fallback.
- Keep test assertions fixed during repair, with at most two repair rounds and the test SHA256 recorded.
- Preserve the URI/version/content check before applying an editor modification.
- Render model and history output as text, never raw HTML in the Webview.
- Distinguish mock engineering tests, trusted reference examples and real model results in every report.
- Leave personal identity fields and personal reflections to the student; do not invent them.

## Checks

From repository root after setting up Python dependencies:

```powershell
.venv\Scripts\python.exe -m pytest -q
cd extension
pnpm install --frozen-lockfile
pnpm run compile
pnpm test
cd ..
node scripts/package-extension.cjs
```

Python 3.12 and Node 22+ are supported. pnpm 11.25.0 matches the existing lockfile/tooling.
Create `artifacts/` if absent before writing test reports. Real Docker tests require an explicitly
built sandbox image and `CODEPILOT_DOCKER_TESTS=1`; without that flag they are intentionally skipped.
Native VS Code tests use `extension/test/run-host.cjs` and a disposable user profile.
Browser/material authoring scripts require optional tools documented in the handoff and are not runtime dependencies.

## Before handing back

Update the relevant behavior docs, record commands and limits accurately, and update `docs/HANDOFF.md`
when the project status materially changes. Do not overwrite historical evidence with invented or simulated model metrics.
Do not include local credentials, databases, environments, caches or raw course documents in commits.
