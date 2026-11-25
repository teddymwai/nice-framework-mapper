# Upcoming Features & Architectural Roadmap (`UPCOMING_FEATURES.md`)

> **Project:** NICE Framework Mapper  
> **Owner:** Ted Mwai  
> **Governance Rule:** Single canonical source of truth for all forward-looking features, deferred `HOLD` items, and planned test/tool expansions. Never scatter separate `RELEASE_NOTES_NEXT.md` files across the repository.

---

## 1. Control Plane & Interactive Dashboard Enhancements

| Feature ID | Target Component | Status (`PLANNED` / `IN_PROGRESS` / `HOLD`) | Architectural Scope & Success Criteria |
| :--- | :--- | :---: | :--- |
| `ROAD-UI-01` | `tools/<tool>/static/<tool>_dashboard.html` | `PLANNED` | Multi-run comparison drawer diffing historical `verdict.json` and UltraRed `summary.json` metrics side-by-side. |
| `ROAD-UI-02` | `tools/<tool>/server.py` | `PLANNED` | Operator observation export to Markdown/CSV and automated Notion tracker synchronization. |

---

## 2. Execution Engine, Concurrency & Convergence

| Feature ID | Target Component | Status (`PLANNED` / `IN_PROGRESS` / `HOLD`) | Architectural Scope & Success Criteria |
| :--- | :--- | :---: | :--- |
| `ROAD-ENG-01` | Orchestrator & Runners | `PLANNED` | Adaptive settle-window tuning based on real-time endpoint latency and hypervisor queue depth. |
| `ROAD-ENG-02` | Contract Ingestor | `PLANNED` | Automated synthesis of `.contract.toml` `[needs]`, `[uses]`, `[produces]`, and `[decommission]` stanzas from recorded HAR wire traces. |

---

## 3. Security Harness & Continuous Upstream Distillation (TedRedCraft)

| Feature ID | Target Component | Status (`PLANNED` / `IN_PROGRESS` / `HOLD`) | Architectural Scope & Success Criteria |
| :--- | :--- | :---: | :--- |
| `ROAD-SEC-01` | `.redcraft.toml` / Loop C | `PLANNED` | Domain-specific AST taint rules and held-out falsification fixtures (100% recall on vulnerable, 0% FP on benign). |
| `ROAD-SEC-02` | `reports/` UltraRed Engine | `PLANNED` | Historical trend delta tracking across consecutive `<projectTitle>_<YYYYMMDD_HHMMSS>/summary.json` audit runs. |

---

## 4. Developer Redesign & Input Ledger (`LEDGER-XX`)

Record environment blockers, missing credentials, or backend defects requiring external operator/developer action here rather than inventing speculative workarounds:

| Item Code | Affected Component | Category | Description & Blocker | Required Developer / Operator Input | Recommended Action / Redesign Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| *None active* | — | — | All current suites and tools operate within verified boundaries. | — | — |
