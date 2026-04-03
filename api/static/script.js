let shearChart, momentChart, loadChart;

async function generate() {
    try {
        const prompt = document.getElementById("prompt").value;
        const loader = document.getElementById("loader");

        loader.style.display = "block";

        console.log("Sending prompt:", prompt); // DEBUG

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt: prompt })
        });

        const data = await response.json();

        loader.style.display = "none";

        console.log("Response:", data); console.log("Response:", data); // DEBUG

        document.getElementById("steel").innerText = data.results.steel_area + " mm²";
        document.getElementById("moment").innerText = data.results.bending_moment + " kNm";
        document.getElementById("wall").innerText = data.results.wall_load + " kN/m";
        document.getElementById("total").innerText = data.results.total_load + " kN/m";

        document.getElementById("reinf").innerText =
            data.reinforcement.recommended +
            " (As: " + data.reinforcement.provided_area + " mm²)";

        drawCharts(data.graphs);  // Graphs calling
        drawBeamDiagram(data.input.span, data.input.load);  //  Beam UI calling

    } catch (error) {
        console.error("Error:", error);   // ERROR DEBUG CATCHER
        alert("Something went wrong. Check your console.. and try again!"); 
        alert("Make sure you're connected to the internet to load graph.");
    }
}

function drawCharts(graphs) {

    const peak = getMaxPoint(graphs.moment);

    const ctx1 = document.getElementById("shearChart").getContext("2d");
    const ctx2 = document.getElementById("momentChart").getContext("2d");
    const ctx3 = document.getElementById("loadChart").getContext("2d");

    if (shearChart) shearChart.destroy();
    if (momentChart) momentChart.destroy();
    if (loadChart) loadChart.destroy();

    const options = (titleText) => ({
        responsive: true,
        animation: {
            duration: 1500,
            easing: "easeOutQuart"
        },

        plugins: {
            legend: {
                labels: { color: "white" }
            },
            title: {
                display: true,
                text: titleText,
                color: "white"
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return context.dataset.label + ": " + context.raw.toFixed(2);
                    }
                }
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
    });

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
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: options("Shear Force Diagram")
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
                tension: 0.4,
                pointRadius: function(ctx) {
                    return ctx.dataIndex === peak.index ? 6 : 0;
                },
                pointBackgroundColor: "#ff0000"
            }]
        },
        options: options("Bending Moment Diagram")
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
                tension: 0,
                pointRadius: 0    
            }]
        },
        options: options("Load Diagram")
    });
}

function getMaxPoint(data) {
    let max = Math.max(...data);
    let index = data.indexOf(max);
    return { max, index };
}

function drawBeamDiagram(span, load) {                 // Beam UI Diagram
    const canvas = document.getElementById("beamCanvas");
    const ctx = canvas.getContext("2d");

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const margin = 50;
    const beamY = 100;
    const startX = margin;
    const endX = canvas.width - margin;

    // Draw Beam Line
    ctx.strokeStyle = "white";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(startX, beamY);
    ctx.lineTo(endX, beamY);
    ctx.stroke();

    // Draw Supports
    ctx.fillStyle = "white";

    // Left support
    ctx.beginPath();
    ctx.moveTo(startX - 10, beamY + 20);
    ctx.lineTo(startX + 10, beamY + 20);
    ctx.lineTo(startX, beamY);
    ctx.fill();

    // Right support
    ctx.beginPath();
    ctx.moveTo(endX - 10, beamY + 20);
    ctx.lineTo(endX + 10, beamY + 20);
    ctx.lineTo(endX, beamY);
    ctx.fill();

    // 🔹 Draw Load Arrows
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 2;

    const arrows = 10;
    const spacing = (endX - startX) / arrows;

    for (let i = 0; i <= arrows; i++) {
        let x = startX + i * spacing;

        ctx.beginPath();
        ctx.moveTo(x, beamY - 30);
        ctx.lineTo(x, beamY);
        ctx.stroke();

        // Arrow head
        ctx.beginPath();
        ctx.moveTo(x - 5, beamY - 10);
        ctx.lineTo(x, beamY);
        ctx.lineTo(x + 5, beamY - 10);
        ctx.stroke();
    }

    // Labels
    ctx.fillStyle = "white";
    ctx.font = "14px Arial";

    ctx.fillText(`Span: ${span} m`, canvas.width / 2 - 40, beamY + 40);
    ctx.fillText(`Load: ${load} kN/m`, canvas.width / 2 - 50, beamY - 50);
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
    link.download = "ai_beam_report.pdf";
    link.click();
}

async function checkHealth() {
    const res = await fetch("/health");
    const data = await res.json();

    document.getElementById("status").innerText = data.status.toUpperCase();
}

checkHealth();
