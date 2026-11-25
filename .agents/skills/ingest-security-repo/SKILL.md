---
name: "ingest-security-repo"
description: "Continuous Upstream Repository Ingestion, Net-Gain vs Tech-Load Review, and Attested Promotion SOP"
---

# Ingest Security Repository Skill

Governs the continuous learning pipeline in `TedRedCraft`, allowing the harness to borrow and distill architectural patterns, rules, and skills from external repositories.

## Workflow

1. **Stage 1: Repository Ingestion**:
   - Run `python3 -m redcraft upstream ingest <owner/repo-or-path>`.
   - Inspects commit logs, security disclosures, skills, and test vectors.
2. **Stage 2: Net-Gain vs. Tech-Load Dossier Generation**:
   - Generates `docs/upstreams/<slug>_review.md`.
   - Documents the Executive Verdict (reject wholesale dependencies vs. native stdlib distillation).
   - Before-vs-After Capability Matrix and Day-2 maintenance overhead.
   - Distilled candidate rules are staged with `status = "observed"`.
3. **Stage 3: Falsification Battery & Seed Gate Verification**:
   - The candidate rule must run against `tests/fixtures/` and achieve 100% catch on vulnerable fixtures and 0% on benign fixtures.
   - Run `python3 -m redcraft selftest` to verify no skill dropped required seed markers.
4. **Stage 4: Attested Promotion**:
   - Promote via `python3 -m redcraft upstream promote <slug> --quote "<operator ruling>"`.
   - Flips status to `status = "agreed <YYYY-MM-DD>"` and commits an attested SHA-256 record to `docs/decisions.jsonl`.

## Invariants
- Candidate rules must prove that targets are **Reachable**, inputs are **Attacker-controlled**, and findings grant a **New capability**.
- Measured impact must carry an explicit **denominator**.
- Evaluator must have **actively tried to disprove** the utility of the external tool before distillation. **Eliminations need evidence**.
- **Zero confirmed findings is a valid outcome**.
- Active dynamic testing of ingested tools must enforce `assert_local_loopback_scope`.
