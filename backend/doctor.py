"""
doctor.py — ENVIX Doctor Module

Diagnoses the dev environment: checks if tools are installed, detects version
info, finds PATH issues, and suggests fixes.

CHANGES IN THIS VERSION:
  - All subprocess.run() calls replaced with run_silent() from
    subprocess_helpers.py, which hides CMD windows when running as .exe.
  - The diagnostic logic itself is unchanged.
"""

import shutil
from tools import TOOLS
from subprocess_helpers import run_silent


# ─── Individual tool diagnosis ────────────────────────────────────────────────

def check_tool(name):
    """
    Check a single tool and return a diagnosis dict:
      - status:  "ok" | "missing" | "path_issue"
      - version: version string if found, else None
      - note:    human-readable description of the finding
      - fix:     what to do about it (if anything)
    """
    tool = TOOLS[name]
    check_cmd = tool["check"]
    winget_id = tool["install"]["id"]

    # 1. Can the OS find the executable at all?
    # shutil.which() searches PATH — same as typing the command name yourself
    exe = check_cmd[0]
    exe_on_path = shutil.which(exe) is not None

    # 2. Can we actually run it and get output?
    # run_silent() is subprocess.run() + hidden CMD window flag
    try:
        result = run_silent(check_cmd, timeout=10)
        # Some tools (like java -version) write to stderr instead of stdout —
        # checking both catches version strings regardless of where they land
        raw_output = (result.stdout + result.stderr).strip()
        ran_successfully = result.returncode == 0 and raw_output != ""
    except FileNotFoundError:
        ran_successfully = False
        raw_output = ""
    except Exception:
        ran_successfully = False
        raw_output = ""

    # ── Determine status: three outcomes, not just two ────────────────────────
    if ran_successfully:
        # Tool works perfectly — first line of output is the version
        version_line = raw_output.splitlines()[0]
        return {
            "name":    name,
            "status":  "ok",
            "version": version_line,
            "note":    f"{name} is installed and working.",
            "fix":     None,
        }

    elif exe_on_path and not ran_successfully:
        # Binary exists on PATH but running it failed — likely a broken install
        # This is more useful than just "missing" — the fix is reinstall, not install
        return {
            "name":    name,
            "status":  "path_issue",
            "version": None,
            "note":    f"{name} binary found on PATH but the command failed. "
                       f"The installation may be corrupted or incomplete.",
            "fix":     f"Try reinstalling via: winget install -e --id {winget_id}",
        }

    else:
        # Completely missing — not on PATH at all
        return {
            "name":    name,
            "status":  "missing",
            "version": None,
            "note":    f"{name} is not installed or not on PATH.",
            "fix":     f"Install it with ENVIX, or manually: winget install -e --id {winget_id}",
        }


# ─── Full system scan ─────────────────────────────────────────────────────────

def run_doctor():
    """
    Run a diagnosis across ALL tools defined in tools.py.
    Returns a list of result dicts (one per tool), plus a summary dict.
    """
    results = []
    for name in TOOLS:
        result = check_tool(name)
        results.append(result)

    ok_count      = sum(1 for r in results if r["status"] == "ok")
    missing_count = sum(1 for r in results if r["status"] == "missing")
    broken_count  = sum(1 for r in results if r["status"] == "path_issue")

    summary = {
        "total":   len(results),
        "ok":      ok_count,
        "missing": missing_count,
        "broken":  broken_count,
    }

    return results, summary


# ─── Quick single-tool check (used by the GUI's status badges) ────────────────

def quick_check(name):
    """
    Fast True/False check — is this tool installed and working?
    Used to update the small status badges on tool cards without a full scan.
    """
    tool = TOOLS[name]
    try:
        result = run_silent(tool["check"], timeout=8)
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0 and output != ""
    except Exception:
        return False
