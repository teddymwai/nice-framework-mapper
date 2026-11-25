---
name: autonomous-execution
description: Core autonomous execution rules, closed-loop verification, Stage 0 probing, and anti-hallucination protocols.
trigger: always_on
---

# Autonomous Execution & Anti-Hallucination Protocol

Every AI agent operating in this project must adhere strictly to these execution rules:

## 1. Closed-Loop Autonomous Execution ("No Eye-Tour")
- **Ground in Schemas First**: Before writing or modifying code, inspect authoritative schemas, spec files, OpenAPI endpoints, and type definitions. Never guess DTO keys, route paths, or DOM selectors.
- **Stage 0 Probe**: When implementing or debugging a UI view or external API, execute a non-destructive read-only probe first. Capture actual visible element attributes (`aria-label`, IDs, role names) or raw response bodies before writing asserts.
- **Self-Correct Before Escalating**: If an operation fails, inspect the generated screenshots, console logs, and wire captures in `output/`, adjust the implementation, and re-run. Only pause to ask the user when blocked by missing credentials, revoked permissions, or contradictory requirements.

## 2. Living Invariant Register
- Consult the Invariant Matrix in `AGENTS.md` and `HARNESS.md` before coding.
- When an empirical quirk, API oddity, or platform edge case is discovered, immediately record it in the Invariant Register so future agent turns never repeat the mistake.

## 3. Affirmative Teardown & Idempotency
- Any test or script that creates state must clean up its resources affirmatively.
- Never rely on fire-and-forget deletion. Verify deletion with a follow-up query confirming absence.
