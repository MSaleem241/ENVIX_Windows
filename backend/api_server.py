"""
api_server.py — ENVIX Python Backend Server

This is a thin FastAPI wrapper around the existing ENVIX logic.
Tauri spawns it as a sidecar on app startup. The React frontend
communicates with it via HTTP on localhost:39291.

WHY HTTP INSTEAD OF TAURI COMMANDS:
  Keeping Python as a standalone HTTP server means:
  - Zero Rust bindings to maintain
  - Python backend is independently testable with curl
  - Full SSE streaming support for live install progress

STREAMING (SSE):
  Long-running installs use Server-Sent Events so each log line
  arrives at the frontend in real time — same as the old callback system.
"""

import sys
import os
import json
import queue
import threading
import builtins
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ── Import existing ENVIX logic (unchanged Python files) ──────────────────
from doctor import run_doctor, quick_check
from installer import setup_tool, is_installed
from tools import TOOLS
from packages import PACKAGES, PACKAGES_BY_ID
from package_hub import is_language_installed, install_language, install_package
from project_setup import create_project
from projects import PROJECTS

# ── App setup ─────────────────────────────────────────────────────────────
app = FastAPI(title="ENVIX Backend API", version="1.1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["tauri://localhost", "http://localhost:1420", "http://localhost:39291"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ────────────────────────────────────────────────────────
class InstallPackageRequest(BaseModel):
    package_id: str
    install_dir: Optional[str] = None

class CreateProjectRequest(BaseModel):
    preset_name: str
    folder_path: str


# ── SSE streaming helper ──────────────────────────────────────────────────
def make_sse_stream(work_fn):
    """
    Run work_fn(callback) in a background thread.
    Every print() or callback(line) call becomes an SSE event.
    Frontend EventSource reads these and updates the Output Console live.
    """
    msg_queue = queue.Queue()
    DONE = object()

    def run():
        original_print = builtins.print

        def captured_print(*args, **kwargs):
            msg = " ".join(str(a) for a in args)
            msg_queue.put({"type": "log", "message": msg})

        def streaming_callback(line: str):
            msg_queue.put({"type": "progress", "message": line})

        builtins.print = captured_print
        try:
            result = work_fn(streaming_callback)
            if result is False:
                msg_queue.put({"type": "error", "message": "Operation failed — check the output above."})
        except Exception as e:
            msg_queue.put({"type": "error", "message": str(e)})
        finally:
            builtins.print = original_print
            msg_queue.put(DONE)

    threading.Thread(target=run, daemon=True).start()

    def generate():
        while True:
            try:
                item = msg_queue.get(timeout=30)
            except queue.Empty:
                yield 'data: {"type":"timeout"}\n\n'
                break
            if item is DONE:
                yield 'data: {"type":"done"}\n\n'
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Health check ──────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.1.0"}


# ── Tools ─────────────────────────────────────────────────────────────────
@app.get("/api/tools")
def get_tools():
    """Return all tools with current install status."""
    result = []
    for name, data in TOOLS.items():
        result.append({
            "name": name,
            "category": data.get("category", "tool"),
            "installed": is_installed(data["check"]),
            "winget_id": data["install"]["id"],
        })
    return {"tools": result}

@app.get("/api/tools/{name}/status")
def get_tool_status(name: str):
    if name not in TOOLS:
        raise HTTPException(404, f"Tool '{name}' not found")
    return {"name": name, "installed": quick_check(name)}

@app.post("/api/tools/{name}/install")
def install_tool_stream(name: str):
    """Install a tool, streaming output via SSE."""
    if name not in TOOLS:
        raise HTTPException(404, f"Tool '{name}' not found")
    return make_sse_stream(lambda cb: setup_tool(name, callback=cb))


# ── Doctor ────────────────────────────────────────────────────────────────
@app.get("/api/doctor/scan")
def doctor_scan():
    """Full environment diagnostic — returns JSON (not streamed, fast)."""
    results, summary = run_doctor()
    return {"results": results, "summary": summary}


# ── Packages ──────────────────────────────────────────────────────────────
@app.get("/api/packages")
def get_packages(language: Optional[str] = None, search: Optional[str] = None):
    """Return packages with optional language filter and search."""
    result = PACKAGES
    if language:
        result = [p for p in result if p["language"] == language]
    if search:
        q = search.lower()
        result = [p for p in result
                  if q in p["name"].lower()
                  or q in p["category"].lower()
                  or q in p["description"].lower()]
    return {"packages": result, "total": len(result)}

@app.post("/api/packages/install")
def install_pkg_stream(request: InstallPackageRequest):
    """Install a package, streaming output via SSE."""
    pkg = PACKAGES_BY_ID.get(request.package_id)
    if not pkg:
        raise HTTPException(404, f"Package '{request.package_id}' not found")
    return make_sse_stream(lambda cb: install_package(pkg, request.install_dir, callback=cb))


# ── Project Presets ───────────────────────────────────────────────────────
@app.get("/api/presets")
def get_presets():
    return {"presets": [
        {"id": k, "label": v["label"], "desc": v["desc"],
         "languages": v["languages"], "file_count": len(v["files"])}
        for k, v in PROJECTS.items()
    ]}

@app.post("/api/presets/create")
def create_project_stream(request: CreateProjectRequest):
    """Create a project from a preset, streaming output via SSE."""
    if request.preset_name not in PROJECTS:
        raise HTTPException(404, f"Preset '{request.preset_name}' not found")
    return make_sse_stream(
        lambda cb: create_project(request.preset_name, request.folder_path, callback=cb)
    )


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("ENVIX_PORT", 39291))
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)
