let shearChart, momentChart, loadChart;

async function generate() {
    try {
        const prompt = document.getElementById("prompt").value;
        const loader = document.getElementById("loader");

        loader.style.display = "block";

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt: prompt })
        });

        const data = await response.json();

        loader.style.display = "none";

        document.getElementById("steel").innerText = data.results.steel_area + " mm²";
        document.getElementById("moment").innerText = data.results.bending_moment + " kNm";
        document.getElementById("wall").innerText = data.results.wall_load + " kN/m";
        document.getElementById("total").innerText = data.results.total_load + " kN/m";

        document.getElementById("reinf").innerText =
            data.reinforcement.recommended +
            " (As: " + data.reinforcement.provided_area + " mm²)";

        drawCharts(data.graphs);

    } catch (error) {
        console.error("Error:", error);
        alert("Something went wrong. Connect your internet to load graph");
    }
}

function drawCharts(graphs) {

    const ctx1 = document.getElementById("shearChart").getContext("2d");
    const ctx2 = document.getElementById("momentChart").getContext("2d");
    const ctx3 = document.getElementById("loadChart").getContext("2d");

    if (shearChart) shearChart.destroy();
    if (momentChart) momentChart.destroy();
    if (loadChart) loadChart.destroy();

    const options = {
        responsive: true,
        plugins: {
            legend: {
                labels: { color: "white" }
            }
        },
        scales: {
            x: {
                ticks: { color: "white" },
                grid: { color: "rgba(255,255,255,0.1)" }
            },
            y: {
                ticks: { color: "white" },
                grid: { color: "rgba(255,255,255,0.1)" }
            }
        }
    };

    const animation = {
        duration: 1500,
        easing: "easeOutQuart"
    };

    shearChart = new Chart(ctx1, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Shear Force (kN)",
                data: graphs.shear,
                borderColor: "#3b82f6",
                backgroundColor: "rgba(59,130,246,0.2)",
                fill: true,
                tension: 0.4
            }]
        },
        options: options
    });

    momentChart = new Chart(ctx2, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Bending Moment (kNm)",
                data: graphs.moment,
                borderColor: "#f59e0b",
                backgroundColor: "rgba(245,158,11,0.2)",
                fill: true,
                tension: 0.4
            }]
        },
        options: options
    });

    loadChart = new Chart(ctx3, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Load (kN/m)",
                data: graphs.load,
                borderColor: "#10b981",
                backgroundColor: "rgba(16,185,129,0.2)",
                fill: true,
                tension: 0
            }]
        },
        options: options
    });
}

async function downloadReport() {
    const prompt = document.getElementById("prompt").value;

    const response = await fetch("/download-report", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: prompt })
    });

    const blob = await response.blob();

    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "beam_report.pdf";
    link.click();
}

async function checkHealth() {
    const res = await fetch("/health");
    const data = await res.json();

    document.getElementById("status").innerText = data.status.toUpperCase();
}

checkHealth();
