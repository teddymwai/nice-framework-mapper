---
name: "codeaudit"
description: "VulnHunter 2-Phase White-Box Source Code Audit Skill with Entry-to-Sink Taint Tracing and 3 Hard Gates"
---

# VulnHunter Code Audit Skill

Distilled from `nealbridges/VulnHunter` and `teddymwai/ARTEX`.

## Phase 1: Input Inventory & Defense Catalog
1. Inventory all user-controllable input routes (HTTP endpoints, CLI flags, MCP tool arguments, environment variables, uploaded files).
2. Catalog shared project defenses (authentication decorators, CSRF validators, path `.resolve()` checks, SQL parameterization helpers).

## Phase 2: Forward Entry-to-Sink Taint Tracing
1. Trace user inputs through function calls, transformations, and object attributes down to dangerous sinks (`eval`, `exec`, `subprocess`, file writes, SQL queries, DOM `.innerHTML`).
2. Audit outbound call-sites to ensure scoping parameters (`tenant`, `user_id`, `run_id`, `session_id`) are never dropped or wildcarded.
3. Conduct transitive caller analysis across module boundaries.

## The 3 Hard Gates & Triage Standards
Every candidate finding must satisfy:
- **Reachable**: Call graph demonstrates live path from public route to sink.
- **Attacker-controlled**: Tainted data reaches sink arguments without safe sanitization.
- **New capability**: Exploitation yields unauthorized access, traversal, or code execution.

- Specify measured impact with an explicit **denominator** (e.g. `12/12 routes affected`, `1/1 endpoints vulnerable`).
- The auditor must have **actively tried to disprove** the flaw before finalizing the report. **Eliminations need evidence** showing which sanitizer or barrier neutralized the taint.
- **Zero confirmed findings is a valid outcome**.
- Verify `assert_local_loopback_scope` before executing any dynamic verification script.
