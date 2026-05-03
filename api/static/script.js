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

        console.log("Response:", data); // DEBUG

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        // ── Beam type & load type labels ──
        const typeLabels = {
            "simply_supported": "Simply Supported",
            "cantilever": "Cantilever",
            "continuous": "Continuous",
            "overhang": "Overhang"
        };
        const loadLabels = {
            "udl": "UDL (Uniformly Distributed)",
            "point_load": "Point Load",
            "triangular": "Triangular"
        };

        document.getElementById("beamType").innerText =
            typeLabels[data.input.beam_type] || data.input.beam_type;
        document.getElementById("loadType").innerText =
            loadLabels[data.input.load_type] || data.input.load_type;
        document.getElementById("support").innerText =
            capitalize(data.input.support_left) + " — " + capitalize(data.input.support_right);

        // ── Load Breakdown ──
        document.getElementById("n1").innerText = data.results.n1_slab_load + " kN/m";
        document.getElementById("n2").innerText = data.results.n2_beam_self_weight + " kN/m";
        document.getElementById("n3").innerText = data.results.n3_wall_load + " kN/m";
        document.getElementById("wTotal").innerText = data.results.w_total_udl + " kN/m";
        document.getElementById("p1").innerText = data.results.p1_point_load + " kN";

        // ── Design Results ──
        document.getElementById("mUdl").innerText = data.results.M_udl + " kNm";
        document.getElementById("mPoint").innerText = data.results.M_point + " kNm";
        document.getElementById("moment").innerText = data.results.bending_moment + " kNm";
        document.getElementById("shear").innerText = data.results.max_shear_force + " kN";
        document.getElementById("steel").innerText = data.results.steel_area + " mm²";

        document.getElementById("reinf").innerText =
            data.reinforcement.recommended +
            " (As: " + data.reinforcement.provided_area + " mm²)";

        document.getElementById("beam").innerText =
            data.beam.width + "mm x " + data.beam.depth + "mm";

        document.getElementById("deflection").innerText = data.deflection;

        drawCharts(data.graphs);
        drawBeamDiagram(data.input);

    } catch (error) {
        console.error("Error:", error);
        loader.style.display = "none";
        alert("Something went wrong. Check your console and try again!\nMake sure you're connected to the internet to load graphs.");
    }
}

function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
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
                    label: function (context) {
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
                pointRadius: function (ctx) {
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


// ═══════════════════════════════════════════════
//  BEAM DIAGRAM — Draws beam, supports & loads
// ═══════════════════════════════════════════════

function drawBeamDiagram(input) {
    const canvas = document.getElementById("beamCanvas");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const margin = 60;
    const beamY = 100;
    const startX = margin;
    const endX = canvas.width - margin;
    const beamLen = endX - startX;

    // ── Draw Beam Line ──
    ctx.strokeStyle = "white";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(startX, beamY);
    ctx.lineTo(endX, beamY);
    ctx.stroke();

    // ── Draw Supports ──
    drawSupport(ctx, startX, beamY, input.support_left);
    if (input.beam_type !== "cantilever") {
        drawSupport(ctx, endX, beamY, input.support_right);
    }

    // ── Draw Load ──
    if (input.load_type === "udl") {
        drawUDL(ctx, startX, endX, beamY, input.load);
    } else if (input.load_type === "point_load") {
        const pos = input.load_position || input.span / 2;
        const px = startX + (pos / input.span) * beamLen;
        drawPointLoad(ctx, px, beamY, input.load);
    } else if (input.load_type === "triangular") {
        drawTriangularLoad(ctx, startX, endX, beamY, input.load);
    }

    // ── Labels ──
    ctx.fillStyle = "white";
    ctx.font = "13px Arial";
    ctx.fillText(`Span: ${input.span} m`, canvas.width / 2 - 35, beamY + 55);
}


function drawSupport(ctx, x, y, type) {
    ctx.fillStyle = "white";
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;

    if (type === "roller") {
        // Triangle
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - 10, y + 18);
        ctx.lineTo(x + 10, y + 18);
        ctx.closePath();
        ctx.stroke();
        // Circle (roller)
        ctx.beginPath();
        ctx.arc(x, y + 23, 5, 0, 2 * Math.PI);
        ctx.stroke();

    } else if (type === "pinned") {
        // Filled triangle
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - 10, y + 18);
        ctx.lineTo(x + 10, y + 18);
        ctx.closePath();
        ctx.fill();
        // Ground line
        ctx.beginPath();
        ctx.moveTo(x - 14, y + 18);
        ctx.lineTo(x + 14, y + 18);
        ctx.stroke();

    } else if (type === "fixed") {
        // Wall (vertical line with hatching)
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(x, y - 20);
        ctx.lineTo(x, y + 25);
        ctx.stroke();
        // Hatching lines
        ctx.lineWidth = 1;
        for (let i = -15; i <= 20; i += 7) {
            ctx.beginPath();
            ctx.moveTo(x, y + i);
            ctx.lineTo(x - 10, y + i + 7);
            ctx.stroke();
        }

    } else if (type === "free") {
        // Nothing drawn — free end
    }
}


function drawUDL(ctx, startX, endX, beamY, load) {
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 2;

    const arrows = 10;
    const spacing = (endX - startX) / arrows;

    // Top line connecting arrows
    ctx.beginPath();
    ctx.moveTo(startX, beamY - 30);
    ctx.lineTo(endX, beamY - 30);
    ctx.stroke();

    for (let i = 0; i <= arrows; i++) {
        let x = startX + i * spacing;

        // Vertical arrow line
        ctx.beginPath();
        ctx.moveTo(x, beamY - 30);
        ctx.lineTo(x, beamY);
        ctx.stroke();

        // Arrow head
        ctx.beginPath();
        ctx.moveTo(x - 4, beamY - 8);
        ctx.lineTo(x, beamY);
        ctx.lineTo(x + 4, beamY - 8);
        ctx.stroke();
    }

    // Load label
    ctx.fillStyle = "#10b981";
    ctx.font = "12px Arial";
    ctx.fillText(`${load} kN/m`, (startX + endX) / 2 - 25, beamY - 35);
}


function drawPointLoad(ctx, px, beamY, load) {
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 3;

    // Arrow line
    ctx.beginPath();
    ctx.moveTo(px, beamY - 50);
    ctx.lineTo(px, beamY);
    ctx.stroke();

    // Arrow head
    ctx.beginPath();
    ctx.moveTo(px - 6, beamY - 10);
    ctx.lineTo(px, beamY);
    ctx.lineTo(px + 6, beamY - 10);
    ctx.stroke();

    // Label
    ctx.fillStyle = "#ef4444";
    ctx.font = "bold 13px Arial";
    ctx.fillText(`${load} kN`, px - 18, beamY - 55);
}


function drawTriangularLoad(ctx, startX, endX, beamY, load) {
    ctx.strokeStyle = "#f59e0b";
    ctx.lineWidth = 2;

    const arrows = 10;
    const spacing = (endX - startX) / arrows;

    // Slanted top line (0 at left → max at right)
    ctx.beginPath();
    ctx.moveTo(startX, beamY);
    ctx.lineTo(endX, beamY - 40);
    ctx.stroke();

    for (let i = 1; i <= arrows; i++) {
        let x = startX + i * spacing;
        let height = (i / arrows) * 40;  // Linearly increasing

        // Vertical arrow
        ctx.beginPath();
        ctx.moveTo(x, beamY - height);
        ctx.lineTo(x, beamY);
        ctx.stroke();

        // Arrow head
        ctx.beginPath();
        ctx.moveTo(x - 4, beamY - 8);
        ctx.lineTo(x, beamY);
        ctx.lineTo(x + 4, beamY - 8);
        ctx.stroke();
    }

    // Label
    ctx.fillStyle = "#f59e0b";
    ctx.font = "12px Arial";
    ctx.fillText(`${load} kN/m (max)`, endX - 70, beamY - 45);
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
