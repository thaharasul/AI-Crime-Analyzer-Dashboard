const SEVERITY_COLORS = {
    Low: "#10b981",
    Medium: "#f59e0b",
    High: "#f97316",
    Critical: "#ef4444",
};

async function loadCrimeMap() {
    const map = L.map("crimeMap").setView([13.0827, 80.2707], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        maxZoom: 18,
    }).addTo(map);

    const res = await fetch("/api/dashboard/map-points");
    const points = await res.json();

    points.forEach(p => {
        const marker = L.circleMarker([p.latitude, p.longitude], {
            radius: 6,
            color: SEVERITY_COLORS[p.severity] || "#2563eb",
            fillColor: SEVERITY_COLORS[p.severity] || "#2563eb",
            fillOpacity: 0.75,
            weight: 1,
        }).addTo(map);

        marker.bindPopup(`
            <strong>${p.crime_type}</strong><br>
            ${p.category} - ${p.severity} severity<br>
            ${p.location_name}, ${p.zone}<br>
            ${p.date_reported} | Status: ${p.status}
        `);
    });
}

document.addEventListener("DOMContentLoaded", loadCrimeMap);
