"""
scanner.py
Pure environment-inspection functions. No Flask/DB dependency here on purpose -
this module should work standalone (e.g. if you later build a CLI or desktop
version, you just import this file).

Every check function returns a dict of the same shape:
{
    "tool": str,
    "found": bool,
    "version": str | None,
    "path": str | None,       # resolved executable path
    "raw": str | None,        # raw command output, for debugging
    "error": str | None
}
"""

import shutil
import subprocess
import os
import re


def _run(cmd_list):
    """Run a command safely, return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return True, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return False, "", "command not found"
    except subprocess.TimeoutExpired:
        return False, "", "command timed out"
    except Exception as e:
        return False, "", str(e)


def check_python():
    exe = shutil.which("python") or shutil.which("python3")
    if not exe:
        return {
            "tool": "python", "found": False, "version": None,
            "path": None, "raw": None, "error": "python not found in PATH"
        }

    ok, out, err = _run([exe, "--version"])
    version = None
    if ok and out:
        match = re.search(r"(\d+\.\d+\.\d+)", out)
        version = match.group(1) if match else out
    return {
        "tool": "python", "found": ok, "version": version,
        "path": exe, "raw": out or err, "error": None if ok else err
    }


def check_pip():
    exe = shutil.which("pip") or shutil.which("pip3")
    if not exe:
        return {
            "tool": "pip", "found": False, "version": None,
            "path": None, "raw": None, "error": "pip not found in PATH"
        }

    ok, out, err = _run([exe, "--version"])
    version = None
    if ok and out:
        match = re.search(r"pip (\d+\.\d+(\.\d+)?)", out)
        version = match.group(1) if match else out
    return {
        "tool": "pip", "found": ok, "version": version,
        "path": exe, "raw": out or err, "error": None if ok else err
    }


def check_git():
    exe = shutil.which("git")
    if not exe:
        return {
            "tool": "git", "found": False, "version": None,
            "path": None, "raw": None, "error": "git not found in PATH"
        }

    ok, out, err = _run([exe, "--version"])
    version = None
    if ok and out:
        match = re.search(r"(\d+\.\d+\.\d+)", out)
        version = match.group(1) if match else out

    # also check user.name / user.email config, since this trips up
    # nearly every beginner on their first commit
    _, name_out, _ = _run([exe, "config", "--global", "user.name"])
    _, email_out, _ = _run([exe, "config", "--global", "user.email"])

    return {
        "tool": "git", "found": ok, "version": version,
        "path": exe, "raw": out or err, "error": None if ok else err,
        "user_name": name_out or None,
        "user_email": email_out or None,
    }


def check_node():
    exe = shutil.which("node")
    if not exe:
        return {
            "tool": "node", "found": False, "version": None,
            "path": None, "raw": None, "error": "node not found in PATH"
        }

    ok, out, err = _run([exe, "--version"])
    version = out.lstrip("v") if ok and out else None
    return {
        "tool": "node", "found": ok, "version": version,
        "path": exe, "raw": out or err, "error": None if ok else err
    }


def check_npm():
    exe = shutil.which("npm")
    if not exe:
        return {
            "tool": "npm", "found": False, "version": None,
            "path": None, "raw": None, "error": "npm not found in PATH"
        }

    ok, out, err = _run([exe, "--version"])
    return {
        "tool": "npm", "found": ok, "version": out if ok else None,
        "path": exe, "raw": out or err, "error": None if ok else err
    }


def check_path_duplicates(tool_name):
    """
    Finds every location of a given executable on PATH, not just the first
    one shutil.which() returns. Multiple installs shadowing each other is a
    classic silent bug (e.g. Anaconda Python vs system Python).
    """
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    found_paths = []
    seen_real_paths = set()
    for directory in path_dirs:
        candidate = os.path.join(directory, tool_name)
        candidates = [candidate, candidate + ".exe"]
        for c in candidates:
            if os.path.isfile(c):
                # resolve symlinks so /bin/python and /usr/bin/python
                # (often the same file via a symlinked directory) don't
                # get double-counted as separate installs
                real = os.path.realpath(c)
                if real not in seen_real_paths:
                    seen_real_paths.add(real)
                    found_paths.append(c)
    return found_paths


def run_full_scan():
    """
    Runs every check and returns one structured result.
    This is the single function app.py calls for /api/scan.
    """
    results = {
        "python": check_python(),
        "pip": check_pip(),
        "git": check_git(),
        "node": check_node(),
        "npm": check_npm(),
    }

    # attach PATH duplicate info for the tools that matter most
    results["python"]["duplicates"] = check_path_duplicates("python") + check_path_duplicates("python3")
    results["node"]["duplicates"] = check_path_duplicates("node")

    return results
