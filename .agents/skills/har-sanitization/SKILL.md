---
name: har-sanitization
description: Redact, scrub, and sanitize HTTP Archive (.har) files, network wire captures, and telemetry logs before git commits to prevent credential leakage.
---

# Network & HAR Telemetry Sanitization

This skill provides the standard procedure and scripts to sanitize HTTP Archive (`.har`) files, wire captures, and diagnostic logs prior to version control commits.

---

## 1. What Must Be Scrubbed

1. **Authorization Headers**: `Bearer eyJ...`, `Basic ...`
2. **Session Cookies**: Any cookie containing `session`, `token`, `auth`, `sid`, `jwt`
3. **API Keys**: `x-api-key`, `apikey`, `secret`
4. **Binary Bloat**: Images, font binaries (`.ttf`, `.woff2`), video streams, and large base64 chunks
5. **Third-Party Telemetry**: Google Analytics, Sentry, Datadog tracker traffic

---

## 2. Python Sanitization Filter Blueprint

```python
import json
import re

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}
SENSITIVE_COOKIE_REGEX = re.compile(r"(session|auth|token|jwt|sid)", re.IGNORECASE)

def sanitize_har_entry(entry):
    # Sanitize request headers
    for h in entry.get("request", {}).get("headers", []):
        if h.get("name", "").lower() in SENSITIVE_HEADERS:
            h["value"] = "[REDACTED]"
            
    # Sanitize cookies
    if "cookies" in entry.get("request", {}):
        for c in entry["request"]["cookies"]:
            if SENSITIVE_COOKIE_REGEX.search(c.get("name", "")):
                c["value"] = "[REDACTED]"
                
    # Strip response binary data if mimeType is binary
    response = entry.get("response", {})
    mime = response.get("content", {}).get("mimeType", "")
    if any(b in mime for b in ["image/", "font/", "octet-stream", "video/"]):
        response["content"]["text"] = "[BINARY_STRIPPED]"
        
    return entry

def sanitize_har_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for entry in data.get("log", {}).get("entries", []):
        sanitize_har_entry(entry)
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
```
