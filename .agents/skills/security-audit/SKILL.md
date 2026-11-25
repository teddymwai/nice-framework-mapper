---
name: "security-audit"
description: "Unified 3-Tier Multi-Stack Security Audit Skill embedding SAST, Loopback DAST, Pentest, and the 4 Disciplined Rules"
---

# Security Audit Skill

This skill executes the comprehensive 3-Tier security verification harness across Python, Go, JavaScript/TypeScript, Shell, and Docker stacks.

## Prime Invariants & Disciplined Rules

1. **Rule 1 (Explicit Scope-Lock Pre-Flight)**: Active DAST and pentest operations must strictly call `assert_local_loopback_scope(host)`. Target hostnames are resolved through DNS to verify `ipaddress.is_loopback`. Remote production and staging endpoints are never scanned.
2. **Rule 2 (Evidence-First Anti-Hallucination Rubric)**: Classify all observations as `CONFIRMED`, `CANDIDATE`, `DISPROVED`, or `HARDENING_NOTE`.
   - To be `CONFIRMED`, an issue must pass VulnHunter's 3 Hard Gates:
     - **Reachable**: Verified execution path in production code.
     - **Attacker-controlled**: Entry parameter originates from untrusted user input.
     - **New capability**: Grants unauthorized access, bypass, execution, or data leak.
   - Every confirmed finding must specify measured impact with an explicit **denominator** (`X/Y`).
   - The auditor must have **actively tried to disprove** the vulnerability. **Eliminations need evidence** at the same standard as confirmations. **Zero confirmed findings is a valid outcome**.
3. **Rule 3 (Root-Cause 3-Tuple Deduplication)**: Group surface findings sharing `(root_cause, component, prerequisite)` into a single canonical finding.
4. **Rule 4 (Bounded Lease Closeout)**: Loopback HTTP servers run in ephemeral leases that tear down sockets and clean temporary directories in `finally` blocks.

## Execution Tiers

- **Tier 1: Pre-Commit (<1.5s)**: Staged diff secrets, HAR files, dangerous execution sinks, unconfined path joins, and missing CSRF headers.
- **Tier 2: Pre-Push & CI (<4s)**: Full AST SAST + Ephemeral Loopback DAST on `127.0.0.1:0` + Adversarial traversal and SSRF payloads.
- **Tier 3: Deep Audit**: 2-phase taint analysis, Cairn `Execute -> Conclude` interrupt recovery, SQLite Dual-Graph persistence, and 5-lens adversary review.
