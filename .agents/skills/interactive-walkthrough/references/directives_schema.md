# Scrollytelling Walkthrough Directives Schema

This reference defines the syntax and attributes supported by the `walkthrough_engine` parser. All directives use standard HTML comment notation so they remain completely unobtrusive in standard Markdown renderers (GitHub, VS Code, terminal).

---

## 1. Document-Level Directives

Document directives configure overall walkthrough metadata. They can appear anywhere before the first step, typically placed near the top of the file:

```markdown
<!-- walkthrough:title "System Deployment & Verification Walkthrough" -->
<!-- walkthrough:domain "INFRA" -->
<!-- walkthrough:test_code "INFRA-01" -->
<!-- walkthrough:deployment "staging" -->
<!-- walkthrough:layout "dual-pane" -->
```

| Directive | Attribute / Value | Description |
| :--- | :--- | :--- |
| `walkthrough:title` | string | Display title in top header. Falls back to first `# Header`. |
| `walkthrough:domain` | string | Domain or subsystem category. |
| `walkthrough:test_code` | string | Canonical test code identifier (e.g. `TEST-01`, `API-04`). |
| `walkthrough:deployment`| string | Target deployment environment (`local`, `staging`, `production`). |
| `walkthrough:layout` | `dual-pane` (default), `stacked` | Presentation layout mode. |

---

## 2. Step Directives

A step directive defines a distinct narrative milestone along the Story rail:

```markdown
<!-- step: 1 id="config-ingest" title="Configuration Ingestion" subject="code-config" highlight="14-28" badge="CONFIG" status="PASS" latency_ms="42.5" -->
```

### Supported Attributes

| Attribute | Format | Default | Description |
| :--- | :--- | :--- | :--- |
| `step: <N>` | Integer (1, 2, 3...) | Mandatory | Step index in the sequence. |
| `id` | String (`slug`) | `step-<N>` | Unique identifier for deep linking and DOM anchoring. |
| `title` | String | `Step <N>` | Narrative title displayed on the step card. |
| `subject` | String (`#id` or `id` or `file:...`) | `default` | ID of the target subject canvas to display on this step. |
| `highlight` | String (`14-22, 28, 35-40`) | `""` | Comma-separated line numbers and ranges to illuminate with green focal bars. Non-highlighted lines dim subtly. |
| `badge` | String | Doc domain | Domain badge or tag label to render in step header. |
| `status` | `PASS`, `FAIL`, `BLOCKED`, `INFO` | `PASS` | Semantic execution status pill. |
| `latency_ms` | Float | `None` | Optional execution duration pill in milliseconds. |

---

## 3. Subject Declarations

Subjects are declared either as fenced code blocks with attribute strings, or referenced as external files.

### Fenced Code Blocks with Metadata

```python id="code-config" file="lib/config.py" title="Configuration Broker"
def load_config(deployment: str = "staging") -> dict:
    # Lines 14 to 28
    return resolve_env(deployment)
```

Attributes on the code fence:
* `id="..."`: Unique subject identifier matched by `subject="..."` on step directives.
* `file="..."`: File path relative to project root. If block contents are empty or placeholder, the parser will automatically load contents from this file!
* `title="..."`: Friendly label displayed in the sticky subject tab header.
* `type="..."`: `code` (default), `terminal`, `json`, or `table`.

### External File References Directly on Steps
If a subject was not pre-declared in a code block, you can reference it directly on the step:

```markdown
<!-- step: 2 subject="file:lib/auth.py" highlight="20-35" title="Session Authentication" -->
```
The parser will automatically ingest `lib/auth.py`, generate a subject with line numbers, and focus on lines 20–35.
