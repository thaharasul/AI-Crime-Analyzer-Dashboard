const CHART_COLORS = ["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899"];

async function fetchJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Request failed: ${url}`);
    return res.json();
}

async function loadSummary() {
    const data = await fetchJSON("/api/dashboard/summary");
    document.getElementById("stat-total").textContent = data.total_crimes;
    document.getElementById("stat-solved").textContent = data.solved_cases;
    document.getElementById("stat-pending").textContent = data.pending_cases;
    document.getElementById("stat-today").textContent = data.today_cases;
    document.getElementById("stat-categories").textContent = data.crime_categories;
}

async function loadCategoryPie() {
    const data = await fetchJSON("/api/dashboard/category-distribution");
    new Chart(document.getElementById("categoryPieChart"), {
        type: "pie",
        data: {
            labels: data.map(d => d.category),
            datasets: [{ data: data.map(d => d.count), backgroundColor: CHART_COLORS }],
        },
        options: { plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } } } },
    });
}

async function loadZoneBar() {
    const data = await fetchJSON("/api/dashboard/zone-distribution");
    new Chart(document.getElementById("zoneBarChart"), {
        type: "bar",
        data: {
            labels: data.map(d => d.zone),
            datasets: [{ label: "Incidents", data: data.map(d => d.count), backgroundColor: "#2563eb", borderRadius: 6 }],
        },
        options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });
}

async function loadStatusChart() {
    const data = await fetchJSON("/api/dashboard/status-breakdown");
    new Chart(document.getElementById("statusChart"), {
        type: "doughnut",
        data: {
            labels: data.map(d => d.status),
            datasets: [{ data: data.map(d => d.count), backgroundColor: ["#10b981", "#f59e0b", "#ef4444"] }],
        },
        options: { plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } } } },
    });
}

async function loadTrendLine() {
    const data = await fetchJSON("/api/dashboard/monthly-trend");
    new Chart(document.getElementById("trendLineChart"), {
        type: "line",
        data: {
            labels: data.map(d => d.month),
            datasets: [{
                label: "Monthly Incidents", data: data.map(d => d.count),
                borderColor: "#2563eb", backgroundColor: "rgba(37,99,235,0.12)",
                fill: true, tension: 0.35, pointRadius: 3,
            }],
        },
        options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });
}

async function loadDangerousLocations() {
    const data = await fetchJSON("/api/dashboard/dangerous-locations");
    const container = document.getElementById("dangerous-locations-list");
    container.innerHTML = data.map(loc => `
        <div class="danger-item">
            <span>${loc.location_name}</span>
            <span>
                <span class="badge-severe">${loc.severe_count} severe</span>
                <span class="text-muted ms-2">${loc.count} total</span>
            </span>
        </div>
    `).join("");
}

document.addEventListener("DOMContentLoaded", () => {
    loadSummary();
    loadCategoryPie();
    loadZoneBar();
    loadStatusChart();
    loadTrendLine();
    loadDangerousLocations();
});
