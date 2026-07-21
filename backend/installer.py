"""
installer.py — ENVIX Installation Logic

Handles checking whether tools are installed and installing them via winget.
The GUI calls these functions from background threads (see gui.py) so the
window stays responsive during long installs.

CHANGES IN THIS VERSION:
  - All subprocess calls now use subprocess_helpers.py which:
      1. Hides the CMD window when running as a compiled .exe
      2. Streams winget output line-by-line so the GUI shows live progress
  - install_winget() now accepts an optional 'callback' parameter.
    The GUI passes its log panel's .log() method as the callback, so
    every line winget prints appears in the GUI in real time.
"""

from tools import TOOLS
from stacks import STACKS
from subprocess_helpers import run_silent, run_streaming


# ─── Check if a tool is already installed ────────────────────────────────────

def is_installed(command):
    """
    Run the tool's check command (e.g. ["java", "-version"]) and return
    True if it ran successfully and printed something.

    Uses run_silent() so no CMD window appears even during status checks.

    Note: we check stdout + stderr together because some tools (notably
    java -version) print their version to STDERR instead of STDOUT.
    This was a real bug — see the tutorial for the full story.
    """
    try:
        result = run_silent(command, timeout=10)
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0 and output != ""
    except Exception:
        # Any failure (tool not found, timeout, etc.) means "not installed"
        return False


# ─── Install a package via winget ────────────────────────────────────────────

def install_winget(package_id, callback=None):
    """
    Install a package using Windows Package Manager (winget).

    package_id : the exact winget package ID, e.g. "Python.Python.3"
    callback   : optional function(str) — called with each line of output.
                 The GUI passes log_panel.log here for live streaming.
                 If None, output is just discarded (silent install).

    Returns True on success, False on failure.

    WHY Popen INSTEAD OF subprocess.run():
    subprocess.run() waits for the entire install to finish before
    returning ANYTHING. A 60-second download shows nothing to the user.
    run_streaming() (which uses Popen internally) reads and forwards each
    output line as it arrives, so the GUI shows live download progress.
    """
    # If no callback was given, use a no-op so run_streaming always has
    # something to call — avoids "if callback:" checks inside the helper.
    if callback is None:
        callback = lambda line: None

    success = run_streaming(
        [
            "winget", "install", "-e",
            "--id", package_id,
            "--accept-source-agreements",
            "--accept-package-agreements",
            "--disable-interactivity",  # prevents winget from waiting for user input
        ],
        callback=callback,
        timeout=600,   # 10 minutes — large packages like Docker can be slow
    )
    return success


# ─── Install a single tool (check → install → verify) ────────────────────────

def setup_tool(name, callback=None):
    """
    Check if a tool is installed; install it if not; report the result.

    name     : key from tools.py, e.g. "python", "node", "java"
    callback : optional function(str) for live output — see install_winget()

    This is the function the GUI calls when you click "Install" on a card.
    It prints() progress messages which the GUI captures via its
    run_with_logged_output() wrapper (see gui.py).
    """
    tool = TOOLS[name]

    # Step 1: already installed? Skip immediately.
    if is_installed(tool["check"]):
        print(f"{name} already installed")
        return

    # Step 2: not installed — run the installer with live output streaming
    print(f"Installing {name}...")
    success = install_winget(tool["install"]["id"], callback=callback)

    # Step 3: verify the install actually worked
    if is_installed(tool["check"]):
        print(f"{name} ready")
    else:
        if not success:
            print(f"{name} install failed — check the output above for details")
        else:
            # winget said success but the tool still isn't responding —
            # usually means the user needs to restart so PATH updates
            print(f"{name} installed but not yet on PATH — try restarting ENVIX")


# ─── Install a named stack (a group of tools) ────────────────────────────────

def setup_stack(name, callback=None):
    """
    Install all tools in a named stack (from stacks.py).

    e.g. setup_stack("web") installs node, git, vscode, python in order.
    """
    if name not in STACKS:
        print("Stack not found")
        return

    for tool in STACKS[name]:
        print(f"\nSetting up {tool}...")
        setup_tool(tool, callback=callback)
