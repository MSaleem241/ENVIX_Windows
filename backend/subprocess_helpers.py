"""
subprocess_helpers.py — ENVIX Subprocess Utilities

Two problems this file solves:

1. SILENT BACKGROUND INSTALLATION
   When ENVIX is compiled to an .exe with PyInstaller, running winget or
   any other console-mode program pops up a black Command Prompt window.
   This looks unprofessional. The fix is STARTUPINFO — a Windows-only
   structure that tells the OS "launch this child process with its window
   hidden." On non-Windows systems (Linux, Mac) it is simply ignored.

2. LIVE OUTPUT STREAMING
   The old code used subprocess.run(...) which waits until the entire
   process finishes before returning. Users saw nothing for 30–60 seconds.
   The new approach uses subprocess.Popen which lets us READ the output
   LINE BY LINE as the process runs, so we can stream each line directly
   into the GUI's log panel in real time.

Both helpers live here so installer.py, project_setup.py, and doctor.py
all get the same behaviour without copy-pasting the same code everywhere.
"""

import sys
import os
import time
import subprocess
import ctypes
from ctypes import wintypes

# Windows process tree tracking structures and helpers
if sys.platform == "win32":
    TH32CS_SNAPPROCESS = 0x00000002

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_wchar * 260),
        ]

    def get_process_path(pid):
        # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not h:
            return None
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                return buf.value
        except Exception:
            pass
        finally:
            ctypes.windll.kernel32.CloseHandle(h)
        return None

    def get_active_processes():
        processes = []
        hProcessSnap = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if hProcessSnap == -1:
            return processes

        try:
            pe32 = PROCESSENTRY32W()
            pe32.dwSize = ctypes.sizeof(PROCESSENTRY32W)

            if ctypes.windll.kernel32.Process32FirstW(hProcessSnap, ctypes.byref(pe32)):
                while True:
                    pid = pe32.th32ProcessID
                    ppid = pe32.th32ParentProcessID
                    name = pe32.szExeFile
                    path = get_process_path(pid)
                    processes.append({
                        "pid": pid,
                        "ppid": ppid,
                        "name": name,
                        "path": path
                    })
                    if not ctypes.windll.kernel32.Process32NextW(hProcessSnap, ctypes.byref(pe32)):
                        break
        finally:
            ctypes.windll.kernel32.CloseHandle(hProcessSnap)
        return processes

    def find_installer_processes(winget_pid, tracked_pids, winget_temp_dir):
        new_found = False
        pid_map = {}
        try:
            processes = get_active_processes()
        except Exception:
            return False, pid_map

        for p in processes:
            pid_map[p["pid"]] = p

        added_any = True
        while added_any:
            added_any = False
            for pid, p in pid_map.items():
                if pid in tracked_pids:
                    continue
                
                is_part_of_tree = False
                # Check 1: starts with winget temp dir
                if p["path"] and p["path"].lower().startswith(winget_temp_dir):
                    is_part_of_tree = True
                # Check 2: parent is winget
                elif p["ppid"] == winget_pid:
                    is_part_of_tree = True
                # Check 3: parent is already tracked
                elif p["ppid"] in tracked_pids:
                    is_part_of_tree = True
                    
                if is_part_of_tree:
                    tracked_pids.add(pid)
                    added_any = True
                    new_found = True
                    
        return new_found, pid_map


def get_startupinfo():
    """
    Returns a Windows STARTUPINFO object that hides the child process window.

    WHY THIS IS NEEDED:
    On Windows, every console-mode program (winget, npm, pip, etc.) normally
    opens its own black CMD window when launched from a GUI application.
    Setting dwFlags + wShowWindow = SW_HIDE tells Windows to create that
    window but keep it invisible — the process still runs normally, the user
    just never sees the CMD flash.

    On Linux and Mac, subprocess.STARTUPINFO does not exist at all, so we
    return None. Every place that uses this checks for None before passing
    it to subprocess.
    """
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        # STARTF_USESHOWWINDOW = "pay attention to the wShowWindow field"
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # SW_HIDE = 0: create the window but keep it hidden
        si.wShowWindow = subprocess.SW_HIDE
        return si
    # On non-Windows systems, return None — callers check for this
    return None


def run_streaming(command, callback, cwd=None, shell=False, timeout=600):
    """
    Run a command and call callback(line) for every line of output it produces,
    in real time — instead of waiting for the whole thing to finish.

    This is the core of the live progress feature. Instead of:
        result = subprocess.run(...)   <- blocks until done, then returns
    we use:
        proc = subprocess.Popen(...)   <- starts the process
        for line in proc.stdout: ...   <- read each line as it arrives

    Arguments:
        command  : list of strings like ["winget", "install", "--id", "..."]
                   OR a plain string if shell=True
        callback : function(str) — called once per output line.
                   The GUI passes log_panel.log here so each line appears
                   in the output panel immediately.
        cwd      : working directory for the command (used by project_setup.py)
        shell    : True if command is a string with && etc. (used by project_setup.py)
        timeout  : seconds before we give up (default 10 minutes)

    Returns:
        True  if the process exited with return code 0 (success)
        False if it failed or timed out
    """
    # Build kwargs dict — only add startupinfo if we got one (i.e. on Windows)
    si = get_startupinfo()
    kwargs = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # merge stderr into stdout — one stream to read
        text=True,
        bufsize=1,                 # line-buffered: give us each line as it arrives
        cwd=cwd,
        shell=shell,
    )
    if si is not None:
        kwargs["startupinfo"] = si

    try:
        if sys.platform == "win32":
            callback("   [ENVIX] Launching installer...")

        proc = subprocess.Popen(command, **kwargs)

        if sys.platform == "win32":
            callback(f"   [ENVIX] Installer started (PID: {proc.pid})")
            callback("   [ENVIX] Waiting for installer...")
            callback("   [ENVIX] Streaming output...")

        # Keep track of the process tree on Windows
        winget_temp_dir = os.path.expandvars(r"%TEMP%\WinGet").lower()
        tracked_pids = {proc.pid}
        tracked_handles = {}
        exit_codes = {}

        last_scan_time = 0

        # Read output line by line as the process runs.
        for raw_line in proc.stdout:
            line = raw_line.rstrip()   # remove trailing newline/whitespace
            if line:                   # skip blank lines
                callback(line)

            if sys.platform == "win32":
                # Scan child processes at most once per second during output streaming
                current_time = time.time()
                if current_time - last_scan_time > 1.0:
                    new_found, pid_map = find_installer_processes(proc.pid, tracked_pids, winget_temp_dir)
                    if new_found:
                        for pid in list(tracked_pids):
                            if pid not in tracked_handles and pid != proc.pid:
                                # Open process with SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION
                                h = ctypes.windll.kernel32.OpenProcess(0x00100000 | 0x1000, False, pid)
                                if h:
                                    tracked_handles[pid] = h
                                    name = pid_map[pid]["name"] if pid in pid_map else "Unknown"
                                    callback(f"   [ENVIX] Detected installer process: {name} (PID: {pid})")
                    last_scan_time = current_time

        # Wait for the process to fully finish and get the exit code
        if sys.platform == "win32":
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass

            last_log_time = time.time()
            while True:
                # 1. Scan for any new child/grandchild processes
                new_found, pid_map = find_installer_processes(proc.pid, tracked_pids, winget_temp_dir)
                if new_found:
                    for pid in list(tracked_pids):
                        if pid not in tracked_handles and pid != proc.pid:
                            h = ctypes.windll.kernel32.OpenProcess(0x00100000 | 0x1000, False, pid)
                            if h:
                                tracked_handles[pid] = h
                                name = pid_map[pid]["name"] if pid in pid_map else "Unknown"
                                callback(f"   [ENVIX] Detected installer process: {name} (PID: {pid})")

                # 2. Get list of all currently running process PIDs to detect exits of processes
                try:
                    all_procs = get_active_processes()
                    running_pids = {p["pid"] for p in all_procs}
                except Exception:
                    running_pids = set()

                active_tracked = tracked_pids.intersection(running_pids)

                # 3. Check status of handles we successfully opened
                active_handles = {}
                for pid, h in list(tracked_handles.items()):
                    exit_code = wintypes.DWORD()
                    if ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(exit_code)):
                        if exit_code.value == 259:  # STILL_ACTIVE
                            active_handles[pid] = h
                        else:
                            exit_codes[pid] = exit_code.value
                            ctypes.windll.kernel32.CloseHandle(h)
                            callback(f"   [ENVIX] Installer process (PID: {pid}) exited with code {exit_code.value}")
                    else:
                        ctypes.windll.kernel32.CloseHandle(h)
                        callback(f"   [ENVIX] Lost track of installer process (PID: {pid})")
                tracked_handles = active_handles

                # 4. Check if we should stop waiting
                winget_running = proc.poll() is None
                active_installer_pids = {pid for pid in active_tracked if pid != proc.pid}

                if not winget_running and len(active_installer_pids) == 0 and len(tracked_handles) == 0:
                    break

                if time.time() - last_log_time > 10.0:
                    callback("   [ENVIX] Installer still running...")
                    last_log_time = time.time()

                time.sleep(1.0)

            # Close any remaining handles
            for pid, h in tracked_handles.items():
                ctypes.windll.kernel32.CloseHandle(h)

            callback("   [ENVIX] Installer exited.")

            # Check overall status
            winget_success = proc.returncode == 0
            installer_success = True
            for pid, code in exit_codes.items():
                if code not in (0, 3010):
                    callback(f"   [ENVIX] Installer process (PID: {pid}) failed with exit code {code}")
                    installer_success = False

            overall_success = winget_success and installer_success
            callback(f"   [ENVIX] Exit code: {proc.returncode if overall_success else (proc.returncode or 1)}")
            return overall_success

        else:
            # Non-Windows systems: standard wait
            proc.wait(timeout=timeout)
            return proc.returncode == 0

    except subprocess.TimeoutExpired:
        proc.kill()
        callback("   (command timed out and was stopped)")
        return False

    except FileNotFoundError:
        # The executable wasn't found at all — usually means PATH isn't set up yet
        callback("   command not found — try restarting ENVIX after installing a new language")
        return False

    except Exception as e:
        callback(f"   unexpected error: {e}")
        return False


def run_silent(command, timeout=15):
    """
    Run a command silently (no output capture needed — just True/False result).
    Used for quick checks like "is this tool installed?" where we don't need
    to stream the output to the GUI.

    This replaces the basic subprocess.run() calls in is_installed() and
    quick_check() — same behaviour, just with the hidden-window flag added.
    """
    si = get_startupinfo()
    kwargs = dict(
        capture_output=True,   # capture stdout + stderr so nothing leaks to screen
        text=True,
        timeout=timeout,
    )
    if si is not None:
        kwargs["startupinfo"] = si

    return subprocess.run(command, **kwargs)
