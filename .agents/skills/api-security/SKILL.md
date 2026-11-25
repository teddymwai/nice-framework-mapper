---
name: "api-security"
description: "7-Phase Offensive API Security Playbook Distilled from reverse-skill and ARTEX"
---

# API Security Playbook

Distilled from `zhaoxuya520/reverse-skill` and `teddymwai/ARTEX`.

## The 7-Phase Audit Lifecycle

1. **Phase 1: API Surface & Route Discovery**: Map all REST endpoints, GraphQL schemas, WebSocket paths, and hidden management routes.
2. **Phase 2: Authentication & Token Lifecycle**: Inspect JWT signing keys, expiration, OAuth scopes, and session invalidation.
3. **Phase 3: BOLA / IDOR Differential Testing**: Execute two-session/two-actor testing across object IDs to prove horizontal or vertical authorization bypass.
4. **Phase 4: GraphQL Introspection & Query Abuse**: Test field suggestions, circular queries, deep nesting, and batch query resource exhaustion.
5. **Phase 5: REST Parameter & Body Validation**: Test mass assignment, type juggling, unexpected fields, and boundary handling.
6. **Phase 6: Business Logic & State Differential**: Verify sequential state machine constraints (e.g. pay before download, step bypass).
7. **Phase 7: WebSocket & Streaming Protocol Audit**: Test handshake validation, message injection, cross-site WebSocket hijacking, and auth drop.

## Triage & Evidence Requirements
- In loopback testing, verify `assert_local_loopback_scope(host)` before sending any test payload.
- All access-control findings require two-actor differential proof.
- Findings must be proven **Reachable**, driven by **Attacker-controlled** data, and unlock a **New capability**.
- Always state the measured impact with an explicit **denominator** (`X/Y`).
- The tester must have **actively tried to disprove** bypasses by testing with invalidated or lower-tier tokens. **Eliminations need evidence**.
- **Zero confirmed findings is a valid outcome**.
