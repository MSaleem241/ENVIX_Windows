"""
project_setup.py — ENVIX Project Folder System

Creates a ready-to-code project folder from a preset (Web Dev, Backend, etc.).
This module:
    1. Installs required languages system-wide (reuses installer.py)
    2. Creates the project folder
    3. Writes starter files (index.html, main.py, etc.)
    4. Runs setup commands INSIDE the folder (npm install, pip install, etc.)

CHANGES IN THIS VERSION:
  - run_in_folder() now uses run_streaming() from subprocess_helpers so:
      a) No CMD window appears when running npm/pip from a compiled .exe
      b) Each line of output streams live to the GUI log panel
  - create_project() and run_in_folder() both accept a 'callback' parameter
    so the GUI can display live progress from npm/pip commands.
"""

import os
from installer import setup_tool
from projects import PROJECTS
from subprocess_helpers import run_streaming


def create_project(preset_name, folder_path, callback=None):
    """
    Build a full project from a preset inside folder_path.

    preset_name : key into PROJECTS (e.g. "web", "backend_python")
    folder_path : full path where the project folder will be created
    callback    : optional function(str) for live output streaming

    Everything this function does shows up as print() messages, which the
    GUI captures via run_with_logged_output() (see gui.py).
    """
    if preset_name not in PROJECTS:
        print("Preset not found")
        return False

    preset = PROJECTS[preset_name]

    # ── Step 1: install required languages system-wide ─────────────────────
    print(f"\nChecking required languages for {preset['label']}...")
    for lang in preset["languages"]:
        # Pass callback through so winget output also streams live
        setup_tool(lang, callback=callback)

    # ── Step 2: create the project folder ───────────────────────────────────
    if os.path.exists(folder_path) and os.listdir(folder_path):
        # Safety check: never overwrite an existing non-empty folder
        print(f"\nFolder already exists and is not empty: {folder_path}")
        print("Please choose an empty folder or a new folder name.")
        return False

    print(f"\nCreating project folder: {folder_path}")
    os.makedirs(folder_path, exist_ok=True)

    # ── Step 3: write starter files ─────────────────────────────────────────
    print("Writing starter files...")
    for relative_path, content in preset["files"].items():
        full_path = os.path.join(folder_path, relative_path)

        # Create any subfolders needed (e.g. "server/" for fullstack preset)
        os.makedirs(os.path.dirname(full_path) or folder_path, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   created {relative_path}")

    # ── Step 4: run setup commands inside the project folder ────────────────
    if preset["commands"]:
        print("Installing project dependencies...")
        all_commands_ok = True
        for command in preset["commands"]:
            print(f"   running: {command}")
            if not run_in_folder(command, folder_path, callback=callback):
                all_commands_ok = False
        if not all_commands_ok:
            print("One or more setup commands failed.")
            return False
    else:
        print("No extra setup needed for this preset.")

    print(f"\n{preset['label']} project ready at:\n  {folder_path}")
    return True


def run_in_folder(command, folder_path, callback=None):
    """
    Run a shell command inside folder_path, streaming output live.

    Uses run_streaming() from subprocess_helpers so:
      - No CMD window appears on screen (fixed for compiled .exe)
      - Each output line is forwarded to callback() in real time

    shell=True is needed because some commands use "cd server && npm install"
    which requires the shell to interpret the && operator.
    """
    # If no callback was given, use a no-op
    if callback is None:
        callback = lambda line: None

    success = run_streaming(
        command,
        callback=callback,
        cwd=folder_path,
        shell=True,         # needed for compound commands with &&
        timeout=300,        # 5 minutes — npm/pip installs can be slow
    )

    if not success:
        # run_streaming already called callback() with any error messages,
        # so just add a summary line for the log
        print(f"   command finished with an error (see output above)")

    return success
