"""
doctor.py — ENVIX Doctor Module
Diagnoses the dev environment: checks if tools are installed,
detects version info, finds PATH issues, and suggests fixes.
"""

import subprocess
import shutil
from tools import TOOLS



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

    exe = check_cmd[0]
    exe_on_path = shutil.which(exe) is not None

    try:
        result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        raw_output = (result.stdout + result.stderr).strip()
        ran_successfully = result.returncode == 0 and raw_output != ""
    except FileNotFoundError:
        ran_successfully = False
        raw_output = ""
    except subprocess.TimeoutExpired:
        ran_successfully = False
        raw_output = "(timed out)"

    if ran_successfully:
        version_line = raw_output.splitlines()[0]
        return {
            "name":    name,
            "status":  "ok",
            "version": version_line,
            "note":    f"{name} is installed and working.",
            "fix":     None,
        }

    elif exe_on_path and not ran_successfully:
        return {
            "name":    name,
            "status":  "path_issue",
            "version": None,
            "note":    f"{name} binary found on PATH but the command failed. "
                       f"The installation may be corrupted or incomplete.",
            "fix":     f"Try reinstalling via: winget install -e --id {winget_id}",
        }

    else:
        return {
            "name":    name,
            "status":  "missing",
            "version": None,
            "note":    f"{name} is not installed or not on PATH.",
            "fix":     f"Install it with ENVIX, or manually: winget install -e --id {winget_id}",
        }



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



def quick_check(name):
    """
    Fast check: returns True if the tool runs successfully, False otherwise.
    Useful for refreshing status badges without a full scan.
    """
    tool = TOOLS[name]
    try:
        result = subprocess.run(
            tool["check"],
            capture_output=True,
            text=True,
            timeout=8
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0 and output != ""
    except Exception:
        return False
