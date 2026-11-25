---
name: repo-health-audit
description: Systematically audit codebase health across 7 architectural tiers: bytecode compilation, 1:1 registry/manifest/spec-on-disk parity, contract canonicalization, dynamic tool & interactive dashboard standards, tiered documentation & single roadmap sync, external Notion tracker parity, and the Developer Redesign & Input Ledger. Use before committing changes or promoting branches.
---

# Repository Health & Continuous 7-Tier Parity Audit

Distilled from `CYBER RANGES Agents/.agents/skills/repo-health-audit/SKILL.md` and `TedRedCraft`.

---

## 1. When to Activate
- Prior to promoting features across `beta/unstable-nightly` (or `beta-<Feature>`), `staging`, and `main`.
- When adding, modifying, or retiring test suites, contracts, or operational tools under `tools/`.
- When reorganizing documentation, updating release notes, or synchronizing with external Notion trackers.
- Whenever an agent completes a complex task and needs to certify repository consistency.

---

## 2. The 7-Tier Audit Workflow

### Phase 1: Full-Tree Compilation & Bytecode Sweep
Verify that zero syntax errors, invalid f-strings, or broken `typing` imports exist across all Python modules:
```bash
python3 -m compileall -q lib/ tools/ tests/ templates/ 2>/dev/null || python3 -m compileall -q .
```
*Remediation*: Fix any compilation failure immediately. Legacy or reference-only code must be remediated, quarantined in `tools/legacy/archive/`, or archived via the Commit-and-Purge pattern.

### Phase 2: Registry $\leftrightarrow$ Manifest $\leftrightarrow$ Physical Spec-on-Disk Parity Gate
Verify 1:1 bidirectional alignment between code registries, governance manifests, and physical specification files:
1. Run registry listing (`--list-suites`) and offline harness self-tests (`--selftest`).
2. Enforce invariants:
   - Every suite in the code registry must have an affirmative entry in `manifest.toml`.
   - Every `default_spec` path declared in the registry or manifest must physically exist as a non-empty markdown file on disk under `specs/`.
   - Internal modules under `lib/framework/` and `lib/suites/` must never import from root-level legacy shims (enforced via AST import-boundary lint).
   - Manifest governance rules must be satisfied (`idempotent = false` requires `max_retries = 0`).

### Phase 3: Contract Canonicalization & Lifecycle Hook Validation
Verify that declarative contracts adhere to canonical naming and lifecycle schemas:
- **Canonical Naming**: Files must follow `<suite_code_lower>.contract.toml` (e.g., `mp_01.contract.toml`, `re_01.contract.toml`). Purge non-canonical squashed duplicates (`mp01.contract.toml`).
- **Lifecycle Guarantees**: Mutating contracts must declare `[needs]`, `[uses]`, `[produces]`, and affirmative `[decommission]` teardown hooks.

### Phase 4: Dynamic Tool Architecture & Interactive Dashboard Audit
Ensure all utilities under `tools/<tool>/` satisfy the Dynamic Tool & Interactive Dashboard Mandates:
- **Dynamic Endpoints & Auth**: No hardcoded URLs or session cookies (`<YOUR_PROD_SESSION_COOKIE>`); resolve endpoints via `--deployment` / `-d` and `SessionManager`.
- **Output Hierarchy**: Write exclusively to `output/<deployment>/<tool>/<YYYY-MM-DD_HHMMSS>/` (or `reports/<projectTitle>_<YYYYMMDD_HHMMSS>/` for UltraRed audits).
- **Mandatory 5-Section `README.md`**: Every tool folder under `tools/` must contain a senior-engineer `README.md` (Architectural Overview, Deployment Resolution, Credential Guide, How to Run, Output Artifacts).
- **Interactive Dashboard Standards**: Primary HTML files in `tools/<tool>/static/` must be named `<tool>_dashboard.html` (never naked `index.html`), alias `/` and `/index.html`, support in-tandem `--dashboard` startup (`ensure_<tool>_running`), handle `409 Conflict` with one-click reset, hydrate state on refresh, synthesize missing `run-report.md` from `verdict.json` on demand, and pass TedRedCraft Tier 1 SAST (`SEC-01`..`SEC-04`, `SEC-JS-INNER-HTML`).

### Phase 5: Tiered Documentation, Single Roadmap & Release Register Sync
Audit repository documentation to eliminate fragmentation:
- **Single Canonical Roadmap**: Consolidate all upcoming work into `docs/UPCOMING_FEATURES.md` grouped by domain. Merge and delete ad-hoc `RELEASE_NOTES_NEXT.md` files.
- **Historical Release Notes**: Move superseded release notes into `docs/releases/archive/` and paginate older `CHANGELOG.md` entries inside `<details>` blocks.
- **Release Lineage**: Verify exact commit SHA, date, and Ptarmigan (*Lagopus*) taxonomic tag parity across `CHANGELOG.md`, `docs/RELEASE_REGISTER.md`, and `docs/releases/RELEASE_NOTES_*.md`.
- **Promotion Runbook**: Cross-check `docs/push2git.md` and `.github/pull_request_template.md` against active CI and TedRedCraft security gates.

### Phase 6: External Tracker / Notion Cockpit Parity Gate
Keep volatile tracking out of Git:
- Ephemeral sprint scratchpads, daily run logs, and manual card trackers belong in Notion (referenced via `docs/trackers/README.md`).
- Durable specs, contracts, and architectural invariants remain in Git.

### Phase 7: Developer Redesign & Input Ledger (`LEDGER-XX`)
When the audit discovers missing environment credentials, isolated network VLANs/VPNs, or backend defects requiring architectural redesign, compile a structured escalation ledger rather than inventing speculative mocks or hardcoding bypasses:

| Item Code | Affected Component | Category | Description & Blocker | Required Developer / Operator Input | Recommended Action / Redesign Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LEDGER-XX` | `<path>` | `Infrastructure` / `Credentials` / `UI` / `Schema` | `<detailed description>` | `<exact input required>` | `<suggested path>` |
