---
name: dynamic-tooling-and-outputs
description: Dynamic environment resolution, strict output folder hierarchies, secret redaction, and verdict.json observability contracts.
trigger: always_on
---

# Dynamic Tooling, Output Hierarchy, & Redaction

## 1. Dynamic Environment Resolution
- Never hardcode base URLs, ports, or credentials in scripts or test runners.
- Accept an explicit `--deployment` / `-d` argument (e.g. `local`, `staging`, `prod`) to resolve base URLs from a centralized configuration source or environment variables.
- Production environments must default to read-only mode unless an explicit `--allow-mutation` override is passed.

## 2. Mandatory Output Hierarchy
- All test runs, extractors, and automated tools must store generated artifacts under a strictly partitioned directory:
  ```text
  output/<deployment>/<tool>/<YYYY-MM-DD_HHMMSS>/
  ├── screenshots/
  ├── console.log
  ├── wire_telemetry.json
  ├── verdict.json
  └── run-report.md
  ```
- Standalone HTML control surfaces in `tools/<tool>/static/` must be named `<tool>_dashboard.html` (never generic `index.html`).

## 3. Telemetry Redaction & HAR Sanitization
- Before saving network traces or committing logs, scrub all authorization headers, session cookies, bearer tokens, API keys, and internal secrets.
- Pass all wire recordings through a sanitization pass to strip oversized binary payloads and tracking pixels.

## 4. Interactive Scrollytelling Walkthroughs & Playback
- **Dual-Pane Mental Model**: Complex multi-stage test runs, architectural walkthroughs, and operational playbooks should provide an interactive scrollytelling playback (narrative story on the left, sticky stateful canvas on the right).
- **Git-Friendly Markdown Comment Directives**: Never use proprietary or opaque JSON AST schemas for documentation. Author walkthroughs in 100% valid Markdown using HTML comment directives (`<!-- step: 1 id="..." subject="..." highlight="14-28" -->`).
- **Zero-Build Single-File HTML Output**: Walkthrough players must compile into self-contained, portable single-file HTML documents (`walkthrough.html`) using pure browser APIs (`IntersectionObserver`, CSS `position: sticky`, vector icons). Heavy NPM, Webpack, or React runtime dependencies are prohibited.
- **Reporting Contract**: When generated alongside test executions, `walkthrough.html` must be stored under `output/<deployment>/<tool>/<timestamp>/`, recorded in `verdict.json` under `"artifacts"`, and linked via an interactive tip callout in `run-report.md`.

## 5. Mandatory 5-Section Tool `README.md` Contract
- Every tool, runner, scraper, or control surface created under `tools/<tool>/` must include a dedicated, senior-engineer `README.md` covering:
  1. **Architectural Overview**: Core mission, backing contracts, and execution flow.
  2. **Deployment & Environment Resolution**: Supported `--deployment` / `-d` flags and config mapping.
  3. **Credential & Authentication Guide**: Automated `SessionManager` resolution, credentials file paths, and `--cookie` overrides.
  4. **How to Run**: Exhaustive, copy-pasteable CLI commands (standard run, staging verification, in-tandem `--dashboard` launch, and checkpoint resumption).
  5. **Output Artifacts**: Exact directory tree and schema description of generated files.

## 6. Dual Reporting Standard: Execution `verdict.json` + UltraRed `mainReport.md`
- **Suite & Runner Execution (`output/<deployment>/<tool>/<YYYY-MM-DD_HHMMSS>/`)**:
  - Emit `verdict.json` (schema v1.0.0 with `git_sha`, `target_version`, `status`, `checks`, `telemetry.redaction_applied`) and human-readable `run-report.md`.
  - When a dashboard or operator requests `run-report.md` and only `verdict.json` is present on disk, synthesize `run-report.md` on demand rather than returning 404.
- **Security & Repository Audits (`reports/<projectTitle>_<YYYYMMDD_HHMMSS>/`)**:
  - Emit the 3-file **UltraRed Reporting Bundle** (`mainReport.md`, `findings.json`, `summary.json`) containing:
    - **Executive Scorecard**: Inspected file count, verified safe invariants, immediate attention count, advisory count, explicit impact denominator (`X/Y target assets`), and posture status (`ALL_SAFE`, `ADVISORY`, `NEEDS_IMMEDIATE_ACTION`).
    - **1. What Was Run**: Active engines, scope, mode, profile, commit SHA, target version, duration, and host platform.
    - **2. What Was Safe**: Affirmatively verified policy invariants (`[PASS]`), falsified candidate hypotheses (`[DISPROVED]`), and clean surfaces (`[CLEAN]`) backed by concrete evidence.
    - **3. What Needs Immediate Attention**: Critical/High findings passing all 3 Hard Gates (*Reachable*, *Attacker-Controlled*, *New Capability*) and deduplicated by `(root_cause, component, prerequisite)`, with numbered reproduction steps, proof evidence, and remediation.
    - **4. Other Items That Need Attention (Not Severe)**: Medium/Low findings and defense-in-depth hardening notes.
    - **5. Pre-Submission Rubric Self-Verification**: Deterministic compliance check against the ARTEX 7-Check Oracle.
