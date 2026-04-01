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
        alert("Something went wrong. Check console.");
    }
}

function drawCharts(graphs) {
    const ctx1 = document.getElementById("shearChart").getContext("2d");
    const ctx2 = document.getElementById("momentChart").getContext("2d");
    const ctx3 = document.getElementById("loadChart").getContext("2d");

    if (shearChart) shearChart.destroy();
    if (momentChart) momentChart.destroy();
    if (loadChart) loadChart.destroy();

    shearChart = new Chart(ctx1, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Shear Force",
                data: graphs.shear,
                fill: false
            }]
        }
    });

    momentChart = new Chart(ctx2, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Bending Moment",
                data: graphs.moment,
                fill: false
            }]
        }
    });

    loadChart = new Chart(ctx3, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Load (kN/m)",
                data: graphs.load,
                fill: false
            }]
        }
    });

    options: {
        plugins: {
            legend: {
                labels: {
                    color: "white"   // legend text
                }
            }
        };
        scales: {
            x: {
                ticks: {
                    color: "white"   // x-axis numbers
                };
                grid: {
                    color: "rgba(255,255,255,0.1)"
                }
            };
            y: {
                ticks: {
                    color: "white"   // y-axis numbers
                };
                grid: {
                    color: "rgba(255,255,255,0.1)"
                }
            }
        }
    }
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

datasets: [{
    label: "Shear Force",
    data: graphs.shear,
    borderColor: "#3b82f6",  // bright blue
    tension: 0.3
}]

datasets: [{
    label: "Load",
    data: graphs.shear,
    borderColor: "#fa3c23",  // bright red
    tension: 0.3
}]

datasets: [{
    label: "Shear Force",
    data: graphs.shear,
    borderColor: "#f6603b",  // bright blue
    tension: 0.3
}]