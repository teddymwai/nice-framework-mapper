---
name: interactive-walkthrough
description: Author, compile, audit, and preview interactive scrollytelling walkthroughs and test execution playback dashboards. Use when creating or restyling step-by-step code walkthroughs, scenario playbooks, orchestrator execution debriefs, or converting test manifests into dual-pane scrollytelling HTML players adhering to the UI Mantra.
---

# Interactive Scrollytelling Walkthrough Skill Suite

Author and compile interactive, dual-pane **scrollytelling walkthroughs** and test run playback dashboards.

This skill operationalizes the core mental model of synchronized technical documentation:
- **The Story (Left Rail)**: A linear prose feed written in standard GitHub-Flavored Markdown with unobtrusive HTML comment directives (`<!-- step: 1 ... -->`).
- **The Subject (Sticky Right Canvas)**: A stateful, sticky viewport that synchronizes code files, configuration templates, wire payloads, terminal telemetry, and glowing line highlights.

---

## When to Use

1. **Documenting Multi-Stage Architecture & Code Flows**: Explaining complex test harness suites, session auth brokers, cloud-init scripts, or API contract lifecycles.
2. **Generating Interactive Run Playbacks**: Converting test run artifacts (`output/<deployment>/<tool>/<timestamp>/index.json`) into interactive `walkthrough.html` players alongside standard `run-report.md`.
3. **Operational Playbooks & Exercise Guides**: Creating interactive scenario debriefs for operators, developers, and trainees.
4. **Auditing Walkthrough Integrity**: Verifying that line highlight ranges (`highlight="14-28"`), subject IDs, and external file references (`file:...`) exist and match current repository code.

---

## Core Invariants

1. **Zero-Build, Pure-Python Engine**: No Node.js or React runtime overhead; produces self-contained, single-file HTML players adhering strictly to the **UI Mantra**:
   - Quiet Chrome: Understated obsidian surfaces and borders.
   - Vector Iconography: Standard Google Fonts Material Symbols exclusively; zero emojis.
   - Apple HIG Component Foundation: Capsule buttons (`border-radius: 9999px`), 44x44px minimum hit targets, tactile `:active` `scale(0.97)` feedback.
2. **Markdown-First Git Friendliness**: Author walkthroughs in 100% valid Markdown with HTML comment directives. Documents remain cleanly diffable and readable on GitHub and terminal pagers.
3. **Responsive Dual-Pane Grid**: Native `IntersectionObserver` synchronizes scroll position with sticky code pane centering and focal line highlights. Gracefully collapses to stacked layout on screens `< 1024px`.

---

## Step-by-Step Authoring Workflow

### 1. Document Configuration
Declare walkthrough metadata at the top of your markdown document:
```markdown
<!-- walkthrough:title "System Deployment Walkthrough" -->
<!-- walkthrough:domain "INFRA" -->
<!-- walkthrough:test_code "INFRA-01" -->
<!-- walkthrough:deployment "staging" -->
<!-- walkthrough:layout "dual-pane" -->
```

### 2. Declare Code Subjects
Define fenced code blocks with `id="..."`, `title="..."`, and optional `file="..."`:
````markdown
```python id="code-auth" file="lib/auth.py" title="Authentication Broker"
def resolve_session(deployment: str) -> requests.Session:
    # Code content here, or empty to automatically read from file="..."
```
````

### 3. Add Step Directives & Line Highlights
Segment narrative prose into sequential steps with line-level focus:
```markdown
<!-- step: 1 id="step-auth" title="1. Dynamic Session Resolution" subject="code-auth" highlight="14-22" badge="AUTH" status="PASS" latency_ms="48.1" -->

The test suite begins by authenticating an affirmative operator session.
Sensitive tokens are automatically scrubbed from memory cache.
```

### 4. Compile Standalone Walkthrough Player
Compile your markdown document to an interactive HTML player:
```bash
python3 templates/walkthrough_engine.py \
  --file .agents/skills/interactive-walkthrough/examples/sample_walkthrough.md \
  --output output/staging/walkthrough/walkthrough.html
```

---

## Reporting Pipeline Integration

In automated test suites, wire walkthrough generation into report generation:
```python
# 1. Synthesize walkthrough directly from test run telemetry:
doc = synthesize_walkthrough_from_manifest(manifest_path_or_dict)
html_str = render_walkthrough_html(doc)

# 2. Save alongside test reports:
out_file = output_dir / "walkthrough.html"
out_file.write_text(html_str, encoding="utf-8")

# 3. Register in verdict.json artifacts:
verdict["artifacts"]["walkthrough"] = "walkthrough.html"
```
