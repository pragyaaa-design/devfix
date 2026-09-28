"""
app.py
Flask backend. Thin layer on top of scanner.py + rules.py -- this file should
mostly just wire HTTP requests to those pure functions and handle JSON in/out.
"""

from flask import Flask, jsonify, render_template, request
import scanner
import rules
import database

app = Flask(__name__)
database.init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def api_scan():
    """
    Runs a full environment scan, diagnoses issues, saves to history,
    and returns everything to the frontend.
    """
    scan_result = scanner.run_full_scan()
    issues = rules.diagnose(scan_result)
    scan_id = database.save_scan(scan_result, issues)

    return jsonify({
        "scan_id": scan_id,
        "scan": scan_result,
        "issues": issues,
        "issue_count": len(issues),
    })


@app.route("/api/verify/<int:scan_id>", methods=["POST"])
def api_verify(scan_id):
    """
    Re-runs the scan and compares against a previous scan_id's issues,
    reporting which specific issues are now resolved.
    """
    previous = database.get_scan_by_id(scan_id)
    if previous is None:
        return jsonify({"error": "scan_id not found"}), 404

    new_scan = scanner.run_full_scan()
    new_issues = rules.diagnose(new_scan)
    new_issue_ids = {issue["id"] for issue in new_issues}

    resolved = [
        issue for issue in previous["issues_json"]
        if issue["id"] not in new_issue_ids
    ]
    still_present = [
        issue for issue in new_issues
        if issue["id"] in {i["id"] for i in previous["issues_json"]}
    ]
    new_scan_id = database.save_scan(new_scan, new_issues)

    return jsonify({
        "new_scan_id": new_scan_id,
        "resolved": resolved,
        "still_present": still_present,
        "new_issues_total": new_issues,
    })


@app.route("/api/history")
def api_history():
    return jsonify(database.get_history(limit=20))


if __name__ == "__main__":
    print("DevFix running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
