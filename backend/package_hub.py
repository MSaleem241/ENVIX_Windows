"""
package_hub.py — ENVIX Package Hub Logic

This file handles the actual installation work for the Package Hub tab.
It sits between the GUI (which handles display) and the low-level
subprocess helpers (which handle running commands silently).

What this file does:
  1. Checks whether the required language is installed before installing a package
  2. Runs the correct install command (pip, npm, go get) for each package
  3. Installs packages into the project folder selected by the user

What this file does NOT do:
  - Any GUI/widget code (that's all in gui.py)
  - Winget installation of languages (that's installer.py)
  - Any subprocess stuff directly (that's subprocess_helpers.py)
"""

import os
from subprocess_helpers import run_streaming, run_silent
from installer import is_installed, setup_tool
from tools import TOOLS


# ── Language check commands ───────────────────────────────────────────────────
# Maps each package language to the command that checks if it's installed.
# These are the same as the "check" fields in tools.py, just accessed here
# by language name instead of tool name.

LANGUAGE_CHECK = {
    "python": ["python", "--version"],
    "node":   ["node", "-v"],
    "java":   ["java", "-version"],
    "go":     ["go", "version"],
}


def is_language_installed(language):
    """
    Check if the required language runtime is available on the system.

    Returns True if the language can be run, False if it's missing.
    We reuse is_installed() from installer.py — same logic, no duplication.
    """
    check_cmd = LANGUAGE_CHECK.get(language)
    if check_cmd is None:
        # Unknown language — assume it's fine (don't block the install)
        return True
    return is_installed(check_cmd)


def install_language(language, callback=None):
    """
    Install a missing language runtime using the existing installer logic.

    language : "python" | "node" | "java" | "go"
    callback : function(str) for live streaming output to the GUI

    This just calls setup_tool() from installer.py — no new install logic here.
    The language name in packages.py matches the tool name in tools.py, so
    we can pass it directly.
    """
    if language not in TOOLS:
        if callback:
            callback(f"  Unknown language '{language}' — cannot auto-install")
        return False

    print(f"\nInstalling required language: {language}...")
    setup_tool(language, callback=callback)

    # Check again after installing
    return is_language_installed(language)


def install_package(package, install_dir, callback=None):
    """
    Install a single package into the given directory.

    package     : a dict from packages.py (with id, name, language, install_cmd, etc.)
    install_dir : full path to the folder where the package should be installed.
    callback    : function(str) called for each line of output — for live streaming.

    Returns True if the install command ran without error, False otherwise.

    HOW INSTALL WORKS PER LANGUAGE:
      Python:  run `pip install <package>` inside the project's venv.
               If the folder has no venv yet, create one first.
      Node:    run `npm install <package>` inside the project folder
               so it lands in node_modules and is saved to package.json.
      Go:      run `go get <package>` inside the project folder
               so it's added to go.mod.
      Java:    show the Maven/Gradle snippet — full automation would require
               parsing pom.xml/build.gradle which is out of scope for now.
    """
    if callback is None:
        callback = lambda line: None   # no-op if no callback given

    if not install_dir:
        print("No install folder was selected. Package installs must target a project folder.")
        return False

    cmd = package["install_cmd"]

    print(f"Installing {package['name']}...")
    print(f"  Command: {cmd}")
    if install_dir:
        print(f"  Location: {install_dir}")

    # ── Handle Python packages specially: use or create a local venv ──────────
    if package["language"] == "python" and install_dir:
        if not _ensure_python_venv(install_dir, callback):
            print("Could not create or use a Python virtual environment in this folder.")
            return False
        cmd = _get_python_install_cmd(package["install_cmd"], install_dir)

    # ── Run the command ───────────────────────────────────────────────────────
    success = run_streaming(
        cmd,
        callback=callback,
        cwd=install_dir,
        shell=True,     # needed because commands can be strings with flags like -D
        timeout=300,    # 5 minutes should be enough for any package
    )

    if success:
        print(f"\n✓ {package['name']} installed successfully.")
    else:
        print(f"\n✗ {package['name']} installation failed — check the output above.")

    return success


def _ensure_python_venv(folder_path, callback):
    """
    Ensure folder_path has a local Python virtual environment.

    Python packages should not leak into the user's global Python install when
    a project folder was selected. If venv/ does not exist yet, create it first.
    """
    if _get_venv_pip_path(folder_path):
        return True

    print("  No venv found in this folder — creating one now...")
    return run_streaming(
        "python -m venv venv",
        callback=callback,
        cwd=folder_path,
        shell=True,
        timeout=300,
    )


def _get_venv_pip_path(folder_path):
    venv_pip_windows = os.path.join(folder_path, "venv", "Scripts", "pip.exe")
    venv_pip_unix = os.path.join(folder_path, "venv", "bin", "pip")

    if os.path.exists(venv_pip_windows):
        return venv_pip_windows
    if os.path.exists(venv_pip_unix):
        return venv_pip_unix
    return None


def _get_python_install_cmd(base_cmd, folder_path):
    """
    If a virtual environment (venv) exists inside folder_path, use its pip
    instead of the system pip. This keeps packages isolated to the project.

    For example, if the folder has a venv/ directory, we run:
        venv\\Scripts\\pip install <package>    (Windows)
    instead of just:
        pip install <package>                  (system-wide)

    This is a best-practice in Python development — packages should live
    inside a project's venv, not mixed into the global Python installation.
    """
    venv_pip = _get_venv_pip_path(folder_path)
    if not venv_pip:
        return base_cmd

    return base_cmd.replace("pip install", f'"{venv_pip}" install', 1)
