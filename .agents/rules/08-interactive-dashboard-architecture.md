# Interactive Operator Dashboard & Control Plane Architecture

Whenever building, modifying, or reviewing a web dashboard, operator panel, recording studio, or local cockpit surface (`tools/<tool>/static/<tool>_dashboard.html` and `tools/<tool>/server.py`), agents must enforce this interactive control-plane contract.

---

## 1. Zero "Decorative Tech-Debt" Dashboards

A dashboard must **never** be a passive, read-only status viewer that forces the operator back to the terminal to configure or run tasks.
- **Anti-Seam-Rot Mandate**: The CLI runner (`tools/<tool>.py` or `tools/orchestrator.py`) is the first consumer of every manifest, contract, event stream (`events.jsonl`), and control file (`control.json`). The web dashboard is a second consumer of those exact same artifacts and adds zero separate state store of its own.
- **Canonical Filename & Aliasing**: The HTML file must be named `tools/<tool>/static/<tool>_dashboard.html` (never naked `index.html`). The HTTP handler (`do_GET`) must serve `<tool>_dashboard.html` as canonical while aliasing `/` and `/index.html` to it.

---

## 2. The 7 Mandatory Interactive Capabilities

Every dashboard must ship with all seven interactive capabilities out of the box:

### A. Run Creation & Target Configuration Deck
1. **Dynamic Deployment / Target Selector**:
   - Populated dynamically from `GET /api/config` or `GET /api/deployments` (never hardcoded to a static list of 1–2 items).
   - Supports inline onboarding of new deployments/targets via `POST /api/deployments/onboard` (persisting base URL, custom slug, mutation policy, and persona credentials).
2. **Suite / Task Selection & Filtering**:
   - Categorized navigation tabs (e.g., by portal or architectural domain) with live count badges.
   - Real-time search input (by suite code, title, or domain keyword) and filter pills (`All`, `Failed Only`, `Passed`, `Mutating`, `Destructive`).
   - Batch selection actions: `Select Filtered`, `Clear Selection`, domain-level batch checkboxes, and a live selection counter.
   - **Live Plan & Dependency Preview (`GET /api/plan`)**: Shows topological DAG execution order, auto-included prerequisite suites, and deferred operator-assisted tasks before launch.
3. **Operator Identity & Traceability**:
   - Dedicated `Operator` input field defaulting to the project lead (e.g., `"{{PROJECT_OWNER}}, QA Lead"` or `"Ted Mwai, QA Lead"`), persisted into `verdict.json`, `run-report.md`, `mainReport.md`, and `operator_feedback.jsonl`.
4. **Safety & Production Mutation Interlock UI**:
   - Explicit toggles for `Allow Mutation` and `Confirm Destructive`.
   - When a production target (`production`, `prod`, `cyberranges.com`) is selected and mutation is toggled on, reveal a required confirmation input demanding the exact token `PROD-MUTATE` (enforced client-side and verified server-side with `403 Forbidden` on mismatch).

### B. Active Lifecycle Management & Multi-Session Error Recovery (`409 Conflict`)
1. **Apple HIG 44x44px Capsule Action Bar**:
   - `Run Selected` (`POST /api/session/start` or `POST /api/runs`)
   - `Pause at Next Barrier` (`POST /api/runs/<id>/control` with `{"action": "pause"}`)
   - `Abort / Stop` (`POST /api/session/stop` or `POST /api/stop`)
   - `Cancel / Reset Session` (`POST /api/session/abort` or `POST /api/session/reset`)
   - `Resume Latest` (`POST /api/runs` with `{"resume_latest": true}`)
2. **Dead-Worker Auto-Healing**:
   - Before processing `/start` or `/status`, the server must inspect `worker_thread.is_alive()` (or subprocess `.poll()`). If a previous worker died or exited while the status remained `STARTING`, `WORKING`, `RECORDING`, or `INGESTING`, automatically heal the state back to `IDLE` so the operator is never locked out after an interrupted launch.
3. **Actionable `409 Conflict` Recovery Banner**:
   - When a session is genuinely active and a second launch is requested, the server returns HTTP `409 Conflict` with `{"error": "...", "status": "<ACTIVE_STATE>"}`.
   - The UI must catch `409` responses and render an immediate, prominent recovery banner containing a one-click **`Force Reset & Abort Active Session`** button wired directly to `/api/session/reset`.

### C. Full State Hydration Across Browser Refresh
- Refreshing the browser tab must **never** lose visibility into an active or completed run.
- On `DOMContentLoaded`, query `/api/session/status` and `/api/runs` to restore:
  - Selected deployment/target and operator name.
  - Active `allow_mutation` / `confirm_destructive` states.
  - Current run ID, step progress matrix, elapsed duration, and live event tail cursor (`seq`).

### D. Live Output & Event Stream Monitor
- Poll `GET /api/runs/<id>/events?since=<seq>` (monotonic sequence cursor) and `GET /api/launch-log` every `1.5s–2.0s` while a run is active.
- Render both:
  1. **Active Execution Progress Matrix**: Per-suite/step status badges (`PASS`, `FAIL`, `WORKING`, `PENDING`, `SKIPPED`), elapsed duration, and direct clickable report links.
  2. **Auto-Scrolling Monospace Telemetry Console**: Real-time stream of structured events and subprocess stdout/stderr.

### E. Run History & In-App Report Viewer (Zero 404 Report Links)
- Display historical and active runs (`GET /api/runs` or `GET /api/reports`) with posture/verdict chips (`PASS`, `FAIL`, `ALL_SAFE`, `ADVISORY`, `NEEDS_IMMEDIATE_ACTION`).
- Clicking any run or suite report opens an in-dashboard report drawer/modal rendering `run-report.md` / `mainReport.md` and `verdict.json` / `findings.json`.
- **On-Demand Report Synthesis Fallback**: When `GET /files/.../run-report.md` or `GET /api/runs/<id>/report` is requested and the markdown report file is missing on disk while `verdict.json` or `summary.json` exists, the server must synthesize the markdown report on the fly rather than returning `404 Not Found`.

### F. In-Tandem Server Lifecycle (`--dashboard` & `ensure_<tool>_running()`)
- Every CLI runner, orchestrator, or security auditor with an accompanying dashboard must support `--dashboard` (and `--port <N>`).
- Implement `ensure_<tool>_running(host="127.0.0.1", port=...)`:
  1. Probe `socket.connect_ex((host, port)) == 0` with a `0.5s` timeout.
  2. If already active, log `[*] <Tool> detected active on http://127.0.0.1:<port>/` and continue without failing.
  3. If free, spawn `ThreadingHTTPServer` (`allow_reuse_address = True`) in a background `daemon=True` thread and print a 70-character `=` banner with the live URL and CSRF token prefix.

### G. Resilient Static `file://` Preview Mode & UI Craft Built-Ins
1. **Offline `file://` Resilience**:
   - Register all DOM event listeners synchronously prior to any `fetch()` calls.
   - If opened directly via `file://` or when the backend daemon is unreachable, display a subtle preview banner (`Offline Preview Mode — start server for live execution`) and populate a sample catalog so every tab, filter, tooltip, and drawer remains 100% interactive.
2. **Studio Curve (`img001.jpg`) Composite Canvas**:
   - Apply the standard dual-layer composite canvas (`linear-gradient(180deg, rgba(9, 13, 11, 0.86) 0%, rgba(9, 13, 11, 0.94) 100%)` over fixed `/backgrounds/img001.jpg` with `file://` relative path fallback) and frosted-glass cards (`backdrop-filter: blur(12px)`).
   - Never clutter the header with redundant theme-selector dropdowns.
3. **Position-Aware Auto-Hiding `TooltipManager`**:
   - Attach floating guidance tooltips (`data-tooltip="..."`, optional `data-shortcut="..."`) to interactive controls.
   - Must comply with WCAG 2.1 AA (1.4.13): hidden by default (`visibility: hidden; pointer-events: none; top: -9999px; left: -9999px`), `<kbd>Escape</kbd>` dismissal, pointer hoverability, auto-hide on `mouseout`/`focusout`/`pointerdown`/`scroll`/`blur` and inactivity timeout (`4000ms`), and viewport boundary clamping with dynamic top/bottom flip.
4. **Header Alignment, CLI Quick-Reference & Attribution Footer**:
   - Left header: brand vector icon inline with tool title and subtitle badge.
   - Right header: active deployment pill, loopback lock indicator (`127.0.0.1:<port>`), and session state badge.
   - Bottom footer: copy-pasteable CLI command equivalents dynamically reflecting the selected deployment and suites, paired with the canonical attribution (`Copyright © 2026 Ted Mwai · TedCraft, a publication of Edulis Secure Systems Hub Limited`) and Apple HIG capsule links (`min-height: 44px`, `border-radius: 9999px`) for GitHub (`https://github.com/teddymwai`), LinkedIn (`https://www.linkedin.com/in/teddymwai/`), and GitLab (`https://gitlab.com/teddymwai`).

---

## 3. Dashboard Security & DOM Hardening Invariants

All dashboard servers and HTML files must pass TedRedCraft Tier 1 SAST and Tier 2 Loopback DAST with zero findings:
1. **Path Confinement (`SEC-01`)**: Every static or artifact file lookup must resolve and verify parent confinement:
   ```python
   target = (base_dir / rel_path).resolve()
   if not target.is_relative_to(base_dir.resolve()):
       return self._json(403, {"error": "Path traversal rejected"})
   ```
2. **CSRF & Origin Guard (`SEC-02`)**: Inject a per-process `secrets.token_urlsafe(24)` token into the HTML template, validate `X-Session-Token` / `X-Panel-Token` / `X-Cockpit-Token` with `hmac.compare_digest()`, and restrict `Origin` to `http://127.0.0.1`, `http://localhost`, and `http://[::1]`.
3. **Bounded Body Read (`SEC-04`)**: Enforce `MAX_BODY_BYTES = 1_048_576` (1 MB) before calling `self.rfile.read()`, returning HTTP `413` on excess.
4. **DOM XSS Prevention (`SEC-JS-INNER-HTML`)**: Prefer `textContent` and `document.createElement()`. Whenever template literals are rendered into HTML containers, pass all dynamic values through a strict HTML entity escaper (`esc()`).
