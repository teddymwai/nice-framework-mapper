# Changelog & Architectural Release Lineage (`CHANGELOG.md`)

All notable architectural enhancements, security invariants, interactive dashboard upgrades, and suite certifications for **NICE Framework Mapper** are documented in this file.

- **Release Nomenclature**: Strictly governed by the Ptarmigan (*Lagopus*) taxonomic specification ([`docs/releases/LAGOPUS_NOMENCLATURE_SPEC.md`](docs/releases/LAGOPUS_NOMENCLATURE_SPEC.md)).
- **Release Index**: Canonical tags, branches, and commit SHAs are synchronized in [`docs/RELEASE_REGISTER.md`](docs/RELEASE_REGISTER.md).
- **Promotion Workflow**: Staging-to-production validation gates are governed by [`docs/push2git.md`](docs/push2git.md).
- **Pagination Convention**: The active/latest release and open engineering watchouts remain expanded at the top of this document; historical releases are paginated inside collapsible `<details>` blocks below.

---

## [v1.3.0 — 2026-11-25] Lagopus Islandorum (Core Harness Alignment, DOM XSS Remediation & Test Suite)

| Field | Value |
| :--- | :--- |
| **Taxonomic Identifier** | `LagopusIslandorum_v1.3.0` |
| **Stage / Branch** | `Staging / Integration` (`main` -> PR / promotion) |
| **Primary Subsystems** | Antigravity Core Harness (`.agents/`, `templates/`, `tools/git_hooks/`), Browser TKS Mapper (`index.html`), CLI Mapper (`nice_mapper.py`), Unit Test Suite (`tests/test_nice_mapper.py`) |
| **Validation Status** | `python3 -m compileall -q .` passed; `python3 nice_mapper.py --selftest` passed (`tks_pool=2211, matches=3`); `python3 -m unittest discover -s tests -v` passed (5/5); TedRedCraft Tier 1 pre-commit SAST passed (`0 surface finding(s), 0 canonical root cause(s)`). |

### Architectural & Security Updates
- **Antigravity Core Template Alignment**: Bootstrapped `.agents/rules/`, `.agents/skills/`, `templates/`, `tools/git_hooks/` (`pre-commit`, `pre-push`), `.github/pull_request_template.md`, `.redcraft.toml`, `AGENTS.md`, `GEMINI.md`, `HARNESS.md`, `KICKOFF_PROMPT.md`, and `docs/` governance files (`RELEASE_REGISTER.md`, `UPCOMING_FEATURES.md`, `push2git.md`, `releases/`).
- **DOM XSS Remediation & Attribution/Tooltip Alignment (`SEC-JS-INNER-HTML`)**: Refactored `index.html` to eliminate all dynamic `innerHTML` assignments (`setUploadStatus`, `setRunStatus`, `renderFileRow`, `runMapping`, `renderResults`, and boot loader) in favor of explicit `document.createElement`, `textContent`, and `replaceChildren()` DOM construction, neutralizing unescaped `uploadedFileName` interpolation; added the canonical Edulis Secure Systems Hub Limited / TedCraft attribution footer with Apple HIG capsule links (`min-height: 44px`, `border-radius: 9999px`) and the WCAG 1.4.13 auto-hiding `TooltipManager`.
- **CLI Self-Test & Deterministic Unit Tests**: Added `--selftest` (`run_selftest`) to `nice_mapper.py` and created `tests/test_nice_mapper.py` covering TKS dictionary integrity (2,211 statements), hyphenated tokenization/stopword filtering, per-statement reuse cap enforcement, sample CSV/JSON loading and export, and CLI self-test execution.
- **Git Hygiene & Telemetry Exclusion**: Updated `.gitignore` to exclude `output/`, `reports/`, `.redcraft/`, `*.session_cache.json`, and `*.har`, and symlinked `tools/git_hooks/pre-commit` and `tools/git_hooks/pre-push` into `.git/hooks/`.

---

## [v1.2.0 — 2026-11-22] Lagopus Hyperborea (Full-SDLC, Interactive Dashboards & UltraRed Reporting)

| Field | Value |
| :--- | :--- |
| **Taxonomic Identifier** | `LagopusHyperborea_v1.2.0` |
| **Stage / Branch** | `Baseline Release` (`main`) |
| **Primary Subsystems** | Interactive Operator Dashboard Control Plane, In-Tandem Server Lifecycle (`--dashboard`), UltraRed Run Reporting Engine (`mainReport.md`), 5-Stage SDLC & 7-Check Pre-Commit Promotion Gate (`docs/push2git.md`) |
| **Validation Status** | `compileall -q` passed 100% cleanly; `tool_boilerplate.py --selftest`, `server_boilerplate.py --selftest`, and `ultrared_reporting.py --selftest` passed; TedRedCraft Tier 1 pre-commit SAST and Tier 2 pre-push Loopback DAST verified with 0 confirmed findings. |

### Architectural Updates
- Codified the **7-Capability Interactive Operator Dashboard Mandate** (`.agents/rules/08-interactive-dashboard-architecture.md` and `.agents/skills/interactive-dashboard-architect/SKILL.md`), eliminating passive status dashboards in favor of full control planes with run creation, DAG plan previews, live incremental event monitoring, multi-session `409 Conflict` one-click reset, state hydration across browser refreshes, in-app report rendering with on-demand markdown synthesis, Studio Curve (`img001.jpg`) composite canvas, `TooltipManager`, and `file://` offline preview mode.
- Upgraded `templates/server_boilerplate.py` and authored `templates/dashboard_boilerplate.html` as a complete reference control plane with `ensure_dashboard_running()` in-tandem daemon startup, `.resolve().is_relative_to()` path confinement (`SEC-01`), CSRF & loopback Origin checks (`SEC-02`), 1MB body ceiling (`SEC-04`), and DOM escaping (`SEC-JS-INNER-HTML`).
- Added `templates/ultrared_reporting.py` implementing the zero-dependency **UltraRed Run Reporting Engine** (`<projectTitle>_<YYYYMMDD_HHMMSS>/mainReport.md`, `findings.json`, `summary.json`) with Executive Scorecard, *What Was Run*, *What Was Safe* (evidence-backed eliminations), *What Needs Immediate Attention* (3 Hard Gates + 3-Tuple deduplication), *Other Items*, and *ARTEX 7-Check Pre-Submission Self-Verification*.
- Codified the **Full-SDLC & 3-Tier Git Promotion Lifecycle** (`.agents/rules/09-full-sdlc-git-and-release-lifecycle.md`, `.agents/skills/sdlc-git-release-lifecycle/SKILL.md`, and `docs/push2git.md`) covering `ADOPT`/`REJECT`/`HOLD` planning triage, Anti-Seam-Rot contracts, the 7-Check "Forgotten Bits" pre-commit gate, `Why`/`Trade-off`/`Touches` commit protocol, `beta/unstable-nightly` $\rightarrow$ `staging` $\rightarrow$ `--ff-only` `main` promotion, Commit-and-Purge legacy archiving, and `GH013` protected tag deletion.

---

## Historical Releases (Paginated Archive)

<details>
<summary><strong>[v1.1.0 — 2026-11-21] Lagopus Helvetica (TedRedCraft Security Harness & Port/Session Control Plane)</strong></summary>

### Architectural Updates
- Integrated TedRedCraft (`https://github.com/teddymwai/TedRedCraft`) 3-tier polyglot SAST/DAST, 4 disciplined rules, VulnHunter 3 Hard Gates, Sudus 5-Lens Adversary Review, and loopback scope lock (`assert_local_loopback_scope`).
- Established dedicated port allocation register (`8770`, `8780`, `8790`), `SO_REUSEADDR` socket reuse, `EADDRINUSE` auto-recovery, thread-safe session state machines, and `PROD-MUTATE` production mutation safety interlock.

</details>

<details>
<summary><strong>[v1.0.0 — 2026-11-18] Lagopus (Initial Autonomous Engineering Template)</strong></summary>

### Architectural Updates
- Initial codification of the Closed-Loop Verification Protocol ("No Eye-Tour"), Stage 0 DOM probing, Living Invariant Matrix, UI Unslop & Apple HIG component standards, Dynamic Tooling & Output Hierarchy, Interactive Scrollytelling Walkthrough engine, and Ptarmigan (*Lagopus*) taxonomic release governance.

</details>
