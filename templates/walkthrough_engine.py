#!/usr/bin/env python3
"""
Scrollytelling Walkthrough Engine & HTML Generator
─────────────────────────────────────────────────
Generic, zero-dependency Python template for dual-pane interactive documentation.
Parses native Markdown directives (HTML comments), synthesizes test manifests,
and compiles standalone single-file HTML players adhering to Quiet Chrome & Apple HIG:
  - Quiet obsidian/slate base palette.
  - Apple HIG Component Foundation (capsule buttons, 44px hit targets, tactile feedback).
  - Zero emojis (Google Fonts Material Symbols exclusively).
  - Native browser IntersectionObserver scrollytelling engine.
"""

import os
import sys
import re
import json
import html
import logging
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any, List, Optional, Union

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("walkthrough_engine")


# ── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class WalkthroughSubject:
    """Represents a stateful target displayed in the sticky canvas (code, terminal, json)."""
    id: str
    type: str = "code"  # "code", "terminal", "json", "image", "table"
    title: str = ""
    language: str = "python"
    content: str = ""
    file_path: Optional[str] = None
    versions: Dict[str, str] = field(default_factory=dict)


@dataclass
class WalkthroughStep:
    """Represents an individual narrative step along the left Story rail."""
    step_number: int
    step_id: str
    title: str
    content_html: str
    raw_markdown: str = ""
    target_subject_id: str = "default"
    highlight_lines: List[int] = field(default_factory=list)
    badge: Optional[str] = None
    latency_ms: Optional[float] = None
    status: Optional[str] = None  # PASS, FAIL, INFO, BLOCKED


@dataclass
class WalkthroughDocument:
    """Compiled representation of a complete scrollytelling walkthrough."""
    title: str
    domain: str = "SYSTEM"
    test_code: Optional[str] = None
    deployment: str = "staging"
    duration_ms: Optional[float] = None
    verdict_status: str = "PASS"
    steps: List[WalkthroughStep] = field(default_factory=list)
    subjects: Dict[str, WalkthroughSubject] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── Directive Parser ─────────────────────────────────────────────────────────

ATTR_REGEX = re.compile(r'([a-zA-Z0-9_\-]+)=(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))')
DOC_DIRECTIVE_REGEX = re.compile(r'<!--\s*walkthrough:([a-zA-Z0-9_\-]+)\s*(.*?)\s*-->', re.IGNORECASE)
STEP_DIRECTIVE_REGEX = re.compile(r'<!--\s*step:\s*(\d+)\s*(.*?)\s*-->', re.IGNORECASE)
FENCED_CODE_REGEX = re.compile(
    r'^```([a-zA-Z0-9_\-]+)?(?:\s+(.*?))?\n(.*?)\n```$',
    re.MULTILINE | re.DOTALL
)


def _parse_directive_attributes(attr_str: str) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    if not attr_str:
        return attrs
    for match in ATTR_REGEX.finditer(attr_str):
        k = match.group(1).lower()
        v = match.group(2) if match.group(2) is not None else (
            match.group(3) if match.group(3) is not None else match.group(4)
        )
        attrs[k] = v or ""
    return attrs


def _parse_highlight_ranges(range_str: str) -> List[int]:
    if not range_str:
        return []
    lines: List[int] = []
    chunks = range_str.replace(" ", "").split(",")
    for chunk in chunks:
        if not chunk:
            continue
        if "-" in chunk:
            parts = chunk.split("-", 1)
            try:
                start = int(parts[0])
                end = int(parts[1])
                lines.extend(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                lines.append(int(chunk))
            except ValueError:
                continue
    return sorted(list(set(lines)))


def _markdown_to_clean_html(md_text: str) -> str:
    lines = md_text.strip().split("\n")
    out_html: List[str] = []
    in_list = False
    in_alert: Optional[str] = None
    alert_lines: List[str] = []

    def flush_alert():
        nonlocal in_alert, alert_lines
        if in_alert:
            alert_class = in_alert.lower()
            inner = "<br>".join(alert_lines)
            out_html.append(
                f'<div class="callout callout-{alert_class}">'
                f'<span class="material-symbols-outlined callout-icon">'
                f'{"info" if alert_class in ("note", "info") else ("lightbulb" if alert_class == "tip" else "warning")}</span>'
                f'<div class="callout-body">{inner}</div></div>'
            )
            in_alert = None
            alert_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()
        alert_match = re.match(r'^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\](.*)$', line, re.IGNORECASE)
        if alert_match:
            flush_alert()
            in_alert = alert_match.group(1).upper()
            extra = alert_match.group(2).strip()
            if extra:
                alert_lines.append(html.escape(extra))
            continue

        if in_alert:
            if line.startswith(">"):
                alert_lines.append(html.escape(line.lstrip("> ").strip()))
                continue
            else:
                flush_alert()

        if line.startswith("- ") or line.startswith("* "):
            if not in_list:
                out_html.append('<ul class="walkthrough-list">')
                in_list = True
            safe_text = _format_inline_markdown(line[2:].strip())
            out_html.append(f"<li>{safe_text}</li>")
            continue
        else:
            if in_list:
                out_html.append("</ul>")
                in_list = False

        if not line:
            continue

        if line.startswith("### "):
            out_html.append(f'<h4 class="step-subheading">{_format_inline_markdown(line[4:].strip())}</h4>')
        elif line.startswith("## "):
            out_html.append(f'<h3 class="step-subheading">{_format_inline_markdown(line[3:].strip())}</h3>')
        elif line.startswith("# "):
            out_html.append(f'<h2 class="step-subheading">{_format_inline_markdown(line[2:].strip())}</h2>')
        else:
            out_html.append(f'<p class="step-text">{_format_inline_markdown(line)}</p>')

    flush_alert()
    if in_list:
        out_html.append("</ul>")
    return "\n".join(out_html)


def _format_inline_markdown(text: str) -> str:
    safe = html.escape(text)
    safe = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', safe)
    safe = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', safe)
    safe = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', safe)
    safe = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" class="walkthrough-link" target="_blank" rel="noopener">\1</a>', safe)
    return safe


def parse_walkthrough_markdown(md_text: str, project_root: Optional[Path] = None) -> WalkthroughDocument:
    root = project_root or Path.cwd()

    title = "System Walkthrough"
    domain = "SYSTEM"
    test_code: Optional[str] = None
    deployment = "staging"
    duration_ms: Optional[float] = None
    verdict_status = "PASS"
    metadata: Dict[str, Any] = {}
    subjects: Dict[str, WalkthroughSubject] = {}
    steps: List[WalkthroughStep] = []

    for match in DOC_DIRECTIVE_REGEX.finditer(md_text):
        dtype = match.group(1).lower()
        dval = match.group(2).strip()
        dval_clean = dval.strip('"\'')
        attrs = _parse_directive_attributes(dval)

        if dtype == "title":
            title = attrs.get("title") or dval_clean
        elif dtype == "domain":
            domain = attrs.get("domain") or dval_clean
        elif dtype == "test_code":
            test_code = attrs.get("test_code") or dval_clean
        elif dtype == "deployment":
            deployment = attrs.get("deployment") or dval_clean
        elif dtype == "meta":
            metadata.update(attrs)

    for match in FENCED_CODE_REGEX.finditer(md_text):
        lang = (match.group(1) or "text").lower()
        attr_str = match.group(2) or ""
        code_content = match.group(3)
        attrs = _parse_directive_attributes(attr_str)
        block_id = attrs.get("id")
        if block_id:
            file_ref = attrs.get("file")
            resolved_content = code_content
            if file_ref and (not code_content.strip() or code_content.strip().startswith("# load:")):
                target_file = root / file_ref.lstrip("/")
                if target_file.exists() and target_file.is_file():
                    try:
                        resolved_content = target_file.read_text(encoding="utf-8")
                    except Exception:
                        pass
            subjects[block_id] = WalkthroughSubject(
                id=block_id,
                type=attrs.get("type", "code"),
                title=attrs.get("title", file_ref or block_id),
                language=lang,
                content=resolved_content,
                file_path=file_ref,
            )

    step_splits = re.split(r'(<!--\s*step:\s*\d+\s*.*?-->)', md_text, flags=re.IGNORECASE)

    for i in range(1, len(step_splits), 2):
        directive_str = step_splits[i]
        body_str = step_splits[i + 1] if i + 1 < len(step_splits) else ""
        match = STEP_DIRECTIVE_REGEX.search(directive_str)
        if not match:
            continue

        step_num = int(match.group(1))
        attrs = _parse_directive_attributes(match.group(2))
        step_id = attrs.get("id", f"step-{step_num}")
        target_subject = attrs.get("subject", "default")
        highlight_str = attrs.get("highlight", "")
        badge = attrs.get("badge", test_code or domain)
        step_status = attrs.get("status", "PASS").upper()
        latency_val = float(attrs.get("latency_ms")) if "latency_ms" in attrs else None

        cleaned_body_lines: List[str] = []
        step_title = attrs.get("title", f"Step {step_num}")

        for bline in body_str.strip().split("\n"):
            h_match = re.match(r'^#{1,3}\s+(.+)$', bline)
            if h_match and "title" not in attrs:
                step_title = h_match.group(1).strip()
                continue
            if bline.startswith("```") and 'id=' in bline:
                continue
            cleaned_body_lines.append(bline)

        cleaned_md = "\n".join(cleaned_body_lines).strip()
        body_html = _markdown_to_clean_html(cleaned_md)

        if target_subject.startswith("file:"):
            file_slug = target_subject[5:].strip()
            subj_id = f"file-{step_num}"
            if subj_id not in subjects:
                target_file = root / file_slug.lstrip("/")
                fcontent = f"# File {file_slug} could not be read."
                if target_file.exists() and target_file.is_file():
                    try:
                        fcontent = target_file.read_text(encoding="utf-8")
                    except Exception as e:
                        fcontent = f"# Error reading {file_slug}: {e}"
                subjects[subj_id] = WalkthroughSubject(
                    id=subj_id,
                    type="code",
                    title=file_slug,
                    language=Path(file_slug).suffix.lstrip(".") or "python",
                    content=fcontent,
                    file_path=file_slug,
                )
            target_subject = subj_id

        steps.append(
            WalkthroughStep(
                step_number=step_num,
                step_id=step_id,
                title=step_title,
                content_html=body_html,
                raw_markdown=cleaned_md,
                target_subject_id=target_subject,
                highlight_lines=_parse_highlight_ranges(highlight_str),
                badge=badge,
                latency_ms=latency_val,
                status=step_status,
            )
        )

    if not subjects:
        subjects["default"] = WalkthroughSubject(
            id="default",
            type="code",
            title="System Execution Context",
            language="markdown",
            content=md_text,
        )

    return WalkthroughDocument(
        title=title,
        domain=domain,
        test_code=test_code,
        deployment=deployment,
        duration_ms=duration_ms,
        verdict_status=verdict_status,
        steps=steps,
        subjects=subjects,
        metadata=metadata,
    )


def synthesize_walkthrough_from_manifest(
    manifest_or_dir: Union[Path, Dict[str, Any]],
    deployment: Optional[str] = None,
) -> WalkthroughDocument:
    manifest_data: Dict[str, Any] = {}
    if isinstance(manifest_or_dir, (str, Path)):
        p = Path(manifest_or_dir)
        if p.is_dir():
            for name in ("index.json", "manifest.json", "verdict.json"):
                f = p / name
                if f.exists():
                    try:
                        manifest_data = json.loads(f.read_text(encoding="utf-8"))
                        break
                    except Exception:
                        pass
        elif p.is_file():
            try:
                manifest_data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    else:
        manifest_data = manifest_or_dir

    title = manifest_data.get("title", "Execution Playback")
    dep = deployment or manifest_data.get("deployment", "staging")
    t_code = manifest_data.get("test_code", "RUN")
    status = manifest_data.get("status", "PASS")

    stage_results = manifest_data.get("stage_results") or manifest_data.get("results") or {}
    stages_executed = manifest_data.get("stages_executed") or list(stage_results.keys()) or ["execution"]

    steps: List[WalkthroughStep] = []
    subjects: Dict[str, WalkthroughSubject] = {}

    for idx, stage_name in enumerate(stages_executed, start=1):
        s_data = stage_results.get(stage_name, {"status": status})
        s_status = "PASS" if (isinstance(s_data, dict) and s_data.get("status") in (True, "PASS", "pass")) else "FAIL"
        content_str = json.dumps(s_data, indent=2)

        subj_id = f"stage-{idx}"
        subjects[subj_id] = WalkthroughSubject(
            id=subj_id,
            type="json",
            title=f"Telemetry: {stage_name}",
            language="json",
            content=content_str,
        )

        steps.append(
            WalkthroughStep(
                step_number=idx,
                step_id=f"step-{idx}",
                title=f"{idx}. {stage_name.replace('_', ' ').title()}",
                content_html=f'<p class="step-text">Stage <strong><code>{stage_name}</code></strong> completed with status <span class="status-pill status-{s_status.lower()}">{s_status}</span>.</p>',
                target_subject_id=subj_id,
                highlight_lines=[1, 2, 3],
                badge=t_code,
                status=s_status,
            )
        )

    return WalkthroughDocument(
        title=title,
        domain="QA",
        test_code=t_code,
        deployment=dep,
        verdict_status=status,
        steps=steps,
        subjects=subjects,
    )


# ── Standalone HTML Renderer ─────────────────────────────────────────────────

def render_walkthrough_html(doc: WalkthroughDocument) -> str:
    serialized_subjects: Dict[str, Any] = {}
    for s_id, s_obj in doc.subjects.items():
        lines = s_obj.content.split("\n")
        serialized_subjects[s_id] = {
            "id": s_obj.id,
            "type": s_obj.type,
            "title": s_obj.title or s_obj.id,
            "language": s_obj.language,
            "line_count": len(lines),
            "lines": lines,
        }
    subjects_json = json.dumps(serialized_subjects).replace("</script>", "<\\/script>")

    serialized_steps: List[Dict[str, Any]] = []
    for step in doc.steps:
        serialized_steps.append({
            "number": step.step_number,
            "id": step.step_id,
            "title": step.title,
            "subject_id": step.target_subject_id,
            "highlight_lines": step.highlight_lines,
            "badge": step.badge,
            "status": step.status,
            "latency_ms": step.latency_ms,
        })
    steps_json = json.dumps(serialized_steps).replace("</script>", "<\\/script>")

    total_steps = len(doc.steps)
    initial_step = doc.steps[0] if doc.steps else None
    initial_subject_id = initial_step.target_subject_id if initial_step else (list(doc.subjects.keys())[0] if doc.subjects else "default")
    initial_subject = doc.subjects.get(initial_subject_id)
    initial_lines = (initial_subject.content if initial_subject else "").split("\n")
    initial_highlights = set(initial_step.highlight_lines if initial_step else [])

    code_lines_html: List[str] = []
    for idx, line_text in enumerate(initial_lines, start=1):
        is_hl = idx in initial_highlights
        hl_class = " is-highlighted" if is_hl else (" is-dimmed" if initial_highlights else "")
        safe_line = html.escape(line_text) or "&nbsp;"
        code_lines_html.append(
            f'<div class="code-line{hl_class}" data-line="{idx}" id="line-{idx}">'
            f'<span class="line-num">{idx}</span>'
            f'<span class="line-content">{safe_line}</span>'
            f'</div>'
        )
    rendered_code_block = "\n".join(code_lines_html)

    step_cards_html: List[str] = []
    for idx, step in enumerate(doc.steps, start=1):
        active_class = " is-active" if idx == 1 else ""
        badge_markup = f'<span class="step-badge">{html.escape(step.badge)}</span>' if step.badge else ""
        status_markup = f'<span class="status-pill status-{step.status.lower()}">{step.status}</span>' if step.status else ""
        latency_markup = f'<span class="meta-pill">{round(step.latency_ms, 1)}ms</span>' if step.latency_ms is not None else ""

        step_cards_html.append(
            f'<article class="step-card{active_class}" data-step-index="{idx}" data-step-id="{step.step_id}" '
            f'data-subject-id="{step.target_subject_id}">'
            f'<div class="step-card-header">'
            f'<span class="step-number-badge">Step {str(idx).zfill(2)}</span>'
            f'{badge_markup}{status_markup}{latency_markup}'
            f'</div>'
            f'<h3 class="step-title">{html.escape(step.title)}</h3>'
            f'<div class="step-body">{step.content_html}</div>'
            f'</article>'
        )

    story_steps_markup = "\n".join(step_cards_html)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(doc.title)} — Interactive Walkthrough</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
<style>
  :root {{
    --bg: #090d0b;
    --bg2: #0d1310;
    --surface: rgba(21, 31, 26, 0.88);
    --surface2: rgba(26, 38, 32, 0.88);
    --surface3: rgba(34, 51, 42, 0.90);
    --line: rgba(255, 255, 255, 0.08);
    --brand: #0e3f2a;
    --brand-active: #1b5e3f;
    --brand-border: #2e7d56;
    --text: #f0f6f2;
    --text2: #9bb1a4;
    --text3: #6c8577;
    --ok: #2ea043;
    --warn: #d29922;
    --err: #f85149;
    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    --radius-capsule: 9999px;
    --radius-card: 12px;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background-color: var(--bg);
    color: var(--text);
    font: 14px/22px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }}

  header.walkthrough-header {{
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 32px;
    background: rgba(9, 13, 11, 0.94);
    border-bottom: 1px solid var(--line);
    backdrop-filter: blur(16px);
  }}

  .header-title-block {{ display: flex; flex-direction: column; }}
  .header-title {{ font-size: 15px; font-weight: 700; color: var(--text); }}
  .header-subtext {{ font-size: 11px; color: var(--text2); }}

  .stepper-pill {{
    display: inline-flex; align-items: center; gap: 8px; height: 38px; padding: 0 16px;
    border-radius: var(--radius-capsule); background: var(--surface2); border: 1px solid var(--line);
    font-size: 12px; font-weight: 600; color: var(--text); user-select: none;
  }}

  .btn-capsule {{
    display: inline-flex; align-items: center; justify-content: center; gap: 6px;
    height: 44px; min-height: 44px; padding: 0 18px; border-radius: var(--radius-capsule);
    border: 1px solid var(--brand-border); background: var(--brand); color: var(--text);
    font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: none;
    transition: transform 120ms cubic-bezier(0.2, 0, 0, 1), background 150ms ease; user-select: none;
  }}
  .btn-capsule:active {{ transform: scale(0.97); }}
  .btn-capsule.secondary {{ background: var(--surface2); border-color: var(--line); color: var(--text2); }}
  .btn-capsule.secondary:hover {{ background: var(--surface3); color: var(--text); }}
  .btn-capsule.icon-only {{ width: 44px; padding: 0; }}

  .progress-track {{ position: absolute; bottom: 0; left: 0; height: 2px; width: 100%; background: var(--line); }}
  .progress-fill {{ height: 100%; width: {100 / max(1, total_steps)}%; background: var(--ok); transition: width 200ms ease; }}

  .walkthrough-grid {{
    display: grid; grid-template-columns: minmax(360px, 1fr) minmax(480px, 1.4fr);
    gap: 32px; max-width: 1720px; margin: 0 auto; padding: 32px 32px 120px 32px;
  }}

  .story-rail {{ display: flex; flex-direction: column; padding-bottom: 240px; }}
  .step-card {{
    background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-card);
    padding: 28px; margin-bottom: 32px; transition: border-color 200ms ease, box-shadow 200ms ease; cursor: pointer;
  }}
  .step-card.is-active {{
    border-color: var(--brand-border); background: rgba(21, 31, 26, 0.98);
    box-shadow: 0 8px 32px rgba(14, 63, 42, 0.35);
  }}

  .step-card-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }}
  .step-number-badge {{
    padding: 2px 10px; border-radius: var(--radius-capsule); background: rgba(255, 255, 255, 0.08);
    font-size: 11px; font-weight: 700; color: var(--text); text-transform: uppercase;
  }}
  .step-badge {{
    padding: 2px 8px; border-radius: var(--radius-capsule); background: rgba(14, 63, 42, 0.4);
    border: 1px solid rgba(46, 125, 86, 0.6); font-size: 11px; font-weight: 700; color: var(--text);
  }}
  .step-title {{ font-size: 17px; font-weight: 700; color: var(--text); margin-bottom: 14px; }}
  .step-body {{ color: var(--text2); font-size: 14px; line-height: 22px; }}
  .inline-code {{ font-family: var(--mono); font-size: 12px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.06); color: #e6edf3; }}

  .callout {{ display: flex; gap: 12px; padding: 12px 16px; border-radius: 8px; margin: 14px 0; font-size: 13px; line-height: 19px; }}
  .callout-tip {{ background: rgba(46, 125, 86, 0.15); border: 1px solid rgba(46, 125, 86, 0.4); color: #f0f6f2; }}
  .callout-note {{ background: rgba(56, 139, 253, 0.12); border: 1px solid rgba(56, 139, 253, 0.35); color: #f0f6f2; }}

  .status-pill {{ padding: 2px 8px; border-radius: var(--radius-capsule); font-size: 11px; font-weight: 700; }}
  .status-pill.status-pass {{ background: rgba(46, 160, 67, 0.2); color: var(--ok); border: 1px solid rgba(46, 160, 67, 0.4); }}
  .meta-pill {{ padding: 2px 8px; border-radius: var(--radius-capsule); background: rgba(255,255,255,0.05); font-size: 11px; color: var(--text3); font-family: var(--mono); }}

  .subject-pane-container {{ position: sticky; top: 76px; height: calc(100vh - 100px); }}
  .subject-pane {{ height: 100%; display: flex; flex-direction: column; background: #080d0b; border: 1px solid var(--line); border-radius: var(--radius-card); overflow: hidden; }}
  .subject-toolbar {{ display: flex; align-items: center; justify-content: space-between; padding: 10px 18px; background: var(--surface2); border-bottom: 1px solid var(--line); }}
  .subject-title {{ font-size: 13px; font-weight: 600; color: var(--text); font-family: var(--mono); }}

  .code-viewport {{ flex: 1; overflow-y: auto; font-family: var(--mono); font-size: 13px; line-height: 22px; padding: 16px 0; background: #050807; scroll-behavior: smooth; }}
  .code-line {{ display: flex; padding: 0 20px 0 16px; min-height: 22px; transition: background 160ms ease, opacity 160ms ease; }}
  .code-line.is-dimmed {{ opacity: 0.42; }}
  .code-line.is-highlighted {{ background: rgba(46, 125, 86, 0.24); border-left: 4px solid var(--ok); opacity: 1; }}
  .line-num {{ width: 44px; user-select: none; color: var(--text3); text-align: right; padding-right: 18px; flex-shrink: 0; }}
  .line-content {{ color: #e6edf3; white-space: pre-wrap; word-break: break-all; flex: 1; }}

  @media (max-width: 1024px) {{
    .walkthrough-grid {{ grid-template-columns: 1fr; }}
    .subject-pane-container {{ position: relative; top: 0; height: 480px; margin-bottom: 32px; }}
  }}
</style>
</head>
<body>

<header class="walkthrough-header">
  <div class="header-title-block">
    <h1 class="header-title">{html.escape(doc.title)}</h1>
    <span class="header-subtext">{doc.deployment.upper()} &bull; Verdict: {doc.verdict_status}</span>
  </div>
  <div class="stepper-pill">
    <span class="material-symbols-outlined" style="font-size: 16px; color: var(--text2);">view_timeline</span>
    <span id="stepper-label">Step 1 of {total_steps}</span>
  </div>
  <div style="display: flex; gap: 8px;">
    <button class="btn-capsule secondary icon-only" id="btn-prev" title="Previous (k / ArrowUp)"><span class="material-symbols-outlined">arrow_upward</span></button>
    <button class="btn-capsule icon-only" id="btn-next" title="Next (j / ArrowDown)"><span class="material-symbols-outlined">arrow_downward</span></button>
  </div>
  <div class="progress-track"><div class="progress-fill" id="progress-bar"></div></div>
</header>

<main class="walkthrough-grid">
  <section class="story-rail">{story_steps_markup}</section>
  <aside class="subject-pane-container">
    <div class="subject-pane">
      <div class="subject-toolbar">
        <span class="subject-title" id="subject-title">{html.escape(initial_subject.title if initial_subject else "Context")}</span>
        <button class="btn-capsule secondary" id="btn-copy" style="height: 32px; padding: 0 12px; font-size: 11px;">Copy</button>
      </div>
      <div class="code-viewport" id="code-viewport">{rendered_code_block}</div>
    </div>
  </aside>
</main>

<script>
(function() {{
  const SUBJECTS = {subjects_json};
  const STEPS = {steps_json};
  const TOTAL = STEPS.length;
  let currentStep = 1;

  const stepperLabel = document.getElementById("stepper-label");
  const progressBar = document.getElementById("progress-bar");
  const subjectTitle = document.getElementById("subject-title");
  const codeViewport = document.getElementById("code-viewport");
  const btnPrev = document.getElementById("btn-prev");
  const btnNext = document.getElementById("btn-next");
  const btnCopy = document.getElementById("btn-copy");
  const stepCards = document.querySelectorAll(".step-card");

  function escapeHtml(str) {{
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }}

  function activateStep(stepNum) {{
    if (stepNum < 1 || stepNum > TOTAL) return;
    currentStep = stepNum;
    const stepData = STEPS[stepNum - 1];
    if (!stepData) return;

    stepperLabel.textContent = `Step ${{stepNum}} of ${{TOTAL}}`;
    progressBar.style.width = `${{(stepNum / TOTAL) * 100}}%`;

    stepCards.forEach((c, idx) => {{
      if (idx + 1 === stepNum) c.classList.add("is-active");
      else c.classList.remove("is-active");
    }});

    const subj = SUBJECTS[stepData.subject_id] || Object.values(SUBJECTS)[0];
    if (subj) {{
      subjectTitle.textContent = subj.title;
      const hlSet = new Set(stepData.highlight_lines || []);
      codeViewport.replaceChildren();
      const frag = document.createDocumentFragment();
      subj.lines.forEach((txt, i) => {{
        const ln = i + 1;
        const isHl = hlSet.has(ln);
        const cl = isHl ? " is-highlighted" : (hlSet.size > 0 ? " is-dimmed" : "");
        const div = document.createElement("div");
        div.className = `code-line${{cl}}`;
        div.dataset.line = String(ln);
        div.id = `line-${{ln}}`;
        const sNum = document.createElement("span");
        sNum.className = "line-num";
        sNum.textContent = String(ln);
        const sContent = document.createElement("span");
        sContent.className = "line-content";
        sContent.textContent = txt || " ";
        div.appendChild(sNum);
        div.appendChild(sContent);
        frag.appendChild(div);
      }});
      codeViewport.appendChild(frag);

      if (stepData.highlight_lines && stepData.highlight_lines.length > 0) {{
        const target = document.getElementById(`line-${{Math.min(...stepData.highlight_lines)}}`);
        if (target) target.scrollIntoView({{ behavior: "smooth", block: "center" }});
      }} else {{
        codeViewport.scrollTo({{ top: 0, behavior: "smooth" }});
      }}
    }}
  }}

  const observer = new IntersectionObserver((entries) => {{
    entries.forEach(e => {{
      if (e.isIntersecting) {{
        const num = parseInt(e.target.getAttribute("data-step-index"), 10);
        if (num && num !== currentStep) activateStep(num);
      }}
    }});
  }}, {{ rootMargin: "-20% 0px -40% 0px", threshold: 0.1 }});

  stepCards.forEach(c => observer.observe(c));
  stepCards.forEach((c, idx) => c.addEventListener("click", () => {{
    activateStep(idx + 1);
    c.scrollIntoView({{ behavior: "smooth", block: "center" }});
  }}));

  btnPrev.addEventListener("click", () => {{
    if (currentStep > 1) {{
      stepCards[currentStep - 2].scrollIntoView({{ behavior: "smooth", block: "center" }});
      activateStep(currentStep - 1);
    }}
  }});

  btnNext.addEventListener("click", () => {{
    if (currentStep < TOTAL) {{
      stepCards[currentStep].scrollIntoView({{ behavior: "smooth", block: "center" }});
      activateStep(currentStep + 1);
    }}
  }});

  window.addEventListener("keydown", (e) => {{
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (e.key === "ArrowDown" || e.key === "j") {{ e.preventDefault(); btnNext.click(); }}
    else if (e.key === "ArrowUp" || e.key === "k") {{ e.preventDefault(); btnPrev.click(); }}
  }});

  btnCopy.addEventListener("click", () => {{
    const subj = SUBJECTS[STEPS[currentStep - 1]?.subject_id] || Object.values(SUBJECTS)[0];
    if (subj) navigator.clipboard.writeText(subj.lines.join("\\n")).then(() => {{
      btnCopy.textContent = "Copied!";
      setTimeout(() => {{ btnCopy.textContent = "Copy"; }}, 1600);
    }});
  }});
}})();
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Standalone Scrollytelling Walkthrough Compiler")
    parser.add_argument("--file", "-f", type=Path, help="Markdown walkthrough or manifest path")
    parser.add_argument("--output", "-o", type=Path, help="Output HTML destination")
    parser.add_argument("--serve", "-s", action="store_true", help="Start local HTTP preview server")
    parser.add_argument("--port", "-p", type=int, default=8095, help="Server port (default: 8095)")
    args = parser.parse_args()

    if args.file:
        if args.file.suffix.lower() == ".json":
            doc = synthesize_walkthrough_from_manifest(args.file)
        else:
            doc = parse_walkthrough_markdown(args.file.read_text(encoding="utf-8"))
        html_out = render_walkthrough_html(doc)
        dest = args.output or Path("walkthrough.html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")
        logger.info(f"Compiled walkthrough to: {dest}")

    if args.serve:
        logger.info(f"Serving on http://127.0.0.1:{args.port}/")
        server = HTTPServer(("0.0.0.0", args.port), SimpleHTTPRequestHandler)
        server.serve_forever()


if __name__ == "__main__":
    main()
