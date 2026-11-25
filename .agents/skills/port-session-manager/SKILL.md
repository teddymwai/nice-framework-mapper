---
name: "port-session-manager"
description: "Author, audit, and debug local HTTP control planes, dedicated port allocation, EADDRINUSE auto-recovery, and thread-safe session lifecycle management"
---

# Local Port & Session Management Skill

Distilled from `CYBER RANGES Agents/tools/recorder_studio/server.py` and `TedRedCraft/tools/security_cockpit/server.py`.

## Operational Purpose
Provides end-to-end guidance and verified patterns for implementing local HTTP servers, dedicated port management, socket lifecycle controls, thread-safe session state machines, production mutation interlocks, and CSRF defense for operator authoring surfaces and test harness tools.

---

## 1. Port Registry & Conflict Recovery

### Dedicated Port Matrix
- `6769`: Embedded Telemetry & Warmup Logserver (`tools/template_runner/boot_mct_logserver.py`)
- `8770`: UI Recorder Studio & Semantic Ingestion Server (`tools/recorder_studio/server.py`)
- `8780`: Scrollytelling Walkthrough Player Preview Dashboard (`templates/walkthrough_engine.py`)
- `8787`: Operator Panel & Nightly Orchestrator Cockpit (`tools/operator_panel/server.py`)
- `8790`: TedRedCraft Local Security Cockpit (`tools/security_cockpit/server.py`)
- `8771`–`8786`: Reserved Local Tooling & Inspection Range
- `8000`–`8080`: Local Application & Mock Services

### Socket Lifecycle Pattern
Always bind exclusively to `127.0.0.1` and enable `SO_REUSEADDR`:

```python
import errno
import logging
import sys
from http.server import ThreadingHTTPServer

logger = logging.getLogger("server")

def launch_server(host: str, port: int, handler_cls) -> int:
    ThreadingHTTPServer.allow_reuse_address = True
    try:
        server = ThreadingHTTPServer((host, port), handler_cls)
    except OSError as exc:
        if exc.errno in (errno.EADDRINUSE, 48, 98):
            logger.error(f"[!] Bind Conflict: Port {port} is already in use on {host}.")
            logger.info("[*] Diagnostic Options:")
            logger.info(f"    • Active instance:   http://{host}:{port}/")
            logger.info(f"    • Terminate owner:   kill $(lsof -t -i :{port})")
            logger.info(f"    • Fallback port:     python3 {sys.argv[0]} --port {port + 1}")
            return 1
        raise

    logger.info(f"Server active at http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Gracefully stopping server...")
        server.server_close()
    return 0
```

---

## 2. Thread-Safe Session State Management

### State Lifecycle
`IDLE` &rarr; `STARTING` &rarr; `RECORDING` / `WORKING` &rarr; `INGESTING` &rarr; `COMPLETED` (or `ERROR`).

### Core Implementation
```python
import threading
from typing import Optional, Dict, Any

class SessionStateManager:
    """Thread-safe state manager for background recording or execution sessions."""

    def __init__(self):
        self.lock = threading.Lock()
        self.status = "IDLE"
        self.worker_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.error_msg: Optional[str] = None
        self.report_md: Optional[str] = None

    def auto_heal(self):
        """Auto-recovers state to IDLE if the previous worker crashed."""
        with self.lock:
            if self.worker_thread and not self.worker_thread.is_alive():
                if self.status in ("STARTING", "RECORDING", "WORKING", "INGESTING"):
                    self.status = "IDLE"
                    self.error_msg = None

    def request_start(self, target_worker, args=()) -> bool:
        self.auto_heal()
        with self.lock:
            if self.status in ("STARTING", "RECORDING", "WORKING", "INGESTING"):
                return False  # Caller should respond with 409 Conflict
            self.status = "STARTING"
            self.stop_event.clear()
            self.worker_thread = threading.Thread(target=target_worker, args=args, daemon=True)
            self.worker_thread.start()
            return True

    def abort(self, timeout: float = 3.0):
        self.stop_event.set()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=timeout)
        with self.lock:
            self.status = "IDLE"
            self.stop_event.clear()
```

---

## 3. Production Affirmative Mutation Interlock

When mutating endpoints are invoked against production:
1. Verify target deployment is production (`deployment in ("production", "prod", "cyberranges.com")`).
2. Verify mutation is explicitly requested (`allow_mutation == True`).
3. Enforce the exact confirmation token `PROD-MUTATE`.
4. If invalid or missing, respond with `403 Forbidden`:
   ```python
   if is_prod and allow_mutation:
       if token != "PROD-MUTATE":
           return self._json(403, {"error": "Production mutation rejected: Missing token 'PROD-MUTATE'"})
   ```

---

## 4. CSRF, Origin Defense & Body Restrictions

1. **Token Generation**: `secrets.token_urlsafe(24)`.
2. **Template Injection**: Dynamically replace `__TOKEN_PLACEHOLDER__` in served HTML.
3. **Verification**: Validate `X-Session-Token` with `hmac.compare_digest(token, server.token)`.
4. **Origin Check**: Inspect `Origin` header; reject non-loopback domains.
5. **Body Ceiling**: Enforce `MAX_BODY_BYTES = 1_048_576` (1 MB) to prevent memory exhaustion attacks.
6. **Path Confinement (`SEC-01`)**: Resolve every static/artifact file path via `target = (base_dir / rel).resolve()` and assert `target.is_relative_to(base_dir.resolve())`.

---

## 5. In-Tandem Server Daemon Lifecycle (`--dashboard`)

Every CLI runner or auditor with a local dashboard must expose `--dashboard` and launch/reuse the server automatically via `socket.connect_ex`:

```python
import socket
import threading
import time
from http.server import ThreadingHTTPServer

def ensure_dashboard_running(host: str = "127.0.0.1", port: int = 8770, server_cls=ThreadingHTTPServer, handler_cls=None) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        if s.connect_ex((host, port)) == 0:
            print(f"[*] Dashboard already active on http://{host}:{port}/")
            return True

    def _run():
        server_cls.allow_reuse_address = True
        try:
            httpd = server_cls((host, port), handler_cls)
            httpd.serve_forever()
        except Exception:
            pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    print("=" * 70)
    print(f"[*] Dashboard launched in tandem at http://{host}:{port}/")
    print("=" * 70)
    time.sleep(0.3)
    return True
```
