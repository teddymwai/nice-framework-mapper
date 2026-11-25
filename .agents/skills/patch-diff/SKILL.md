---
name: "patch-diff"
description: "N-Day Vulnerability Patch Diffing and Exploit Vector Reconstruction Playbook"
---

# Patch Diff Exploit Analysis Skill

Distilled from `zhaoxuya520/reverse-skill` and `teddymwai/ARTEX`.

## Methodology

1. **Step 1: Commit & Patch Isolation**:
   - Compare the vulnerable version with the patched version (`git diff v1.0.0..v1.0.1` or commit hash).
   - Filter for security-relevant file modifications (route handlers, auth checks, path joins, serializers, parsers).
2. **Step 2: Guard & Precondition Inference**:
   - Analyze added conditionals (`if`, `require`, boundary checks, sanitizers).
   - Invert the added guard to determine the exact precondition that the vulnerability exploited.
3. **Step 3: Root-Cause Classification**:
   - Map the flaw to CWE classes (e.g., CWE-22 Path Traversal, CWE-352 CSRF, CWE-89 SQLi, CWE-79 XSS, CWE-434 File Upload).
4. **Step 4: PoC Construction & Verification**:
   - Construct a minimal reproducible proof-of-concept against local unpatched test fixtures.
   - Verify that `assert_local_loopback_scope` is enforced on all test connections.
5. **Step 5: Codebase Sweep & Regression Detection**:
   - Search the entire repository for similar unpatched patterns using AST and regex queries.

## Invariants
- Verify that the flaw is **Reachable** in production, driven by **Attacker-controlled** data, and grants a **New capability**.
- Calculate measured impact across the codebase with an explicit **denominator** (`X/Y affected endpoints`).
- The researcher must have **actively tried to disprove** reachability in other call sites. **Eliminations need evidence**.
- **Zero confirmed findings is a valid outcome**.
