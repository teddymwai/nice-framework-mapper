# Project Base Mantra & Architecture Constitution

> **Project Name:** NICE Framework Mapper  
> **Lead / Owner:** Ted Mwai  
> **Repository Scope:** Architectural governance, agent invariants, and autonomous verification harness.

---

## 1. Brand Identity & Nomenclature Standard

- **Project Canonical Name**: Always format project names in their canonical casing across documentation, logs, and code (e.g., `NICE Framework Mapper`). Never squash names or invent arbitrary variations.
- **Tone & Persona**: Authoritative, concise, senior-engineer rigor. Avoid informal AI conversational filler ("Certainly!", "I'd be happy to help!").

---

## 2. Environment Architecture & Lifecycle Policy

| Environment | Purpose / Scope | Default Access Mode | Promotion Policy |
|---|---|---|---|
| **Local / Dev** | Local workstation sandbox & offline selftests | Read / Write | Pre-flight validation gate before pushing |
| **Staging / Beta** | Primary testing ground, CI/CD pipeline, and empirical UI/API probing | Read / Write (with safety guards) | All features and test suites must pass 100% here first |
| **Production** | Live system of record | **Strictly Read-Only** | Only promoted after staging stability verification passes; mutations require `--allow-mutation` and explicit credentials |

---

## 3. UI Development & Design Mantra (Unslop + Apple HIG)

Every front-end view, dashboard, or report component must follow these strict guidelines:

### A. Color Palette & Craft Hierarchy
- Ground the interface in a deep, executive base tone (e.g., dark-mode charcoal `#0d1310` or enterprise slate `#0f172a`).
- Text readability must be razor sharp (high-contrast off-whites `#f0f6f2` for primary body copy, `#9bb1a4` for secondary metadata).
- Single focal point: Reserve bright accent colors for primary call-to-actions and real-time status gauges. Ban gratuitous gradients, rainbow borders, and neon mesh backgrounds.

### B. Iconography & Zero "AI-Slop"
- **Strictly No Emojis**: Never use emojis (no 🚀, ✨, 🔥, 🤖, ✅) in UI buttons, tables, badges, or headers.
- **Vector Icons Only**: Use standard vector icon libraries exclusively (e.g., Google Fonts Material Symbols, Heroicons, or Lucide).
- Icons must remain tinted with secondary/muted text roles to avoid visual noise.

### C. Apple HIG Component Foundation
- **Shapes**:
  - Capsule (`border-radius: 9999px`) for standalone pill actions, status tags, and horizontal toolbar buttons.
  - Rounded Rectangle (`border-radius: 8px`–`12px`) for cards, modal dialogs, and stacked forms.
- **Hit Targets**: Minimum **44x44px** hit target area on all interactive buttons, selects, and inputs.
- **Tactile Response**: Instant tactile press feedback (`transform: scale(0.97)` on `:active`).
- **Form Controls & Select Sanitization**:
  - Explicit cross-browser appearance resets: `appearance: none; -webkit-appearance: none;`.
  - Dedicated chevron right padding: `padding-right: 38px`.
  - Text truncation: `text-overflow: ellipsis; white-space: nowrap; overflow: hidden;`.
  - Position chevron cleanly to eliminate arrow collision on long strings.

---

## 4. Dynamic Tool Architecture Mandate

All automation tools, test harnesses, scrapers, and scripts must adhere to:

1. **Zero Hardcoded Secrets or URLs**: Resolve all target URLs, API hosts, and environments dynamically via centralized configuration or CLI flags (`--deployment` / `-d`).
2. **Automated Session Resolution**:
   - Check and reuse cached session tokens before requesting fresh authentication.
   - Support automated headless authentication or `--token` / `--cookie` override flags.
3. **Safety Guards**: Intercept mutating HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`) with safety checks. Never mutate state against production without affirmative operator override.
4. **Dashboard Naming Convention**: Web control surfaces under `tools/<tool>/static/` must be named `<tool>_dashboard.html` (e.g. `runner_dashboard.html`). Generic `index.html` is prohibited as a primary file name.
5. **Standard Output Hierarchy**:
   ```text
   output/<deployment>/<tool>/<YYYY-MM-DD_HHMMSS>/
   ├── screenshots/       # Browser stage captures
   ├── wire_telemetry.json# Network logs / sanitized payloads
   ├── console.log        # Raw execution log
   ├── verdict.json       # Conforming machine-readable result
   ├── run-report.md      # Human-readable summary
   └── walkthrough.html   # Standalone scrollytelling player (optional)
   ```
6. **Interactive Scrollytelling Walkthrough Standard**:
   - Complex execution playbooks, multi-stage test debriefs, and architecture tours must adopt the dual-pane model (linear narrative rail on left + sticky state canvas on right).
   - Author in pure Markdown using unobtrusive HTML comment directives (`<!-- step: N subject="..." highlight="..." ... -->`).
   - Compile into self-contained single-file HTML players (`walkthrough.html`) adhering to Quiet Chrome, Apple HIG capsule controls, zero emojis, and glowing line-level focus.
   - When test suites run, register `"walkthrough": "walkthrough.html"` in `verdict.json` artifacts and link in `run-report.md`.

---

## 5. Security Tooling & TedRedCraft Protocol

All security verifications, static code scans, loopback dynamic probing, and adversarial audits must integrate the **TedRedCraft** (`redcraft`) security platform:

- **Private Repository URI**: `https://github.com/teddymwai/TedRedCraft`
- **Canonical Workstation Clone**: `/Users/ted/Development/TedRedCraft`
- **Core Technology**: 100% Python 3.11+ Standard Library (Zero External Dependencies).

### A. Lifecycle Stage Advisory: When to Run Security Tooling

| Stage | Trigger / Context | Verification Tool & Command | Target Runtime | Scope & Checks Enforced |
|---|---|---|---|---|
| **Development** | Feature coding, test authoring, and local refactoring | `python3 -m redcraft selftest`<br>`python3 -m redcraft search "<query>"` | <3s | Offline benchmark. Search blackboard for prior findings, waivers, and root causes. Loopback scope-lock check. |
| **Pre-Commit** | Git staging and commit verification | `python3 -m redcraft audit --target . --mode pre-commit` | <1.5s | **Tier 1 Fast Polyglot SAST**: Scans staged diffs for unredacted secrets, dangerous sinks (`eval`, `exec`, `subprocess`), unconfined path joins (`os.path.join`), `.har` cookie leaks, and missing CSRF headers. |
| **Pre-Push** | Preparing branch push or opening pull requests | `python3 -m redcraft audit --target . --mode pre-push` | <4s | **Tier 2 Ephemeral Loopback DAST**: Probes running loopback HTTP servers, CSRF defenses, Origin headers, tokens, and ephemeral socket closeout. |
| **Live Usage & Deep Audit** | Pre-release verification, security reviews, and Cockpit monitoring | `python3 -m redcraft audit --target . --mode deep-audit`<br>`python3 -m redcraft cockpit --port 8790` | On-Demand | **Tier 3 Deep Audit & Cockpit Dashboard**: Loopback canary testing, full AST taint tracing, Cairn recovery, and local web UI (port 8790, loopback only, per-session CSRF token, strict CSP, 1MB limit). |
| **Upstream Distillation** | Ingesting external security repos & rules | `python3 -m redcraft upstream ingest <slug>`<br>`python3 -m redcraft upstream promote <slug>` | Offline | **Loop C Learning Pipeline**: Ingest rules (`status = "observed"`), evaluate Net-Gain vs. Tech-Load, run held-out falsification battery (100% catch on vulnerable, 0% FP on benign), and commit attested promotion. |

### B. The 4 Disciplined Rules
1. **Explicit Scope-Lock Pre-Flight**: Active DAST and pentest operations must strictly call `assert_local_loopback_scope(host)` before opening network sockets. Remote infrastructure is never scanned.
2. **Evidence-First Anti-Hallucination Rubric**: Classify all findings as `CONFIRMED`, `CANDIDATE`, `DISPROVED`, or `HARDENING_NOTE`. Eliminations require evidence at the same standard as confirmations.
3. **Root-Cause 3-Tuple Deduplication**: Group redundant findings sharing `(root_cause, component, prerequisite)` into one canonical finding.
4. **Bounded Lease Closeout**: Loopback servers run in ephemeral leases that tear down sockets and wipe temp dirs in `finally:` blocks.

### C. VulnHunter 3 Hard Gates
No finding may be marked `CONFIRMED` unless it conclusively passes all three gates:
- **Gate 1 (Reachable)**: Proven execution path from active routes down to the sink in production code.
- **Gate 2 (Attacker-Controlled)**: Input originates from an untrusted caller / external input.
- **Gate 3 (New Capability)**: Grants an unauthorized capability (bypass, traversal, execution, leak).

---

## 6. Local Port Allocation, Socket Lifecycle & Session Architecture

All local HTTP control planes, test runners, recording studios, and interactive dashboards authored within this harness (e.g. `recorder_studio`, `security_cockpit`, `walkthrough_preview`) must strictly adhere to these port management and session handling standards:

### A. Dedicated Local Port Allocation Register
- **`6769`**: **Telemetry & Warmup Logserver** (`tools/template_runner/boot_mct_logserver.py`) — Embedded HTTP telemetry daemon, concurrency dials, and warmup-skip control plane.
- **`8770`**: **UI Recorder Studio** (`tools/recorder_studio/server.py`) — Headed Playwright recording plane, semantic action listener, and trace extraction.
- **`8780`**: **Walkthrough Preview Dashboard** (`templates/walkthrough_engine.py`) — Local dual-pane scrollytelling preview server.
- **`8787`**: **Operator Panel / Orchestrator Cockpit** (`tools/operator_panel/server.py`) — Multi-suite test batch orchestrator control surface, DAG planner, and live event monitor.
- **`8790`**: **Security Cockpit** (`tools/security_cockpit/server.py` or `redcraft cockpit`) — TedRedCraft local security dashboard, finding explorer, report viewer, and upstream manager.
- **`8771`–`8786`**: **Reserved Tooling Range** — Auxiliary local inspection dashboards and proxy surfaces.
- **`8000`–`8080`**: **Local Application Services** — Mock servers and local test targets.

### B. Strict Loopback Binding & Socket Lifecycle
- **Strict `127.0.0.1` Binding**: Local tool servers must bind strictly to `127.0.0.1` (or `::1`). Binding to `0.0.0.0` is strictly prohibited.
- **Immediate Socket Reuse (`SO_REUSEADDR`)**: Always set `ThreadingHTTPServer.allow_reuse_address = True` before socket bind to prevent TCP `TIME_WAIT` re-bind hangs.
- **Port Conflict Detection & Auto-Recovery**: Catch `OSError` (`errno.EADDRINUSE`, POSIX codes 48 on macOS / 98 on Linux) and provide immediate recovery options:
  - Active URL: `http://{host}:{port}/`
  - Terminate conflicting process: `kill $(lsof -t -i :{port})`
  - Alternate port fallback: `--port {port + 1}`

### C. Thread-Safe Session State Machines & Concurrency Interlocks
- **Thread Safety**: Wrap all state mutations inside `threading.Lock()`.
- **States**: `IDLE` $\rightarrow$ `STARTING` $\rightarrow$ `RECORDING` / `WORKING` $\rightarrow$ `INGESTING` $\rightarrow$ `COMPLETED` (or `ERROR`).
- **Worker Auto-Healing**: If a worker thread died unexpectedly while the state was active, auto-recover state to `IDLE`.
- **Multi-Session Lockout**: Return `409 Conflict` if a new start is requested while a session is active.
- **Affirmative Abort & Reset**: Expose `/api/.../abort` and `/api/.../reset` to signal `threading.Event`, join worker threads with timeout, and reset state.

### D. Production Affirmative Mutation Interlock (`PROD-MUTATE`)
Mutations against production (`deployment in ("production", "prod", "cyberranges.com")`) require an explicit confirmation token: `prod_mutation_token == "PROD-MUTATE"`. Reject with `403 Forbidden` if missing or invalid.

### E. CSRF Defense, Origin Whitelisting & Payload Limits
- Generate per-process dynamic CSRF tokens (`secrets.token_urlsafe(24)`).
- Inject into served HTML (`__TOKEN_PLACEHOLDER__`) and validate with constant-time `hmac.compare_digest()`.
- Enforce loopback Origin whitelist (`http://127.0.0.1`, `http://localhost`, `http://[::1]`).
- Cap request body sizes at `MAX_BODY_BYTES = 1_048_576` (1 MB).

### F. Automated Browser Session Resolution & Artifact Synthesis
- Reconcile session cookies via cached credentials or headless login; sanitize cookie domains (leading dot `.cyberranges.com`); inject into Playwright contexts.
- Write all session artifacts to `output/<deployment>/<tool>/<suite_tag>_<timestamp>/` emitting `run-report.md`, `wire_telemetry.json` / `wire.har`, `trace.zip`, and `verdict.json`.

### G. Interactive Operator Dashboard Mandate ("Zero Decorative Tech-Debt")
Every local web dashboard (`tools/<tool>/static/<tool>_dashboard.html`) must act as a full interactive control plane over the CLI's contracts (never a passive read-only status page):
1. **Run Creation & Target Configuration Deck**: Dynamic deployment selector (`GET /api/config`) + inline target onboarding (`POST /api/deployments/onboard`), categorized suite/task picker with search/filter pills and DAG dependency preview (`GET /api/plan`), operator identity input (defaulting to `"Ted Mwai, QA Lead"`), and safety toggles (`Allow Mutation`, `Confirm Destructive`, plus conditional `PROD-MUTATE` token input on production targets).
2. **Active Lifecycle Management & Multi-Session `409` Recovery**: 44x44px Apple HIG capsule actions (`Run Selected`, `Pause at Next Barrier`, `Abort`, `Cancel / Reset Session`, `Resume Latest`). Auto-heal dead worker threads back to `IDLE`, and when a `409 Conflict` occurs, display an immediate UI recovery banner with a one-click **`Force Reset & Abort Active Session`** button wired to `/api/session/reset`.
3. **State Hydration Across Refresh**: On page load, query `/api/session/status` and `/api/runs` to restore active deployment, mutation toggle state, running progress matrix, and live event stream cursor (`seq`).
4. **Live Output & Event Stream Monitor**: Incremental polling (`GET /api/runs/<id>/events?since=<seq>` and `GET /api/launch-log` every 1.5s–2s) updating a per-step progress matrix and an auto-scrolling monospace console.
5. **Run History & In-App Report Drawer**: Browse historical and active runs (`GET /api/runs` / `GET /api/reports`) and view `run-report.md` / `mainReport.md` and `verdict.json` in-app. If `run-report.md` is missing on disk while `verdict.json` exists, synthesize the markdown report on demand so report links never 404.
6. **In-Tandem Daemon Lifecycle (`--dashboard` & `ensure_<tool>_running`)**: CLI runners and security auditors support `--dashboard`, probing `socket.connect_ex((host, port)) == 0` to reuse an active instance or spawn a background daemon thread with a 70-char `=` console banner.
7. **Resilient `file://` Offline Preview & UI Craft**: Register DOM listeners before network fetches so `file://` opens cleanly in preview mode; use the **Studio Curve (`img001.jpg`)** dual-layer composite canvas (no redundant theme-selector dropdowns); attach position-aware `TooltipManager` floating guidance (WCAG 1.4.13); and include a copy-pasteable CLI quick-reference footer.

---

## 7. Living Platform Invariant Register & Tie-Break Matrix

When ambiguity arises between API documentation, UI text, and live runtime responses, agents must apply the platform ground truths recorded below. Whenever an agent discovers a new non-obvious platform behavior or backend quirk, it **must** append a new invariant row:

| Invariant ID | Domain / Component | Ambiguity / Pitfall | Ground Truth & Required Code Pattern |
|---|---|---|---|
| `INV-01` | Authentication / Routes | Case sensitivity in route URLs | Always sanitize route slugs and usernames with `.lower()` unless explicitly UUID-bound. |
| `INV-02` | API Response Contracts | Deletion status codes (`204` vs `404` vs `400`) | Deletion confirmation must always perform an affirmative follow-up probe rather than trusting fire-and-forget status codes. |
| `INV-03` | UI Modals & Portals | Dialog buttons rendered in root DOM portals | Match action buttons inside modal containers (e.g. `button:has-text("CONFIRM")`) rather than ambiguous parent selectors. |
| `INV-04` | Tag / Multi-Select Inputs | Form state does not commit upon text entry | Always execute `.fill(text)` followed immediately by `.press("Enter")`. |
| `INV-05` | Asynchronous Orchestration | Services take non-zero time to boot/provision | Never assert immediately. Enforce a polling budget (120s @ 5s interval) and check for affirmative steady-state. |
| `INV-SEC-01` | Security / DAST Probes | Scanning remote staging/prod targets | Strictly enforce `assert_local_loopback_scope(host)`. Resolve via `socket.getaddrinfo()` and check `ipaddress.is_loopback`. Remote active scanning is strictly blocked. |
| `INV-SEC-02` | Security / Findings Triage | False-positive vulnerability reports | Never mark `CONFIRMED` without satisfying VulnHunter's 3 Hard Gates (Reachable, Attacker-Controlled, New Capability) and 5-Lens Adversary review. Eliminations require equal evidence. |
| `INV-SEC-03` | Security / Local Web Surfaces | Cross-origin browser tab hijacking & path traversal | All local tool web surfaces must bind `127.0.0.1`, issue per-process CSRF tokens (`secrets.token_urlsafe`), check `hmac.compare_digest`, enforce loopback Origin headers, confine paths via `.resolve().is_relative_to()`, cap bodies at 1MB, and escape DOM `innerHTML`. |
| `INV-SEC-04` | Security / Git Gates | Unverified code pushed to repository | Pre-commit must pass Tier 1 SAST (<1.5s); pre-push must pass Tier 2 ephemeral loopback DAST (<4s). |
| `INV-NET-01` | Networking / Port Binding | Local dashboard bound to `0.0.0.0` | Strictly prohibited. Local dashboards and recording planes must bind exclusively to `127.0.0.1` or `::1`. |
| `INV-NET-02` | Networking / Port Collisions | Server crash on `EADDRINUSE` | Catch `errno.EADDRINUSE` (POSIX 48/98), log `kill $(lsof -t -i :PORT)` recovery command, and provide `--port` increment fallback. |
| `INV-NET-03` | Concurrency / Worker Threads | Zombie threads locking server state | Wrap session state in `threading.Lock()`, auto-heal dead worker threads back to `IDLE`, and return `409 Conflict` on overlapping start calls. |
| `INV-NET-04` | Safety / Production Mutations | Accidental state mutation on production | Require affirmative token `PROD-MUTATE` and reject unauthorized requests with `403 Forbidden`. |
| `INV-UI-01` | Dashboards / Interactivity | Static read-only "decorative tech-debt" dashboards | Every dashboard must support run creation, live log/event tailing, 409 one-click reset, state hydration on page refresh, and in-app report rendering with on-demand markdown synthesis fallback. |
| `INV-UI-02` | Dashboards / Daemon Lifecycle | Manual multi-terminal server startup friction | Support `--dashboard` on CLIs via `ensure_<tool>_running()` (`socket.connect_ex` pre-flight check + background daemon thread + 70-char `=` startup banner). |
| `INV-UI-03` | Dashboards / Canvas & Tooltips | Cluttered theme dropdowns & clipped tooltips | Standardize on Studio Curve (`img001.jpg`) composite canvas (`file://` fallback, zero theme selectors), position-aware `TooltipManager` (`top: -9999px` init + boundary flip), and left-inline brand icon / right-aligned port badges. |
| `INV-ARC-01` | Architecture / Seams & Imports | Seam rot & circular root-shim imports | CLI must be 1st consumer of every contract seam; internal modules (`lib/framework/`, `lib/suites/`) must never import root shims; every suite requires 1:1 registry, `manifest.toml`, and physical `specs/` file parity. |
| `INV-ARC-02` | Testing / Dynamic Fixtures | Hardcoded tenant IDs & teardown dependency errors | Discover assets dynamically or self-provision `pw-tc-<hex8>` fixtures; tear down child entities before parent entities; never auto-delete non-`pw-tc-` entities. |
| `INV-GIT-01` | Git / Staging & Pre-Commit | Leaked secrets or broken imports in commits | Never run `git add -A` or `git add .`; stage explicit paths; ship tests and 5-section `README.md` with the feature; pass all 7 pre-commit sanitization gates (`compileall`, `--selftest`, RedCraft Tier 1 SAST, regex secret check). |
| `INV-GIT-02` | Git / Commits & Promotion | Unstructured commit history & `GH013` tag locks | Format commits with `type(scope)` + `Why:` / `Trade-off:` / `Touches:` (preserving operator-specified subjects verbatim); promote `beta/unstable-nightly` $\rightarrow$ `staging` $\rightarrow$ `--ff-only` `main`; use Commit-and-Purge for legacy scripts and `gh release delete --cleanup-tag` for `GH013`. |

---

## 8. Code Commentary & Senior-Engineer Spec Standard

1. **Comment Intent, Not Syntax**: Explain *why* an invariant is handled or *why* a delay is necessary, not what Python/JavaScript keywords do.
2. **Standard Vocabulary**:
   - Use precise engineering vocabulary: *ingest, reconcile, serialize, affirmative teardown, steady-state convergence, idempotent resumption, telemetry sanitization*.
   - Strictly prohibit empty status-meeting fluff ("working hard on this", "magical solution").

---

## 9. Software Release Nomenclature Specification (Ptarmigan / Lagopus Protocol)

All tagged releases, pull requests, and binary artifacts must strictly follow the biological taxonomy of the **ptarmigan genus (*Lagopus*)** paired with Semantic Versioning:

### A. Canonical Formats
- **Git Tag & Machine Identifier**: `Lagopus[Species][Subspecies]_vMAJOR.MINOR.PATCH[-STAGE.N][+BUILD]`
  - *Major (.0)*: `LagopusLeucura_v3.0.0`
  - *Minor feature*: `LagopusMutaHelvetica_v2.1.0`
  - *Patch fix*: `LagopusMutaHelvetica_v2.1.1`
  - *Pre-release*: `LagopusLeucura_v3.0.0-rc.1`
- **Human Release Title**: `NICE Framework Mapper Platform vMAJOR.MINOR.PATCH[-STAGE.N] - Lagopus [Species] [Subspecies]`
- **Binary Suffix**: `Lagopus[Species][Subspecies]_vMAJOR.MINOR.PATCH-<os>-<arch>`

### B. Biological Taxonomy Progression (Grouse / Ptarmigan Subfamily)
- **Species (`MAJOR`)**:
  - `v1.x`: `Lagopus` (*Lagopus lagopus* — Willow ptarmigan)
  - `v2.x`: `LagopusMuta` (*Lagopus muta* — Rock ptarmigan)
  - `v3.x`: `LagopusLeucura` (*Lagopus leucura* — White-tailed ptarmigan)
  - `v4.x`: `LagopusScotica` (*Lagopus scotica* — Red grouse / Scottish ptarmigan)
- **Subspecies (`MINOR > 0`)**: Assigned dynamically from the priority pool in alphabetical order:
  `Helvetica`, `Hyperborea`, `Islandorum`, `Japonica`, `Millaisi`, `Nivalis`, `Pyrenaica`, `Rupestris`, `Saxatilis`, `Welchi`.
- **Lineage Preservation**: Patches and promotions retain parent species and subspecies verbatim.
- **Register Synchronization**: Every release must append a row to [`docs/RELEASE_REGISTER.md`](docs/RELEASE_REGISTER.md). Specification detailed in [`docs/releases/LAGOPUS_NOMENCLATURE_SPEC.md`](docs/releases/LAGOPUS_NOMENCLATURE_SPEC.md).

---

## 10. Full-SDLC Engineering, Reporting & Git Promotion Governance

1. **Planning ("Critic Before Code" & Anti-Seam-Rot)**:
   - Triage architectural proposals into **`ADOPT`**, **`REJECT`**, or **`HOLD`** before modifying code.
   - Define contracts (`manifest.toml`, `<suite_code_lower>.contract.toml`, `verdict.schema.json`, `events.jsonl`, `control.json`) first; the CLI must be the primary consumer of every seam.
   - Consolidate future work into a single roadmap (`docs/UPCOMING_FEATURES.md`); paginate older `CHANGELOG.md` entries inside `<details>` blocks; externalize volatile daily sprint notes to Notion.
2. **In-Development Resilience & Dual Reporting**:
   - Never hardcode tenant entity IDs; discover dynamically or self-provision `pw-tc-<hex8>` fixtures and tear down in reverse dependency order.
   - Include a 5-section `README.md` in every `tools/<tool>/` folder.
   - When blocked by missing credentials, isolated networks, or backend bugs, log the item in the **Developer Redesign & Input Ledger (`LEDGER-XX`)** rather than inventing fake mocks.
   - Emit `verdict.json` + `run-report.md` for suite executions (`output/<deployment>/<tool>/<timestamp>/`) and the **UltraRed Reporting Bundle** (`reports/<projectTitle>_<YYYYMMDD_HHMMSS>/mainReport.md`, `findings.json`, `summary.json` with Executive Scorecard, *What Was Run*, *What Was Safe*, *Immediate Attention*, *Other Items*, and *ARTEX 7-Check Oracle*) for security and repository audits.
3. **Pre-Commit 7-Check Gate & Commit Protocol**:
   - Stage explicit file paths only (**never `git add -A` or `git add .`**); ship tests and docs in the same commit as the feature.
   - Pass all 7 pre-commit gates (`compileall -q`, `--selftest` 1:1 registry/manifest/spec-on-disk parity, contract/unit tests, Tool Rule #4 audit, Release Register sync, TedRedCraft Tier 1 SAST `<1.5s`, and staged path/secret regex checks).
   - Format commits as `type(scope): imperative summary <= 72 chars` followed by `Why:`, `Trade-off:`, and `Touches:` (preserving operator-requested subjects verbatim).
4. **3-Tier Branch Promotion & History Governance**:
   - Promote code through `beta/unstable-nightly` (or `beta-<Feature>`) $\rightarrow$ `staging` (Tier 2 Loopback DAST `<4s`) $\rightarrow$ `main` (`git merge --ff-only origin/staging`). Never commit directly to `main` or force-push shared branches.
   - Pair every annotated Ptarmigan (*Lagopus*) tag with published GitHub Release notes (`gh release create`).
   - Use the **Commit-and-Purge Reference Pattern** (`chore(archive): ...` followed immediately by `Cleaned up legacy files - see prev <sha> for legacy details.`) for historical legacy scripts, and `gh release delete <tag> --yes --cleanup-tag` to resolve `GH013` protected tag errors. Reference: [`docs/push2git.md`](docs/push2git.md).

