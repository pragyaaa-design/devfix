let currentScanId = null;

const scanBtn = document.getElementById("scanBtn");
const verifyBtn = document.getElementById("verifyBtn");
const loading = document.getElementById("loading");
const results = document.getElementById("results");
const toolGrid = document.getElementById("toolGrid");
const issueList = document.getElementById("issueList");

scanBtn.addEventListener("click", runScan);
verifyBtn.addEventListener("click", runVerify);

async function runScan() {
    loading.classList.remove("hidden");
    results.classList.add("hidden");

    const res = await fetch("/api/scan", { method: "POST" });
    const data = await res.json();

    currentScanId = data.scan_id;
    renderTools(data.scan);
    renderIssues(data.issues);

    loading.classList.add("hidden");
    results.classList.remove("hidden");
    verifyBtn.classList.toggle("hidden", data.issue_count === 0);
}

async function runVerify() {
    loading.classList.remove("hidden");

    const res = await fetch(`/api/verify/${currentScanId}`, { method: "POST" });
    const data = await res.json();

    currentScanId = data.new_scan_id;
    issueList.innerHTML = "";

    if (data.resolved.length > 0) {
        const banner = document.createElement("div");
        banner.className = "resolved-banner";
        banner.textContent = `Resolved: ${data.resolved.map(i => i.title).join(", ")}`;
        issueList.appendChild(banner);
    }

    renderIssues(data.new_issues_total, true);
    verifyBtn.classList.toggle("hidden", data.new_issues_total.length === 0);

    loading.classList.add("hidden");
}

function renderTools(scan) {
    toolGrid.innerHTML = "";
    for (const [name, info] of Object.entries(scan)) {
        const card = document.createElement("div");
        card.className = `tool-card ${info.found ? "ok" : "missing"}`;
        card.innerHTML = `
            <div class="tool-name">${name}</div>
            <div class="tool-version">${info.found ? (info.version || "found") : "not found"}</div>
        `;
        toolGrid.appendChild(card);
    }
}

function renderIssues(issues, append = false) {
    if (!append) issueList.innerHTML = "";

    if (issues.length === 0) {
        const p = document.createElement("p");
        p.className = "no-issues";
        p.textContent = "No issues detected.";
        issueList.appendChild(p);
        return;
    }

    for (const issue of issues) {
        const card = document.createElement("div");
        card.className = `issue-card ${issue.severity}`;
        card.innerHTML = `
            <div class="issue-title">${issue.title}</div>
            <div class="issue-explanation">${issue.explanation}</div>
            <div class="issue-fix">${issue.fix}</div>
        `;
        issueList.appendChild(card);
    }
}
