# Antigravity Operational Commandments

Refer to [AGENTS.md](AGENTS.md) and [HARNESS.md](HARNESS.md) for full architectural guidelines and invariants.

## Quick-Reference Rules (Always-On)

1. **Closed-Loop Autonomous Execution ("No Eye-Tour")**:
   - Never halt or ask unnecessary questions when an empirical probe can answer the question.
   - Ground decisions in concrete schemas (`specs/`, OpenAPI JSONs, CSV matrices, AST inspection).
   - Use Stage 0 read-only probes before authoring or modifying locators, endpoints, or mutations.
   - Self-correct against logs, wire captures, and screenshots before escalating to the human operator.

2. **Environment & Mutation Safety**:
   - Never hardcode environments, base URLs, credentials, or session cookies.
   - Enforce environment resolution (`--deployment` / `-d`).
   - Production is strictly read-only by default. All mutations require staging validation first or explicit `--allow-mutation`.

3. **Asynchronous Convergence & Gracious Settle Windows**:
   - Backend mutations (VM orchestration, async jobs, cloud-init, database migrations) take physical time.
   - Never assert or trigger teardown immediately after initiation.
   - Enforce explicit polling loops with generous time budgets (120s–180s at 5s–10s intervals) and poll for affirmative steady-state convergence (`RUNNING`, `ACTIVE`, `READY`).
   - Honor gracious UI settle intervals (e.g., 3000ms–6000ms post-route transitions or modal animations).

4. **UI Unslop & Apple HIG Standards**:
   - **Zero AI-slop emojis**: Never use emojis in UI buttons, tables, badges, or headers. Use official vector iconography (e.g., Google Fonts Material Symbols).
   - Follow **Quiet Chrome** (unslop architecture): Understated navigation, 4px grid rhythm, single bright focal point, no glowing/gradient slop.
   - Follow **Apple HIG Foundation**: Capsule shapes (`border-radius: 9999px`) for standalone actions, 44x44px minimum hit targets, style prominence hierarchy, and tactile `:active` press states (`scale(0.97)`).
   - **Form Controls & Select Sanitization**: Reset appearance (`appearance: none;`), reserve chevron padding (36px–42px), enforce text truncation (`ellipsis; nowrap; hidden;`), and position chevrons to prevent arrow overlap on long strings.

5. **Dynamic Tool Architecture & Output Hierarchy**:
   - All tools, runners, and scrapers write strictly to `output/<deployment>/<tool>/<YYYY-MM-DD_HHMMSS>/` (or direct tool path for dumps). Never dump to root or flat paths.
   - Standalone web control surfaces under `tools/<tool>/static/` must be named `<tool>_dashboard.html` (never generic `index.html`).
   - Every autonomous run must emit a conforming `verdict.json` (schema v1.0.0) and a human-readable `run-report.md`.

6. **Pre-Commit Secret & Wire Sanitization**:
   - Never commit sensitive session cookies, bearer tokens, or plaintext credentials.
   - Sanitize all `.har` files and HTTP logs before committing: purge cookies, redact bearer tokens, and strip binary asset bloat.

7. **Senior-Engineer Spec Standards**:
   - Maintain clear architectural commentary.
   - Document specifications using precise technical terminology (*ingest, reconcile, serialize, affirmative teardown, idempotent resumption*) without hollow corporate buzzwords.

8. **Ptarmigan (*Lagopus*) Taxonomic Release Nomenclature**:
   - All release tags, PR titles, and build artifacts must strictly pair Semantic Versioning with the biological taxonomy of the **ptarmigan genus (*Lagopus*)**.
   - Git Tag: `Lagopus[Species][Subspecies]_vMAJOR.MINOR.PATCH[-STAGE.N][+BUILD]`.
   - Title: `[Project] Platform vX.Y.Z - Lagopus [Species] [Subspecies]`.
   - Species advances on `MAJOR` (`Lagopus`, `LagopusMuta`, `LagopusLeucura`, `LagopusScotica`); Subspecies advances on `MINOR > 0` (`Helvetica`, `Hyperborea`, `Islandorum`, etc.).
   - Always update `docs/RELEASE_REGISTER.md` upon tagging. Reference: `docs/releases/LAGOPUS_NOMENCLATURE_SPEC.md`.

9. **Interactive Scrollytelling & Walkthrough Standard**:
   - Step-by-step code tours, scenario playbooks, and execution debriefs adopt the dual-pane model (narrative story + sticky state subject).
   - Use Git-friendly Markdown comment directives (`<!-- step: N ... -->`); avoid opaque JSON ASTs.
   - Compile into zero-build, single-file HTML (`walkthrough.html`) with Apple HIG capsule buttons, zero emojis, and line-level focus.
   - Register `"walkthrough": "walkthrough.html"` in `verdict.json` and link in `run-report.md`. Reference: `.agents/skills/interactive-walkthrough/`.

10. **TedRedCraft Security Harness Integration**:
    - **Private Security Core**: Consult and invoke the private security platform at `https://github.com/teddymwai/TedRedCraft` (workstation path: `/Users/ted/Development/TedRedCraft`).
    - **Multi-Stage Security Advisory**:
      * *Development*: Run offline selftests (`python3 -m redcraft selftest`) and TF-IDF search (`python3 -m redcraft search "<query>"`).
      * *Pre-Commit (<1.5s)*: Run Tier 1 polyglot SAST (`python3 -m redcraft audit --target . --mode pre-commit`) blocking unredacted secrets, dangerous sinks (`eval`, `exec`, `subprocess`), unconfined path joins, `.har` leaks, and missing CSRF tokens.
      * *Pre-Push (<4s)*: Run Tier 2 ephemeral loopback DAST (`python3 -m redcraft audit --target . --mode pre-push`) verifying running loopback HTTP servers, CSRF defenses, and bounded socket leases.
      * *Deep Audit & Live Usage*: Run Tier 3 full deep audit (`python3 -m redcraft audit --target . --mode deep-audit`) and launch local Security Cockpit (`python3 -m redcraft cockpit --port 8790`).
      * *Continuous Distillation*: Ingest external repos via Loop C (`python3 -m redcraft upstream ingest / promote`).
    - **Strict Scope-Lock**: All active security probing strictly enforces `assert_local_loopback_scope(host)`. Probing remote hosts is architecturally impossible.
    - **VulnHunter 3 Hard Gates**: Confirm issues only if proven *Reachable*, *Attacker-Controlled*, and granting a *New Capability*. Eliminations require equal evidence.

11. **Port Management, Socket Lifecycle & Session Architecture**:
    - **Dedicated Port Register**: Assign local services to designated ports: `6769` (Telemetry Logserver), `8770` (Recorder Studio), `8780` (Walkthrough Preview), `8787` (Operator Panel / Orchestrator Cockpit), `8790` (Security Cockpit), `8771`–`8786` (Reserved Tooling), `8000`–`8080` (Local Apps).
    - **Strict Loopback Binding**: Always bind exclusively to `127.0.0.1` (or `::1`). Binding to `0.0.0.0` is prohibited.
    - **Socket Reuse**: Always set `ThreadingHTTPServer.allow_reuse_address = True` (`SO_REUSEADDR`) before socket bind to prevent `TIME_WAIT` re-bind hangs.
    - **EADDRINUSE Auto-Recovery**: Trap socket binding collisions (`errno.EADDRINUSE` / 48 / 98) and log recovery commands (`kill $(lsof -t -i :PORT)` and `--port PORT+1`).
    - **Thread-Safe Session State Machines**: Wrap states in `threading.Lock()`, auto-heal dead worker threads back to `IDLE`, guard against overlapping starts with `409 Conflict`, and expose affirmative `/abort` and `/reset` endpoints.
    - **Affirmative Production Safety Interlock**: Enforce requirement of exact `PROD-MUTATE` confirmation token for any mutating operation against production; reject with `403 Forbidden` otherwise.
    - **CSRF, Path Confinement & DOM Defense**: Generate random per-process tokens (`secrets.token_urlsafe(24)`), validate with `hmac.compare_digest()`, whitelist loopback `Origin` headers, enforce a 1MB request body limit (`SEC-04`), confine all static/artifact file reads via `.resolve().is_relative_to()` (`SEC-01`), and escape dynamic HTML (`SEC-JS-INNER-HTML`).

12. **Interactive Operator Dashboard Mandate ("Zero Decorative Tech-Debt")**:
    - Every web dashboard (`tools/<tool>/static/<tool>_dashboard.html`) must be a complete interactive control plane over the CLI's contracts—never a static read-only status page.
    - Ship all 7 interactive capabilities by default:
      1. **Run Creation & Target Deck**: Dynamic deployment selector + inline target onboarding, categorized task/suite selector with search/filter pills and DAG dependency preview (`/api/plan`), operator name input (`"Ted Mwai, QA Lead"`), and `Allow Mutation` / `Confirm Destructive` / `PROD-MUTATE` safety controls.
      2. **Lifecycle & Multi-Session `409` Recovery**: 44x44px Apple HIG capsule buttons (`Run Selected`, `Pause`, `Abort`, `Cancel / Reset`, `Resume Latest`), dead-thread auto-healing, and a prominent `409 Conflict` UI banner with a one-click **`Force Reset & Abort Active Session`** action.
      3. **State Hydration Across Refresh**: Restore selected target, mutation toggles, active run progress, and event cursor (`seq`) on page reload.
      4. **Live Output & Event Monitor**: Poll `/api/runs/<id>/events?since=<seq>` and `/api/launch-log` every 1.5s–2s into a step progress matrix and auto-scrolling monospace console.
      5. **Run History & In-App Report Drawer**: View past runs and render `run-report.md` / `mainReport.md` and `verdict.json` in-app, synthesizing markdown reports on demand from `verdict.json` if missing on disk so links never 404.
      6. **In-Tandem Daemon Lifecycle (`--dashboard`)**: Support `--dashboard` on CLIs via `ensure_<tool>_running()` (`socket.connect_ex` pre-flight check + background daemon thread + 70-char `=` console banner).
      7. **Resilient `file://` Offline Preview & UI Craft**: Register DOM listeners before network calls so `file://` opens interactively in preview mode; use the **Studio Curve (`img001.jpg`)** dual-layer composite canvas (zero theme-selector dropdowns); attach position-aware `TooltipManager` guidance; and render a copy-pasteable CLI command footer.

13. **Full-SDLC, Reporting & Git Promotion Protocol**:
    - **Planning**: Critique proposals with `ADOPT` / `REJECT` / `HOLD` before coding; author contracts first (CLI = 1st consumer); maintain 1:1 registry $\leftrightarrow$ `manifest.toml` $\leftrightarrow$ physical `specs/` parity; keep a single roadmap (`docs/UPCOMING_FEATURES.md`).
    - **In-Dev & Dual Reporting**: Discover entities dynamically or self-provision `pw-tc-<hex8>` fixtures (tearing down child before parent); include a 5-section `README.md` in every `tools/<tool>/` folder; escalate hard blockers via the **Developer Redesign & Input Ledger (`LEDGER-XX`)**; emit `verdict.json` + `run-report.md` for suite runs and the **UltraRed Reporting Bundle** (`reports/<projectTitle>_<YYYYMMDD_HHMMSS>/mainReport.md`, `findings.json`, `summary.json`) for audits.
    - **Pre-Commit & Commit Format**: Never run `git add -A` or `git add .` (stage explicit paths only); ship tests & docs with the feature; pass all 7 pre-commit sanitization gates (`compileall`, `--selftest`, contract tests, Tool Rule #4, Release Register sync, RedCraft Tier 1 SAST `<1.5s`, staged secret/path regex scan). Format commits with `type(scope): summary <= 72 chars` + `Why:` / `Trade-off:` / `Touches:` (preserving operator-specified subjects verbatim).
    - **3-Tier Promotion & History Governance**: Promote `beta/unstable-nightly` (or `beta-<Feature>`) $\rightarrow$ `staging` (Tier 2 Loopback DAST `<4s`) $\rightarrow$ `main` (`--ff-only`), publish verbose GitHub Release notes (`gh release create`), use the **Commit-and-Purge** pattern for legacy scripts, and use `gh release delete <tag> --yes --cleanup-tag` for `GH013` protected tags. Reference: `docs/push2git.md`.

