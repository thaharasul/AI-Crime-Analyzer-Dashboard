document.getElementById("prediction-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const form = e.target;
    const payload = {
        zone: form.zone.value,
        severity: form.severity.value,
        day_of_week: form.day_of_week.value,
        hour_of_day: parseInt(form.hour_of_day.value, 10),
        victim_age: parseInt(form.victim_age.value, 10),
        weapon_involved: form.weapon_involved.checked ? 1 : 0,
    };

    const resultBox = document.getElementById("prediction-result");
    resultBox.innerHTML = "<em>Running Prediction Agent...</em>";

    try {
        const res = await fetch("/api/prediction/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();

        if (!res.ok) {
            resultBox.innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
            return;
        }

        const probRows = data.probability_breakdown.map(p => `
            <div class="mb-2">
                <div class="d-flex justify-content-between"><span>${p.category}</span><span>${(p.probability * 100).toFixed(1)}%</span></div>
                <div class="prob-bar-track"><div class="prob-bar-fill" style="width:${p.probability * 100}%"></div></div>
            </div>
        `).join("");

        resultBox.innerHTML = `
            <div class="mb-3">
                <span class="prediction-badge risk-${data.risk_level}">Risk Level: ${data.risk_level}</span>
            </div>
            <h4>${data.predicted_category}</h4>
            <p class="text-muted">Confidence: ${(data.confidence * 100).toFixed(1)}%</p>
            <hr>
            <h6>Probability Breakdown</h6>
            ${probRows}
        `;
    } catch (err) {
        resultBox.innerHTML = `<div class="alert alert-danger">Prediction failed: ${err}</div>`;
    }
});
