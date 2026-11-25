<!-- walkthrough:title "Autonomous QA Harness & Execution Walkthrough" -->
<!-- walkthrough:domain "HARNESS" -->
<!-- walkthrough:test_code "QA-01" -->
<!-- walkthrough:deployment "staging" -->
<!-- walkthrough:layout "dual-pane" -->

# Autonomous QA Harness & Execution Walkthrough

This interactive walkthrough demonstrates how the autonomous test harness dynamically resolves environments, runs multi-actor browser interactions, and verifies steady-state convergence.

```python id="code-config" file="lib/config.py" title="Dynamic Configuration Resolver"
def load_config(deployment: str = "staging") -> dict:
    """Dynamically ingests deployment configurations without hardcoded URLs."""
    env_cfg = get_environment(deployment)
    return {
        "base_url": env_cfg["app_url"],
        "api_url": env_cfg["api_url"],
        "allow_mutation": env_cfg.get("allow_mutation", False),
    }
```

```python id="code-actor" file="lib/actors.py" title="Multi-Actor Session Pool"
class ActorPool:
    """Manages isolated browser contexts for multi-role workflows."""
    def __init__(self, browser_context):
        self.context = browser_context
        self.actors = {}

    def get_actor(self, role: str) -> "Actor":
        if role not in self.actors:
            self.actors[role] = Actor(role, self.context.new_page())
        return self.actors[role]
```

```json id="telemetry-verdict" title="Execution Verdict Contract"
{
  "schema_version": "1.0.0",
  "test_code": "QA-01",
  "deployment": "staging",
  "status": "PASS",
  "duration_ms": 1420.5,
  "artifacts": {
    "manifest": "index.json",
    "verdict": "verdict.json",
    "report": "run-report.md",
    "walkthrough": "walkthrough.html"
  }
}
```

<!-- step: 1 id="step-config" title="1. Dynamic Configuration Ingestion" subject="code-config" highlight="1-8" badge="CONFIG" status="PASS" latency_ms="14.2" -->

The test suite begins by dynamically resolving endpoints from environment variables or configuration files. Hardcoded base URLs and credentials are strictly prohibited.

> [!NOTE]
> All mutations against production default to blocked unless `--allow-mutation` is explicitly passed.

<!-- step: 2 id="step-actor" title="2. Multi-Actor Session Provisioning" subject="code-actor" highlight="7-12" badge="ACTOR" status="PASS" latency_ms="65.0" -->

The harness provisions clean, isolated browser profiles for each operational role (e.g. Administrator, Operator, Trainee):
- Storage state and cookies are strictly segregated.
- Browser tabs communicate via deterministic state assertions.

<!-- step: 3 id="step-verdict" title="3. Affirmative Verdict Serialization" subject="telemetry-verdict" highlight="5-12" badge="VERDICT" status="PASS" latency_ms="18.5" -->

Final affirmative verification confirms:
- All stages completed within SLA budgets.
- Telemetry payload serialized safely into `verdict.json`.
- Standalone `walkthrough.html` compiled alongside `run-report.md`.
