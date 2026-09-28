# DevFix

A local diagnostic tool that scans your development environment (Python, pip, Git, Node.js, npm), detects common configuration issues, and tells you exactly how to fix them.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## How it works

1. Click **Run Scan** — the backend runs `subprocess` calls to inspect installed tools, versions, and PATH configuration.
2. Detected issues are matched against a rule set (`rules.py`) and shown with plain-language explanations and exact fix commands.
3. After applying a fix, click **Re-scan & Verify Fixes** to confirm the issue is resolved.

## Project structure

```
devfix/
  app.py            Flask routes (thin layer, no diagnostic logic)
  scanner.py         Pure environment-inspection functions
  rules.py           Diagnostic rules, separate from scanning logic
  database.py        SQLite scan history
  templates/          Frontend HTML
  static/             CSS + JS
```

## Adding a new check

1. Add a `check_x()` function to `scanner.py`, returning the standard result dict shape.
2. Add it to `run_full_scan()`.
3. Add one or more `rule_x()` functions to `rules.py` and register them in `ALL_RULES`.

No other files need to change — this separation is intentional so the rule set can grow without touching the scanner or the Flask routes.

## Currently checked

- Python: installed, version, pip availability, PATH duplicates
- Git: installed, version, global user.name/user.email configured
- Node.js: installed, version, npm availability, PATH duplicates

## Roadmap ideas

- Paste-an-error mode: user pastes a raw stack trace, backend correlates it against the current scan state (this is where an LLM API call would actually add value, grounded in real system facts instead of guessing)
- GCC/MinGW checks
- Safe, reversible auto-fix for low-risk issues (e.g. session-only PATH additions)
