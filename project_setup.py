import os
import subprocess
from installer import setup_tool
from projects import PROJECTS


def create_project(preset_name, folder_path):
    
    if preset_name not in PROJECTS:
        print("Preset not found")
        return

    preset = PROJECTS[preset_name]

   
    print(f"\nChecking required languages for {preset['label']}...")
    for lang in preset["languages"]:
        setup_tool(lang)

    if os.path.exists(folder_path) and os.listdir(folder_path):
        print(f"\nFolder already exists and is not empty: {folder_path}")
        print("Please choose an empty folder or a new folder name.")
        return

    print(f"\nCreating project folder: {folder_path}")
    os.makedirs(folder_path, exist_ok=True)

    print("Writing starter files...")
    for relative_path, content in preset["files"].items():
        full_path = os.path.join(folder_path, relative_path)

        os.makedirs(os.path.dirname(full_path) or folder_path, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   created {relative_path}")

    if preset["commands"]:
        print("Installing project dependencies...")
        for command in preset["commands"]:
            print(f"   running: {command}")
            run_in_folder(command, folder_path)
    else:
        print("No extra setup needed for this preset.")

    print(f"\n{preset['label']} project ready at:\n  {folder_path}")


def run_in_folder(command, folder_path):
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=folder_path,
            capture_output=True,
            text=True,
            timeout=300,   
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            if detail:
                print(f"      error: {detail.splitlines()[-1]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("      command timed out")
        return False
    except FileNotFoundError:
        print("      command not found — you may need to restart ENVIX "
              "after installing a new language so PATH updates.")
        return False
