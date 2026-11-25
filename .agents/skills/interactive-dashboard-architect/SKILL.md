---
name: "interactive-dashboard-architect"
description: "Design, build, upgrade, and audit interactive local operator dashboards, control planes, and monitoring cockpits (<tool>_dashboard.html + server.py). Use whenever creating or refactoring a tool web UI so it includes interactive run creation, live event streaming, multi-session 409 conflict reset, state hydration across browser refreshes, in-tandem daemon launch, on-demand report viewing, Studio Curve composite canvas, TooltipManager, and offline file:// fallback."
---

# Interactive Operator Dashboard & Control Plane Architect

Distilled from `CYBER RANGES Agents/tools/operator_panel/`, `CYBER RANGES Agents/tools/recorder_studio/`, `CYBER RANGES Agents/tools/template_runner/mct_logserver_dashboard.html`, and `TedRedCraft/tools/security_cockpit/`.

## When to Activate
- Whenever the user asks to create, improve, restyle, or fix a dashboard, operator panel, recording studio, or local web console.
- Whenever a CLI runner, test orchestrator, or security tool needs an accompanying web control plane (`--dashboard`).
- When auditing an existing HTML dashboard to ensure it is not a static "decorative tech-debt" status page.

---

## 1. Core Architectural Philosophy: Zero Decorative Tech Debt

1. **Anti-Seam-Rot**: The CLI runner is the first consumer of all manifests (`manifest.toml`), contracts (`.contract.toml`), event streams (`events.jsonl`), and IPC control files (`control.json`). The dashboard is a second consumer of those exact artifacts.
2. **Canonical File Naming**: Always place the dashboard at `tools/<tool>/static/<tool>_dashboard.html` (never generic `index.html`). Alias `/` and `/index.html` in `do_GET` to serve `<tool>_dashboard.html`.
3. **Reference Implementations**: Use `templates/server_boilerplate.py` and `templates/dashboard_boilerplate.html` as the canonical starting foundation.

---

## 2. The 7 Mandatory Interactive Capabilities Checklist

Before declaring any dashboard complete, verify all 7 capabilities:

- [ ] **1. Run Creation & Target Configuration Deck**:
  - Dynamic deployment/target dropdown (`GET /api/config` / `GET /api/deployments`) + inline target onboarding (`POST /api/deployments/onboard`).
  - Categorized task/suite selector with portal/domain tabs, search filter, status filter pills (`All`, `Failed Only`, `Passed`, `Mutating`), batch `Select Filtered` / `Clear`, and DAG plan preview (`GET /api/plan`).
  - Operator identity field defaulting to `"{{PROJECT_OWNER}}, QA Lead"` (or `"Ted Mwai, QA Lead"`), recorded into run artifacts.
  - Safety toggles (`Allow Mutation`, `Confirm Destructive`) + conditional `PROD-MUTATE` confirmation token input when a production target is selected.
- [ ] **2. Active Lifecycle Controls & Multi-Session `409` Recovery**:
  - Apple HIG 44x44px capsule buttons: `Run Selected`, `Pause at Next Barrier`, `Abort`, `Cancel / Reset Session`, `Resume Latest`.
  - Server-side `auto_heal()` that resets state to `IDLE` if a previous worker thread or subprocess died unexpectedly.
  - Client-side `409 Conflict` handler that renders an immediate recovery banner with a one-click **`Force Reset & Abort Active Session`** button wired to `POST /api/session/reset`.
- [ ] **3. Full State Hydration Across Browser Refresh**:
  - On page load, `hydrateState()` queries `/api/session/status` and `/api/runs` to restore active deployment, mutation toggle state, running progress matrix, and event stream cursor (`seq`).
- [ ] **4. Live Output & Event Stream Monitor**:
  - Incremental polling (`GET /api/runs/<id>/events?since=<seq>` and `GET /api/launch-log` every 1.5s–2s) updating a per-step progress matrix and an auto-scrolling monospace event console.
- [ ] **5. Run History & In-App Report Drawer (With On-Demand Synthesis)**:
  - Historical runs list (`GET /api/runs`, `GET /api/reports`) with clickable report drawers rendering `run-report.md` / `mainReport.md` and `verdict.json`.
  - If `run-report.md` is missing on disk while `verdict.json` exists, synthesize `run-report.md` on the fly so report links never 404.
- [ ] **6. In-Tandem Server Daemon Lifecycle (`--dashboard` & `ensure_<tool>_running`)**:
  - Pre-flight check via `socket.connect_ex((host, port)) == 0`; reuses active server or spawns a background daemon thread with a 70-char `=` console banner.
- [ ] **7. Resilient `file://` Offline Preview & UI Craft**:
  - Synchronous event listener registration before network calls; graceful offline preview banner + sample catalog when opened via `file://`.
  - Studio Curve (`img001.jpg`) composite canvas (`rgba(9, 13, 11, 0.86..0.94)` over fixed `/backgrounds/img001.jpg` with `file://` fallback; no theme selector dropdown).
  - Position-aware `TooltipManager` (WCAG 1.4.13, `<kbd>Escape</kbd>` dismiss, viewport clamping) and copy-pasteable CLI quick-reference footer.

---

## 3. REST & IPC Endpoint Contract

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/`, `/<tool>_dashboard.html`, `/index.html` | Serves `<tool>_dashboard.html` with `__SESSION_TOKEN_PLACEHOLDER__` injected and strict CSP header. |
| `GET` | `/api/config` (or `/api/deployments`) | Returns configured deployments/targets, default deployment, and `production` / `read_only` flags. |
| `GET` | `/api/catalog?deployment=<d>` | Returns suites/tasks grouped by domain/portal, profiles, and latest verdict per suite. |
| `GET` | `/api/plan?suites=A,B&profile=P` | Resolves DAG execution order and auto-included dependencies. |
| `GET` | `/api/session/status` | Auto-heals dead threads and returns current session state, active run ID, elapsed seconds, and recent actions/events. |
| `GET` | `/api/runs?deployment=<d>` | Lists historical and active runs (`verdict.json` / `summary.json`). |
| `GET` | `/api/runs/<run_id>/events?since=<seq>` | Returns incremental NDJSON events with `seq > since`. |
| `GET` | `/api/runs/<run_id>/report` | Returns `run-report.md` / `mainReport.md` and `verdict.json` (synthesizing markdown on demand if missing). |
| `POST` | `/api/session/start` (or `/api/runs`) | Validates CSRF token, loopback Origin, 1MB body cap, `409 Conflict` lock, and `PROD-MUTATE` token before spawning worker. |
| `POST` | `/api/session/stop` | Signals graceful barrier drain (`stop_event.set()` / `control.json` / 1st `SIGINT`). |
| `POST` | `/api/session/abort`, `/api/session/reset` | Immediately aborts active worker/subprocess, joins with timeout, and resets state to `IDLE`. |
| `POST` | `/api/deployments/onboard` | Dynamically registers a new target deployment into runtime config. |
| `GET` | `/files/<rel_path>`, `/backgrounds/<file>` | Confined static/artifact serving using `target.resolve().is_relative_to(base_dir.resolve())`. |
