# Specification: {{FEATURE_OR_SUITE_CODE}} - {{TITLE}}

**Status:** Draft | Verified | In Production  
**Owner:** {{AUTHOR}}  
**Target Environments:** `staging` -> `prod`

---

## 1. Intent & Scope
Concise senior-engineer description of what this component or suite does, what invariants it asserts, and what business/technical failure mode it prevents.

---

## 2. Interface Contract (Needs, Uses, Produces)

- **Needs (Preconditions)**:
  - Valid authentication session for `{{ROLE}}`
  - Active network connectivity to `{{ENDPOINT}}`
  - Pre-existing entity: `{{ENTITY}}` (or auto-provisioned via Stage 1)
- **Uses (Resources & APIs)**:
  - `GET /api/v1/resource`
  - `POST /api/v1/resource/action`
- **Produces (Outputs & Artifacts)**:
  - `output/<deployment>/<tool>/<run_id>/verdict.json`
  - Created entity ID: `{{ENTITY_ID}}`
- **Decommission (Teardown Contract)**:
  - Affirmative deletion of created entity via `DELETE /api/v1/resource/{id}`
  - Affirmative verification probe (`GET` returns 404 or empty list)

---

## 3. Empirical Invariants & Edge Cases

| Invariant Code | Component / Event | Failure Risk | Enforced Remediation |
|---|---|---|---|
| `INV-{{CODE}}-01` | Async Job Execution | Asserting before worker picks up task | Explicit polling loop (60s @ 5s) |
| `INV-{{CODE}}-02` | Dropdown Select | DOM portal detachment | Await portal render before item selection |

---

## 4. Verification & Selftest Commands

```bash
# Execute suite against staging
python3 -m tools.runner --deployment staging --suite {{FEATURE_OR_SUITE_CODE}}

# Run offline unit validation
pytest tests/test_{{FEATURE_OR_SUITE_CODE}}.py -v
```
