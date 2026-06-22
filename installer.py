import subprocess
from tools import TOOLS 
from stacks import STACKS 


def is_installed(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0 and output != ""
    except:
        return False
    


def install_winget(package_id):
    try:
        subprocess.run([
            "winget", "install", "-e",
            "--id", package_id,
            "--accept-source-agreements",
            "--accept-package-agreements"
        ], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        if detail:
            print(f"   winget error: {detail.splitlines()[-1]}")
        return False 
    

def setup_tool(name):
    tool = TOOLS[name]

    if is_installed(tool["check"]):
        print(f"{name} already installed")
        return
    
    print(f"Installing {name}...")

    install_winget(tool["install"]["id"])

    if is_installed(tool["check"]):
        print(f"{name} ready")
    else:
        print(f"{name} install failed")



def setup_stack(name):
    if name not in STACKS:
        print("Stack not found")
        return
    
    for tool in STACKS[name]:
        print(f"\nSetting up {tool}...")
        setup_tool(tool)