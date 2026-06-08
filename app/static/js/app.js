/* ============================================================
   THEME INITIALISATION
   ============================================================ */

// Default to dark mode on first load
if (!localStorage.getItem("theme")) {
    localStorage.setItem("theme", "dark");
}

// Apply saved theme
document.body.classList.toggle(
    "dark-mode",
    localStorage.getItem("theme") === "dark"
);

// Update theme button label
const themeBtn = document.querySelector(".theme-toggle");
themeBtn.textContent = document.body.classList.contains("dark-mode")
    ? "☀️ Light Mode"
    : "🌙 Dark Mode";


/* ============================================================
   THEME TOGGLE
   ============================================================ */

function toggleTheme() {
    const isDark = document.body.classList.toggle("dark-mode");
    themeBtn.textContent = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
    localStorage.setItem("theme", isDark ? "dark" : "light");
}


/* ============================================================
   THINKING INDICATOR
   ============================================================ */

function showThinking() {
    document.getElementById("thinking").style.display = "flex";
}

function hideThinking() {
    const t = document.getElementById("thinking");
    t.style.display = "none";
    void t.offsetHeight; // reset animation
}


/* ============================================================
   CHAT MESSAGE RENDERING
   ============================================================ */

function addMessage(role, text) {
    const box = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = `message ${role}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = marked.parse(text);

    msg.appendChild(bubble);
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
}

function renderChatMessage(agentResponse) {
    const { summary, insights } = agentResponse;

    const box = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = "message assistant";

    msg.innerHTML = `
        <div class="bubble">
            <div class="summary">${summary}</div>
            <ul class="insights">
                ${insights.map(i => `<li>${i}</li>`).join("")}
            </ul>
        </div>
    `;

    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
}

/* ============================================================
   Content Toggles (SQL, Data Preview)
   ============================================================ */

// SQL toggle
document.getElementById("toggle-sql").addEventListener("click", () => {
    const sqlBox = document.getElementById("sql-box");
    const btn = document.getElementById("toggle-sql");

    const hidden = sqlBox.classList.toggle("hidden");
    btn.textContent = hidden ? "Show SQL" : "Hide SQL";
});

// Preview toggle
document.getElementById("toggle-preview").addEventListener("click", () => {
    const content = document.getElementById("data-preview-content");
    const btn = document.getElementById("toggle-preview");

    const hidden = content.classList.toggle("hidden");
    btn.textContent = hidden ? "Show Preview" : "Hide Preview";
});

document.getElementById("toggle-analysis").addEventListener("click", () => {
    const panel = document.getElementById("analysis-details");
    const btn = document.getElementById("toggle-analysis");

    const hidden = panel.classList.toggle("hidden");
    btn.textContent = hidden ? "Show Analysis Details" : "Hide Analysis Details";
});



/* ============================================================
   SQL EXTRACTION FROM HISTORY
   ============================================================ */

function extractLatestSQL(history) {
    for (let i = history.length - 1; i >= 0; i--) {
        const msg = history[i];

        if (msg.role === "tool") {
            try {
                const data = JSON.parse(msg.content);

                if (data.columns && data.rows) {
                    return data;
                }
            } catch (e) {
                console.error("Failed to parse tool content", e);
            }
        }
    }
    return null;
}


/* ============================================================
   RESULTS TABLE RENDERING
   ============================================================ */

function renderResultsTable(data) {
    const box = document.getElementById("results-box");
    box.innerHTML = "";

    if (!data || !data.rows || data.rows.length === 0) {
        box.textContent = "No results.";
        return;
    }

    const table = document.createElement("table");

    // Header
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    data.columns.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body
    const tbody = document.createElement("tbody");

    data.rows.forEach(row => {
        const tr = document.createElement("tr");
        row.forEach(val => {
            const td = document.createElement("td");
            td.textContent = val;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    box.appendChild(table);
}

/* ============================================================
   DATA PANEL RENDERING (df_name, columns, preview, row_count)
   ============================================================ */

function renderDataPanel(finalJson) {
    const resultsBox = document.getElementById("results-box");

    resultsBox.innerHTML = `
        <p><strong>df_name:</strong> ${finalJson.df_name}</p>
        <p><strong>Rows:</strong> ${finalJson.row_count}</p>
        <p><strong>Columns:</strong> ${finalJson.columns.join(", ")}</p>
    `;

    // Render preview table
    if (finalJson.preview && finalJson.preview.length > 0) {
        const table = document.createElement("table");

        // Header
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");

        finalJson.columns.forEach(col => {
            const th = document.createElement("th");
            th.textContent = col;
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Body
        const tbody = document.createElement("tbody");

        finalJson.preview.forEach(row => {
            const tr = document.createElement("tr");
            row.forEach(val => {
                const td = document.createElement("td");
                td.textContent = val;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        resultsBox.appendChild(table);
    }
}

function renderAnalysisDetails(result) {
    const panel = document.getElementById("analysis-details");

    if (!result || !result.analysis_type) {
        panel.innerHTML = "<p>No analysis available.</p>";
        return;
    }

    const type = result.analysis_type;
    const analysis = result.analysis_result;

    // ============================
    // ANOMALY DETECTION
    // ============================
    if (type === "anomaly_detection") {
        if (!analysis.anomalies || analysis.anomalies.length === 0) {
            panel.innerHTML = "<p>No anomalies detected.</p>";
            return;
        }

        let html = "<h3>Anomalies</h3><table><tr>";

        // Table headers
        const headers = Object.keys(analysis.anomalies[0]);
        headers.forEach(h => html += `<th>${h}</th>`);
        html += "</tr>";

        // Rows
        analysis.anomalies.forEach(a => {
            html += "<tr>";
            headers.forEach(h => html += `<td>${a[h]}</td>`);
            html += "</tr>";
        });

        html += "</table>";
        panel.innerHTML = html;
        return;
    }

    // ============================
    // SUMMARY STATISTICS
    // ============================
    if (type === "summary_stats") {
        const metrics = analysis.metrics;
        if (!metrics || Object.keys(metrics).length === 0) {
            panel.innerHTML = "<p>No summary statistics available.</p>";
            return;
        }

        let html = "<h3>Summary Statistics</h3>";

        for (const col in metrics) {
            html += `<h4>${col}</h4><table>`;
            html += "<tr><th>Metric</th><th>Value</th></tr>";

            const stats = metrics[col];
            for (const key in stats) {
                html += `<tr><td>${key}</td><td>${stats[key]}</td></tr>`;
            }

            html += "</table>";
        }

        panel.innerHTML = html;
        return;
    }

    // ============================
    // CORRELATION MATRIX
    // ============================
    if (type === "correlation") {
        const corr = analysis.correlation;
        if (!corr) {
            panel.innerHTML = "<p>No correlation data available.</p>";
            return;
        }

        let html = "<h3>Correlation Matrix</h3><table>";

        const cols = Object.keys(corr);
        html += "<tr><th></th>" + cols.map(c => `<th>${c}</th>`).join("") + "</tr>";

        cols.forEach(row => {
            html += `<tr><th>${row}</th>`;
            cols.forEach(col => html += `<td>${corr[row][col]}</td>`);
            html += "</tr>";
        });

        html += "</table>";
        panel.innerHTML = html;
        return;
    }

    // ============================
    // REGRESSION COEFFICIENTS
    // ============================
    if (type === "regression") {
        const coeffs = analysis.regression_coefficients;
        if (!coeffs || coeffs.length === 0) {
            panel.innerHTML = "<p>No regression coefficients available.</p>";
            return;
        }

        let html = "<h3>Regression Coefficients</h3><table>";
        html += "<tr><th>Feature</th><th>Coefficient</th></tr>";

        coeffs.forEach(c => {
            html += `<tr><td>${c.feature}</td><td>${c.value}</td></tr>`;
        });

        html += "</table>";
        panel.innerHTML = html;
        return;
    }

    // Fallback
    panel.innerHTML = "<p>No analysis details available.</p>";
}



/* ============================================================
   CLEAN JSON FROM MARKDOWN FENCES
   ============================================================ */

function stripMarkdownFences(text) {
    if (!text) return text;

    return text
        .replace(/```json/gi, "")
        .replace(/```/g, "")
        .trim();
}

/* ============================================================
   CHART PANEL HELPERS
   ============================================================ */

function showChartLoading() {
    document.getElementById("chart-loading").classList.remove("hidden");
    document.getElementById("chart-image").classList.add("hidden");
}

function hideChartLoading() {
    document.getElementById("chart-loading").classList.add("hidden");
}

function renderChart(imagePath) {
    const img = document.getElementById("chart-image");

    if (!imagePath) {
        img.classList.add("hidden");
        return;
    }

    // Normalize Windows backslashes → forward slashes
    let normalized = imagePath.replace(/\\/g, "/");

    // Strip leading "app/" if present
    normalized = normalized.replace(/^app\//, "");

    // Prepend correct relative path
    const finalPath = "../" + normalized;

    img.src = finalPath + "?cb=" + Date.now(); // cache-bust
    img.classList.remove("hidden");
}



/* ============================================================
   SEND MESSAGE → BACKEND
   ============================================================ */

function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage("user", text);
    input.value = "";

    showThinking();

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
    })
        .then(res => res.json())
        .then(data => {
            hideThinking();

            const raw = data.agent_response;
            const cleaned = stripMarkdownFences(raw);

            let finalJson = null;

            try {
                finalJson = JSON.parse(cleaned);
            } catch (e) {
                console.error("JSON parse failed:", cleaned);
                addMessage("assistant", "⚠️ The assistant returned invalid JSON.");
                return;
            }

            // Render assistant summary + insights
            renderChatMessage(finalJson);

            // Update SQL panel
            document.getElementById("sql-box").textContent =
                finalJson.sql || "No SQL executed.";

            // Render Data Panel
            renderDataPanel(finalJson);

            // Render Analysis Panel
            renderAnalysisDetails(finalJson);

            // Handle chart logic
            if (finalJson.analysis_result && finalJson.analysis_result.image_path) {
                showChartLoading();
                renderChart(finalJson.analysis_result.image_path);
                hideChartLoading();
            } else {
                document.getElementById("chart-image").classList.add("hidden");
                document.getElementById("chart-loading").classList.add("hidden");
            }
        })
}


/* ============================================================
   CLEAR CHAT
   ============================================================ */

document.getElementById("clear-chat-btn").addEventListener("click", async () => {
    if (!confirm("Clear the entire chat history?")) return;

    await fetch("/clear_chat", { method: "POST" });

    document.getElementById("chat-box").innerHTML = "";
    document.getElementById("user-input").value = "";
    document.getElementById("sql-box").innerHTML = "";
    document.getElementById("results-box").innerHTML = "";

    setTimeout(() => window.location.reload(), 50);
});
