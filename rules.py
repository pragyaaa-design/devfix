"""
rules.py
Takes the structured scan result from scanner.py and turns it into a list
of human-readable issues + fix instructions.

Each rule is a function that takes the full scan_result dict and returns
either None (no problem) or an issue dict:
{
    "id": str,
    "tool": str,
    "severity": "high" | "medium" | "low",
    "title": str,
    "explanation": str,
    "fix": str            # exact steps/command, shown to the user
}
"""


def rule_python_missing(scan):
    p = scan["python"]
    if not p["found"]:
        return {
            "id": "python_missing",
            "tool": "python",
            "severity": "high",
            "title": "Python not found",
            "explanation": (
                "No 'python' or 'python3' executable was found anywhere on "
                "your system PATH. This usually means Python isn't installed, "
                "or it was installed but never added to PATH during setup."
            ),
            "fix": (
                "Install Python from python.org and make sure to check "
                "'Add Python to PATH' during installation (Windows), or "
                "run 'sudo apt install python3' (Linux) / 'brew install python' (Mac)."
            ),
        }
    return None


def rule_pip_missing(scan):
    if scan["python"]["found"] and not scan["pip"]["found"]:
        return {
            "id": "pip_missing",
            "tool": "pip",
            "severity": "high",
            "title": "pip not found despite Python being installed",
            "explanation": (
                "Python is installed but pip isn't available on PATH. This "
                "can happen with minimal Python installs or certain Linux "
                "distro packages that split pip into a separate package."
            ),
            "fix": (
                "Run 'python -m ensurepip --upgrade', or on Linux: "
                "'sudo apt install python3-pip'."
            ),
        }
    return None


def rule_python_path_conflict(scan):
    dupes = scan["python"].get("duplicates", [])
    if len(dupes) > 1:
        return {
            "id": "python_path_conflict",
            "tool": "python",
            "severity": "medium",
            "title": f"Multiple Python installations found on PATH ({len(dupes)})",
            "explanation": (
                "More than one Python executable exists on your PATH: "
                + ", ".join(dupes) + ". The one that actually runs when you "
                "type 'python' is whichever comes first in PATH order, which "
                "can silently differ from the one your IDE or pip is using -- "
                "a very common cause of 'works in terminal, fails in IDE' bugs."
            ),
            "fix": (
                "Check PATH order with 'echo $PATH' (Linux/Mac) or "
                "'echo %PATH%' (Windows), and move your intended Python "
                "installation's folder earlier in the list, or uninstall "
                "the one you don't use."
            ),
        }
    return None


def rule_git_missing(scan):
    if not scan["git"]["found"]:
        return {
            "id": "git_missing",
            "tool": "git",
            "severity": "high",
            "title": "Git not found",
            "explanation": "Git isn't installed or isn't on PATH.",
            "fix": (
                "Install from git-scm.com (Windows/Mac) or "
                "'sudo apt install git' (Linux)."
            ),
        }
    return None


def rule_git_identity_missing(scan):
    g = scan["git"]
    if g["found"] and (not g.get("user_name") or not g.get("user_email")):
        return {
            "id": "git_identity_missing",
            "tool": "git",
            "severity": "medium",
            "title": "Git user identity not configured",
            "explanation": (
                "Git is installed but your global user.name and/or "
                "user.email aren't set. This causes commits to fail or "
                "attribute to a placeholder identity."
            ),
            "fix": (
                "Run: git config --global user.name \"Your Name\" and "
                "git config --global user.email \"you@example.com\"."
            ),
        }
    return None


def rule_node_missing(scan):
    if not scan["node"]["found"]:
        return {
            "id": "node_missing",
            "tool": "node",
            "severity": "high",
            "title": "Node.js not found",
            "explanation": "No 'node' executable found on PATH.",
            "fix": "Install from nodejs.org, or use nvm for version management.",
        }
    return None


def rule_npm_missing(scan):
    if scan["node"]["found"] and not scan["npm"]["found"]:
        return {
            "id": "npm_missing",
            "tool": "npm",
            "severity": "high",
            "title": "npm not found despite Node being installed",
            "explanation": (
                "Node.js is present but npm isn't on PATH. This is unusual "
                "since npm normally ships with Node -- likely a broken or "
                "partial install."
            ),
            "fix": "Reinstall Node.js from nodejs.org (npm is bundled with the installer).",
        }
    return None


def rule_node_path_conflict(scan):
    dupes = scan["node"].get("duplicates", [])
    if len(dupes) > 1:
        return {
            "id": "node_path_conflict",
            "tool": "node",
            "severity": "medium",
            "title": f"Multiple Node.js installations found on PATH ({len(dupes)})",
            "explanation": (
                "More than one 'node' executable exists on PATH: "
                + ", ".join(dupes) + ". This is common after installing Node "
                "both directly and via nvm, and causes version-mismatch bugs."
            ),
            "fix": (
                "Use 'nvm ls' to see managed versions and 'nvm use <version>' "
                "to pick one explicitly, or remove the installation you don't need."
            ),
        }
    return None


# All rules run in this order for every scan
ALL_RULES = [
    rule_python_missing,
    rule_pip_missing,
    rule_python_path_conflict,
    rule_git_missing,
    rule_git_identity_missing,
    rule_node_missing,
    rule_npm_missing,
    rule_node_path_conflict,
]


def diagnose(scan_result):
    """Runs every rule against a scan result, returns list of issues found."""
    issues = []
    for rule_fn in ALL_RULES:
        result = rule_fn(scan_result)
        if result is not None:
            issues.append(result)
    return issues
