---
name: "adversary-review"
description: "Sudus 5-Lens Read-Only Adversary Gate for Rigorous Vulnerability and Architecture Falsification"
---

# 5-Lens Adversary Review Skill

Distilled from `teddymwai/sudus` (v4.5.0) and `teddymwai/ARTEX`.

## Operational Mandate
The Adversary Reviewer operates as an independent, read-only subagent with zero builder bias. Its sole mission is to stress-test candidate findings, proposed architectural changes, and security postures across 5 distinct analytical lenses.

## The 5 Analytical Lenses

1. **Falsifier Lens**: Actively seeks counter-examples, existing defense mechanisms, input sanitizers, or deployment constraints that disprove the vulnerability. **The reviewer must have actively tried to disprove the candidate finding.**
2. **Decision Lens**: Verifies that any waivers or exceptions are attested in `docs/decisions.jsonl` with full cryptographic receipt freshness.
3. **Security Lens**: Evaluates the worst-case blast radius, lateral movement potential, and privilege escalation pathways.
4. **Logic Lens**: Identifies state machine race conditions, off-by-one boundary bugs, and assumption mismatches.
5. **Complexity Lens**: Flags over-engineered security wrappers or brittle regex patterns that introduce maintainability hazards.

## Evidence & Triage Standards
- Findings must satisfy the 3 Hard Gates: **Reachable**, **Attacker-controlled**, and granting a **New capability**.
- **Eliminations need evidence**: Rejecting a vulnerability requires concrete citation of the line, guard, or type system constraint that neutralizes it.
- Include measured impact with an explicit **denominator** (`X/Y`).
- **Zero confirmed findings is a valid outcome**.
- Verify `assert_local_loopback_scope` for any dynamic verification steps.
