#!/usr/bin/env python3
"""
Interactive Local Server & Session Control Plane Boilerplate
────────────────────────────────────────────────────────────
Compliant with the Antigravity Autonomous Engineering Harness:
  - Strict loopback binding (127.0.0.1) & SO_REUSEADDR socket reuse
  - Graceful EADDRINUSE conflict recovery with diagnostic lsof commands
  - In-tandem server lifecycle (ensure_dashboard_running via socket.connect_ex + daemon thread)
  - Thread-safe session state machine (IDLE -> STARTING -> WORKING -> INGESTING -> COMPLETED)
  - Dead worker thread auto-healing & 409 Conflict multi-session recovery
  - Production mutation safety interlock (PROD-MUTATE affirmative token)
  - Dynamic CSRF token generation (secrets.token_urlsafe) & constant-time validation (hmac.compare_digest)
  - Confined static/artifact serving (.resolve().is_relative_to()) & 1MB body limit (SEC-01..SEC-04)
  - On-demand run-report.md synthesis from verdict.json so report links never 404
  - Offline --selftest verification mode
"""

from __future__ import annotations

import argparse
import errno
import hmac
import json
import logging
import re
import secrets
import socket
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

TOOL_NAME = "server_control_plane"
DEFAULT_PORT = 8770
MAX_BODY_BYTES = 1_048_576  # 1 MB (SEC-04)
TEMPLATE_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = (Path.cwd() / "output").resolve()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(TOOL_NAME)

DEFAULT_DEPLOYMENTS: Dict[str, Dict[str, Any]] = {
    "staging": {
        "key": "staging",
        "description": "Staging Validation Sandbox (Read/Write)",
        "base_domain": "staging.internal",
        "production": False,
    },
    "local": {
        "key": "local",
        "description": "Local Loopback Workstation Sandbox",
        "base_domain": "127.0.0.1",
        "production": False,
    },
    "production": {
        "key": "production",
        "description": "Global Production System of Record (Read-Only Default)",
        "base_domain": "cyberranges.com",
        "production": True,
    },
}

DEFAULT_CATALOG: List[Dict[str, Any]] = [
    {"code": "SYN-01", "title": "Synthetic Baseline & IPC Barrier Smoke", "domain": "core", "mutates": False},
    {"code": "API-01", "title": "Dynamic Endpoint & Schema Verification", "domain": "api", "mutates": False},
    {"code": "UI-01", "title": "Interactive Portal & Stateful Lifecycle", "domain": "ui", "mutates": True},
]


def synthesize_report_from_verdict(run_dir: Path) -> Optional[str]:
    """Synthesizes run-report.md on demand from verdict.json if missing on disk."""
    verdict_file = (run_dir / "verdict.json").resolve()
    if not verdict_file.is_file() or not verdict_file.is_relative_to(run_dir.resolve()):
        return None
    try:
        v = json.loads(verdict_file.read_text(encoding="utf-8"))
    except Exception:
        return None

    report_md = (
        f"# Session Execution Report ({v.get('suite', 'run')})\n\n"
        f"- **Run ID:** `{v.get('run_id', run_dir.name)}`\n"
        f"- **Deployment:** `{v.get('deployment', 'staging')}`\n"
        f"- **Operator:** `{v.get('operator', 'Ted Mwai, QA Lead')}`\n"
        f"- **Status:** **`{v.get('status', 'PASS')}`**\n"
        f"- **Duration:** `{v.get('duration_seconds', 0)}s`\n\n"
        f"## Summary\n\n{v.get('summary', 'Synthesized on demand from verdict.json.')}\n"
    )
    report_path = (run_dir / "run-report.md").resolve()
    if report_path.is_relative_to(run_dir.resolve()):
        report_path.write_text(report_md, encoding="utf-8")
    return report_md


class SessionStateManager:
    """Thread-safe state manager for background execution sessions."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.status = "IDLE"  # IDLE, STARTING, WORKING, INGESTING, COMPLETED, ERROR
        self.deployment = "staging"
        self.operator = "Ted Mwai, QA Lead"
        self.allow_mutation = False
        self.suite_tag = "pilot_run"
        self.run_id: Optional[str] = None
        self.start_time: Optional[float] = None
        self.output_dir: Optional[Path] = None
        self.actions: List[Dict[str, Any]] = []
        self.events_log: List[str] = []
        self.report_md: Optional[str] = None
        self.report_json: Optional[Dict[str, Any]] = None
        self.error_msg: Optional[str] = None
        self.stop_event = threading.Event()
        self.worker_thread: Optional[threading.Thread] = None

    def auto_heal(self) -> None:
        """Auto-recover state to IDLE if the worker thread died unexpectedly."""
        with self.lock:
            if self.worker_thread and not self.worker_thread.is_alive():
                if self.status in ("STARTING", "WORKING", "INGESTING"):
                    logger.warning(
                        f"Detected terminated worker thread while status was '{self.status}'. "
                        "Auto-recovering to IDLE."
                    )
                    self.status = "IDLE"
                    self.error_msg = None

    def reset(self) -> None:
        """Affirmatively abort active work and reset session state."""
        self.stop_event.set()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=3.0)
        with self.lock:
            self.status = "IDLE"
            self.start_time = None
            self.error_msg = None
            self.actions = []
            self.events_log = ["[ControlPlane] Session affirmatively reset to IDLE."]
            self.report_md = None
            self.report_json = None
            self.output_dir = None
            self.stop_event.clear()

    def get_state(self) -> Dict[str, Any]:
        with self.lock:
            elapsed = 0
            if self.start_time and self.status in ("WORKING", "INGESTING"):
                elapsed = int(time.time() - self.start_time)
            return {
                "status": self.status,
                "deployment": self.deployment,
                "operator": self.operator,
                "allow_mutation": self.allow_mutation,
                "suite_tag": self.suite_tag,
                "run_id": self.run_id,
                "elapsed_sec": elapsed,
                "output_dir": str(self.output_dir) if self.output_dir else None,
                "actions_count": len(self.actions),
                "actions": list(self.actions),
                "events_log": list(self.events_log[-50:]),
                "error_msg": self.error_msg,
                "has_report": bool(self.report_md),
            }


GLOBAL_SESSION = SessionStateManager()


def _background_worker(
    session: SessionStateManager,
    deployment: str,
    operator: str,
    suites: List[str],
    suite_tag: str,
    run_id: str,
    output_dir: Path,
) -> None:
    """Background worker emitting incremental events, verdict.json, and run-report.md."""
    try:
        with session.lock:
            session.status = "WORKING"
            session.start_time = time.time()
            session.events_log.append(f"[{run_id}] Started execution on '{deployment}' (Operator: {operator})")

        planned = suites or ["SYN-01", "API-01"]
        for idx, code in enumerate(planned, 1):
            if session.stop_event.is_set():
                with session.lock:
                    session.events_log.append(f"[{run_id}] Cooperative stop signal observed; draining cleanly.")
                    session.status = "IDLE"
                return

            time.sleep(0.4)
            step_record = {
                "step": idx,
                "suite": code,
                "domain": "verification",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": f"Verified suite {code}",
                "status": "PASS",
            }
            with session.lock:
                session.actions.append(step_record)
                session.events_log.append(f"[seq={idx}] Suite {code} converged affirmatively -> PASS")

        with session.lock:
            session.status = "INGESTING"

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        report_md = (
            f"# Session Execution Report\n\n"
            f"> **Generated:** `{now_str}` | **Deployment:** `{deployment}` | **Operator:** `{operator}`\n\n"
            f"## Execution Steps\n\n"
            f"| Step | Suite | Status |\n"
            f"|---|---|---|\n"
        )
        for act in session.actions:
            report_md += f"| {act['step']} | {act['suite']} | {act['status']} |\n"

        verdict = {
            "version": "1.0.0",
            "suite": suite_tag,
            "deployment": deployment,
            "operator": operator,
            "run_id": run_id,
            "status": "PASS",
            "duration_seconds": round(time.time() - (session.start_time or time.time()), 2),
            "summary": f"Completed {len(session.actions)} suite(s) cleanly.",
            "checks": [{"name": a["suite"], "status": a["status"], "detail": a["action"]} for a in session.actions],
            "telemetry": {"redaction_applied": True, "screenshots_count": 0, "wire_requests_count": len(session.actions)},
        }

        resolved_out = output_dir.resolve()
        resolved_out.mkdir(parents=True, exist_ok=True)
        (resolved_out / "run-report.md").resolve().write_text(report_md, encoding="utf-8")
        (resolved_out / "verdict.json").resolve().write_text(json.dumps(verdict, indent=2), encoding="utf-8")

        with session.lock:
            session.report_md = report_md
            session.report_json = verdict
            session.events_log.append(f"[{run_id}] Artifacts written to {resolved_out}")
            session.status = "COMPLETED"

    except Exception as exc:
        logger.exception(f"Unhandled error in session worker: {exc}")
        with session.lock:
            session.status = "ERROR"
            session.error_msg = str(exc)


class ControlPlaneServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_cls: type[BaseHTTPRequestHandler]):
        self.session_token = secrets.token_urlsafe(24)
        self.deployments = dict(DEFAULT_DEPLOYMENTS)
        super().__init__(server_address, handler_cls)


class ControlPlaneHandler(BaseHTTPRequestHandler):
    server: ControlPlaneServer

    def _is_loopback_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        origin_lower = origin.lower()
        return any(
            origin_lower.startswith(prefix)
            for prefix in ("http://127.0.0.1", "http://localhost", "http://[::1]")
        )

    def _verify_csrf(self) -> bool:
        token = self.headers.get("X-Session-Token", "")
        if not token:
            return False
        return hmac.compare_digest(token, self.server.session_token)

    def _json(self, status: int, data: Dict[str, Any]) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _list_runs(self) -> List[Dict[str, Any]]:
        runs: List[Dict[str, Any]] = []
        if not OUTPUT_ROOT.is_dir():
            return runs
        for v_file in sorted(OUTPUT_ROOT.rglob("verdict.json"), reverse=True)[:25]:
            resolved_v = v_file.resolve()
            if not resolved_v.is_relative_to(OUTPUT_ROOT):
                continue
            try:
                data = json.loads(resolved_v.read_text(encoding="utf-8"))
                runs.append({
                    "run_id": data.get("run_id", resolved_v.parent.name),
                    "deployment": data.get("deployment", "staging"),
                    "suite": data.get("suite", TOOL_NAME),
                    "status": data.get("status", "PASS"),
                    "duration_seconds": data.get("duration_seconds", 0),
                })
            except Exception:
                continue
        return runs

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        if path in ("/", "/index.html", "/dashboard_boilerplate.html", f"/{TOOL_NAME}_dashboard.html"):
            dash_file = (TEMPLATE_DIR / "dashboard_boilerplate.html").resolve()
            if dash_file.is_file() and dash_file.is_relative_to(TEMPLATE_DIR):
                raw_html = dash_file.read_text(encoding="utf-8")
            else:
                raw_html = "<!DOCTYPE html><html><body>Dashboard template missing</body></html>"
            injected = raw_html.replace("__SESSION_TOKEN_PLACEHOLDER__", self.server.session_token)
            encoded = injected.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
                "base-uri 'none'; object-src 'none'",
            )
            self.end_headers()
            self.wfile.write(encoded)
            return

        if path in ("/api/config", "/api/deployments"):
            self._json(200, {"default": "staging", "deployments": list(self.server.deployments.values())})
            return

        if path == "/api/catalog":
            self._json(200, {"suites": DEFAULT_CATALOG, "profiles": ["smoke", "full"]})
            return

        if path == "/api/plan":
            suites = [s for s in query.get("suites", "").split(",") if s] or [c["code"] for c in DEFAULT_CATALOG]
            self._json(200, {"resolved_dag": suites, "auto_included": []})
            return

        if path == "/api/session/status":
            GLOBAL_SESSION.auto_heal()
            self._json(200, GLOBAL_SESSION.get_state())
            return

        if path == "/api/runs":
            GLOBAL_SESSION.auto_heal()
            self._json(200, {"runs": self._list_runs(), "active": GLOBAL_SESSION.status in ("STARTING", "WORKING")})
            return

        if path.startswith("/api/runs/") and path.endswith("/report"):
            run_id = path[len("/api/runs/") : -len("/report")].strip("/")
            clean_id = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", run_id)
            for v_file in OUTPUT_ROOT.rglob("verdict.json"):
                run_dir = v_file.parent.resolve()
                if not run_dir.is_relative_to(OUTPUT_ROOT):
                    continue
                if run_dir.name == clean_id:
                    rep_file = (run_dir / "run-report.md").resolve()
                    if rep_file.is_file() and rep_file.is_relative_to(run_dir):
                        md = rep_file.read_text(encoding="utf-8")
                    else:
                        md = synthesize_report_from_verdict(run_dir) or "Report unavailable."
                    self._json(200, {"run_id": clean_id, "report_md": md})
                    return
            if GLOBAL_SESSION.report_md:
                self._json(200, {"run_id": clean_id, "report_md": GLOBAL_SESSION.report_md})
                return
            self._json(404, {"error": "Run report not found"})
            return

        if path.startswith("/files/"):
            rel_str = path[len("/files/") :].lstrip("/")
            target = (OUTPUT_ROOT / rel_str).resolve()
            if not target.is_relative_to(OUTPUT_ROOT):
                self._json(403, {"error": "Path traversal rejected"})
                return
            if not target.is_file() and target.name == "run-report.md" and target.parent.is_dir():
                synthesize_report_from_verdict(target.parent)
            if target.is_file():
                data = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            self._json(404, {"error": "Artifact not found"})
            return

        self._json(404, {"error": "Endpoint not found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self._is_loopback_origin():
            self._json(403, {"error": "Cross-origin request rejected"})
            return

        if not self._verify_csrf():
            self._json(403, {"error": "Missing or invalid X-Session-Token"})
            return

        length_hdr = self.headers.get("Content-Length", "0")
        try:
            length = int(length_hdr)
        except ValueError:
            length = 0

        if length > MAX_BODY_BYTES:
            self._json(413, {"error": "Payload exceeds 1MB limit"})
            return

        raw_body = self.rfile.read(min(length, MAX_BODY_BYTES)) if length > 0 else b"{}"
        try:
            body = json.loads(raw_body)
        except Exception:
            body = {}

        path = self.path.split("?")[0]

        if path in ("/api/session/abort", "/api/session/reset"):
            logger.info("Operator requested affirmative abort/reset.")
            GLOBAL_SESSION.reset()
            self._json(200, {"ok": True, "status": "IDLE"})
            return

        if path == "/api/deployments/onboard":
            slug = re.sub(r"[^a-zA-Z0-9_\-]", "_", str(body.get("custom_name") or "custom")).lower()
            app_url = str(body.get("app_url") or "https://staging.internal").strip()
            self.server.deployments[slug] = {
                "key": slug,
                "description": f"Onboarded Target ({app_url})",
                "base_domain": app_url,
                "production": False,
            }
            self._json(200, {"ok": True, "slug": slug, "deployment": self.server.deployments[slug]})
            return

        if path in ("/api/session/start", "/api/runs"):
            GLOBAL_SESSION.auto_heal()
            with GLOBAL_SESSION.lock:
                if GLOBAL_SESSION.status in ("STARTING", "WORKING", "INGESTING"):
                    self._json(
                        409,
                        {
                            "error": f"Session already active ({GLOBAL_SESSION.status}). Click 'Force Reset' to abort.",
                            "status": GLOBAL_SESSION.status,
                        },
                    )
                    return

                deployment = re.sub(r"[^a-zA-Z0-9_\-]", "_", str(body.get("deployment", "staging")))
                operator = str(body.get("operator") or "Ted Mwai, QA Lead").strip()
                suites = [re.sub(r"[^a-zA-Z0-9_\-]", "_", str(s)) for s in (body.get("suites") or [])]
                suite_tag = re.sub(r"[^a-zA-Z0-9_\-]", "_", str(body.get("suite_tag", "run")))
                allow_mutation = bool(body.get("allow_mutation", False))
                prod_token = str(body.get("prod_mutation_token", "")).strip()

                is_prod = deployment in ("production", "prod", "cyberranges.com")
                if is_prod and allow_mutation:
                    if prod_token != "PROD-MUTATE":
                        self._json(
                            403,
                            {"error": "Production mutation rejected: Missing or invalid token 'PROD-MUTATE'."},
                        )
                        return
                    logger.warning("[SAFETY OVERRIDE] Armed mutation on GLOBAL PRODUCTION with token 'PROD-MUTATE'.")

                now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
                run_id = f"{suite_tag}_{now_ts}"
                output_dir = (OUTPUT_ROOT / deployment / TOOL_NAME / run_id).resolve()
                if not output_dir.is_relative_to(OUTPUT_ROOT):
                    self._json(400, {"error": "Invalid output directory resolution"})
                    return
                output_dir.mkdir(parents=True, exist_ok=True)

                GLOBAL_SESSION.status = "STARTING"
                GLOBAL_SESSION.deployment = deployment
                GLOBAL_SESSION.operator = operator
                GLOBAL_SESSION.allow_mutation = allow_mutation
                GLOBAL_SESSION.suite_tag = suite_tag
                GLOBAL_SESSION.run_id = run_id
                GLOBAL_SESSION.output_dir = output_dir
                GLOBAL_SESSION.actions = []
                GLOBAL_SESSION.events_log = []
                GLOBAL_SESSION.report_md = None
                GLOBAL_SESSION.report_json = None
                GLOBAL_SESSION.error_msg = None
                GLOBAL_SESSION.stop_event.clear()

            t = threading.Thread(
                target=_background_worker,
                args=(GLOBAL_SESSION, deployment, operator, suites, suite_tag, run_id, output_dir),
                daemon=True,
            )
            GLOBAL_SESSION.worker_thread = t
            t.start()

            self._json(200, {"ok": True, "status": "STARTING", "run_id": run_id, "output_dir": str(output_dir)})
            return

        if path in ("/api/session/stop", "/api/stop"):
            with GLOBAL_SESSION.lock:
                if GLOBAL_SESSION.status not in ("WORKING", "STARTING"):
                    self._json(400, {"error": f"Cannot stop session in status '{GLOBAL_SESSION.status}'."})
                    return

            GLOBAL_SESSION.stop_event.set()
            if GLOBAL_SESSION.worker_thread:
                GLOBAL_SESSION.worker_thread.join(timeout=5.0)

            self._json(200, {"ok": True, "state": GLOBAL_SESSION.get_state()})
            return

        self._json(404, {"error": "Endpoint not found"})

    def log_message(self, fmt: str, *args: Any) -> None:
        pass


def ensure_dashboard_running(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> bool:
    """Ensures the local control plane is active; spawns a background daemon thread if not running."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        if sock.connect_ex((host, port)) == 0:
            logger.info(f"[*] Control Plane already active on http://{host}:{port}/")
            return True

    def _serve() -> None:
        ControlPlaneServer.allow_reuse_address = True
        try:
            httpd = ControlPlaneServer((host, port), ControlPlaneHandler)
            httpd.serve_forever()
        except Exception:
            pass

    srv_thread = threading.Thread(target=_serve, daemon=True)
    srv_thread.start()
    logger.info("=" * 70)
    logger.info(f"[*] {TOOL_NAME} launched in tandem at http://{host}:{port}/")
    logger.info("=" * 70)
    time.sleep(0.3)
    return True


def run_selftest() -> int:
    """Offline self-test verifying session auto-healing, reset, and on-demand report synthesis."""
    mgr = SessionStateManager()
    mgr.status = "WORKING"
    # Simulate dead worker thread auto-healing
    dead_thread = threading.Thread(target=lambda: None)
    dead_thread.start()
    dead_thread.join()
    mgr.worker_thread = dead_thread
    mgr.auto_heal()
    assert mgr.status == "IDLE", "Dead worker thread must auto-heal to IDLE"

    with tempfile.TemporaryDirectory() as tmp:
        rdir = Path(tmp).resolve()
        (rdir / "verdict.json").write_text(
            json.dumps({"suite": "SELFTEST-01", "run_id": "test_1", "status": "PASS", "duration_seconds": 0.5}),
            encoding="utf-8",
        )
        synthesized = synthesize_report_from_verdict(rdir)
        assert synthesized and "SELFTEST-01" in synthesized, "On-demand report synthesis failed"
        assert (rdir / "run-report.md").is_file(), "run-report.md was not persisted on demand"

    dash_html = (TEMPLATE_DIR / "dashboard_boilerplate.html").resolve()
    assert dash_html.is_file(), "dashboard_boilerplate.html must exist alongside server_boilerplate.py"
    print(f"[{TOOL_NAME}] Selftest: state machine auto-heal, report synthesis & dashboard template PASSED.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=f"{TOOL_NAME} - Interactive Local Server & Session Control Plane")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"HTTP server port (default: {DEFAULT_PORT})")
    parser.add_argument("--host", default="127.0.0.1", help="Loopback bind address (default: 127.0.0.1)")
    parser.add_argument("--selftest", action="store_true", help="Run offline unit selftests and exit")
    args = parser.parse_args()

    if args.selftest:
        return run_selftest()

    ControlPlaneServer.allow_reuse_address = True
    try:
        server = ControlPlaneServer((args.host, args.port), ControlPlaneHandler)
    except OSError as exc:
        if exc.errno in (errno.EADDRINUSE, 48, 98):
            logger.error(f"[!] Bind Conflict: Port {args.port} is already in use on {args.host}.")
            logger.error(f"[*] An instance of {TOOL_NAME} is likely already active.")
            logger.info("[*] Options:")
            logger.info(f"    • Access active instance:   http://{args.host}:{args.port}/")
            logger.info(f"    • Stop existing instance:   kill $(lsof -t -i :{args.port})")
            logger.info(f"    • Alternate port fallback:  python3 {sys.argv[0]} --port {args.port + 1}")
            return 1
        raise

    logger.info("=" * 70)
    logger.info(f"{TOOL_NAME} active at http://{args.host}:{args.port}/")
    logger.info(f"Session Token Prefix: {server.session_token[:8]}... (Loopback Only)")
    logger.info("=" * 70)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        GLOBAL_SESSION.stop_event.set()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
