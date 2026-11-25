---
name: autonomous-qa-harness
description: Closed-loop autonomous QA and end-to-end verification harness. Use when designing, running, or self-debugging automated test suites, browser automation (Playwright), API contracts, or infrastructure verification without unnecessary operator interruption.
---

# Autonomous QA & End-to-End Verification Harness

This skill equips the agent to perform closed-loop autonomous verification across web applications, REST APIs, and infrastructure.

---

## 1. Operating Protocol

```mermaid
flowchart TD
    A["Read Spec & Schemas"] --> B["Stage 0 Probe (Headless/Read-only)"]
    B --> C["Formulate Assertion Plan"]
    C --> D["Execute Suite / Script"]
    D --> E{"Pass?"}
    E -- "Yes" --> F["Emit verdict.json & run-report.md"]
    E -- "No" --> G["Inspect Screenshots, Console, Wire Logs in output/"]
    G --> H{"Self-Correctable?"}
    H -- "Yes" --> I["Adjust Code / Locators"]
    I --> D
    H -- "No (Credentials/Contradiction)" --> J["Escalate with Concrete Diagnostics"]
```

### Phase 1: Grounding & Stage 0 Probe
1. Inspect API definitions and specifications before drafting test code.
2. In browser testing, if a locator is ambiguous, inject a lightweight DOM dump script:
   ```javascript
   // Stage 0 Probe Script
   const elements = Array.from(document.querySelectorAll('button, input, select, [role="button"], .q-btn'))
     .map(el => ({
       tag: el.tagName,
       text: el.innerText?.trim()?.slice(0, 40),
       aria: el.getAttribute('aria-label'),
       id: el.id,
       classes: el.className
     }));
   console.log(JSON.stringify(elements, null, 2));
   ```
3. Capture empirical evidence rather than guessing.

### Phase 2: Asynchronous Convergence & Polling
When waiting for state changes, never use fixed sleeps without assertion loops:
```python
import time

def poll_for_state(fetch_fn, expected_state, timeout_sec=120, interval_sec=5):
    start = time.time()
    while time.time() - start < timeout_sec:
        current = fetch_fn()
        if current == expected_state:
            return True
        time.sleep(interval_sec)
    raise TimeoutError(f"Failed to reach {expected_state} within {timeout_sec}s. Last: {current}")
```

### Phase 3: Observability Output
Always emit a conforming `verdict.json` using the schema in `templates/verdict.schema.json`.
