let shearChart, momentChart, loadChart;

// Store parsed params between modal steps
let pendingParams = null;

// ═══════════════════════════════════════════════
//  STEP 1: Parse prompt → Show modal
// ═══════════════════════════════════════════════

async function handleGenerate() {
    const prompt = document.getElementById("prompt").value.trim();
    if (!prompt) {
        alert("Please enter a beam design prompt first.");
        return;
    }

    const loader = document.getElementById("loader");
    loader.style.display = "block";

    try {
        const response = await fetch("/parse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt })
        });

        const data = await response.json();
        loader.style.display = "none";

        if (data.error) {
            alert("Parsing Error: " + data.error);
            return;
        }

        pendingParams = data.parsed;
        showModal(data.parsed);

    } catch (error) {
        console.error("Parse error:", error);
        loader.style.display = "none";
        alert("Failed to parse prompt. Check console for details.");
    }
}


// ═══════════════════════════════════════════════
//  MODAL FUNCTIONS
// ═══════════════════════════════════════════════

function showModal(params) {
    const grid = document.getElementById("parsedParams");

    // Parameter definitions: [key, label, unit, highlight?]
    const fields = [
        ["beam_type",       "Beam Type",        "",    true],
        ["load_type",       "Load Type",        "",    true],
        ["span",            "Span",             "m",   false],
        ["load",            "Load",             "kN/m", false],
        ["slab_load",       "Slab Load (n1)",   "kN/m", false],
        ["point_load",      "Point Load (p1)",  "kN",  false],
        ["load_position",   "Load Position",    "m",   false],
        ["overhang_length", "Overhang Length",   "m",   false],
        ["fcu",             "Concrete (fcu)",   "N/mm²", false],
        ["fy",              "Steel (fy)",       "N/mm²", false],
        ["support_left",    "Left Support",     "",    false],
        ["support_right",   "Right Support",    "",    false],
        ["wall_height",     "Wall Height",      "m",   false],
        ["wall_thickness",  "Wall Thickness",   "m",   false],
        ["density",         "Wall Density",     "kN/m³", false],
    ];

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

    let html = "";

    for (const [key, label, unit, highlight] of fields) {
        let val = params[key];

        // Skip null/zero optional fields
        if (val === null || val === undefined) continue;
        if (val === 0 && ["slab_load", "point_load", "wall_height", "wall_thickness", "overhang_length", "load_position"].includes(key)) continue;

        // For continuous beams, skip single span/support (we show multi-span instead)
        if (params.spans && ["span", "support_left", "support_right"].includes(key)) continue;

        // Format display value
        if (key === "beam_type") val = typeLabels[val] || val;
        if (key === "load_type") val = loadLabels[val] || val;
        if (key === "support_left" || key === "support_right") val = capitalize(val);

        const displayVal = unit ? `${val} ${unit}` : val;
        const hlClass = highlight ? " highlight" : "";
        const fullClass = (key === "beam_type" || key === "load_type") ? " full-width" : "";

        html += `
            <div class="param-item${fullClass}">
                <span class="param-label">${label}</span>
                <span class="param-value${hlClass}">${displayVal}</span>
            </div>
        `;
    }

    // ── Multi-span display for continuous beams ──
    if (params.spans && params.spans.length > 0) {
        const spansStr = params.spans.map(s => s + "m").join(" → ");
        html += `
            <div class="param-item full-width">
                <span class="param-label">Spans (${params.spans.length})</span>
                <span class="param-value highlight">${spansStr}</span>
            </div>
        `;
    }

    if (params.supports && params.supports.length > 0) {
        const supStr = params.supports.map(s => capitalize(s)).join(" → ");
        html += `
            <div class="param-item full-width">
                <span class="param-label">Supports (${params.supports.length})</span>
                <span class="param-value">${supStr}</span>
            </div>
        `;
    }

    grid.innerHTML = html;

    // Show modal
    document.getElementById("parseModal").classList.add("active");
}

function closeModal() {
    document.getElementById("parseModal").classList.remove("active");
    pendingParams = null;
}

// ═══════════════════════════════════════════════
//  STEP 2: Confirm → Run full design
// ═══════════════════════════════════════════════

async function confirmGenerate() {
    closeModal();
    const prompt = document.getElementById("prompt").value;
    await generate(prompt);
}

async function generate(prompt) {
    try {
        const loader = document.getElementById("loader");
        loader.style.display = "block";

        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt })
        });

        const data = await response.json();

        loader.style.display = "none";

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

        // Support display — continuous vs single-span
        if (data.continuous) {
            const supStr = data.continuous.supports.map(s => capitalize(s)).join(" → ");
            document.getElementById("support").innerText = supStr;
        } else {
            document.getElementById("support").innerText =
                capitalize(data.input.support_left) + " — " + capitalize(data.input.support_right);
        }

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

        // ── Continuous Beam Extra Data ──
        const contDiv = document.getElementById("continuousData");
        if (data.continuous && contDiv) {
            let html = `<h4 style="margin-top:12px; opacity:0.8;">Continuous Beam Analysis (Three-Moment Theorem)</h4>`;
            html += `<div class="result-item"><strong>Spans:</strong> ${data.continuous.spans.map(s => s + "m").join(" + ")} (${data.continuous.n_spans}-span)</div>`;

            // Support moments table
            html += `<div class="result-item"><strong>Support Moments:</strong></div>`;
            for (let i = 0; i < data.continuous.support_moments.length; i++) {
                const label = String.fromCharCode(65 + i); // A, B, C, D...
                const m = data.continuous.support_moments[i];
                html += `<div class="result-item">&nbsp;&nbsp;M<sub>${label}</sub> = ${m.toFixed(2)} kNm</div>`;
            }

            // Reactions table
            html += `<div class="result-item"><strong>Support Reactions:</strong></div>`;
            for (let i = 0; i < data.continuous.reactions.length; i++) {
                const label = String.fromCharCode(65 + i);
                const r = data.continuous.reactions[i];
                html += `<div class="result-item">&nbsp;&nbsp;R<sub>${label}</sub> = ${r.toFixed(2)} kN</div>`;
            }

            contDiv.innerHTML = html;
            contDiv.style.display = "block";
        } else if (contDiv) {
            contDiv.innerHTML = "";
            contDiv.style.display = "none";
        }

        drawCharts(data.graphs);

        // Draw beam diagram — multi-span or single-span
        if (data.continuous) {
            drawContinuousBeamDiagram(data.continuous);
        } else {
            drawBeamDiagram(data.input);
        }

    } catch (error) {
        console.error("Error:", error);
        document.getElementById("loader").style.display = "none";
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

    const oh = input.overhang_length || 0;
    const totalLen = input.span + oh;
    const beamLen = endX - startX;

    // Support positions (proportional to total length)
    const supportAx = startX;
    const supportBx = startX + (input.span / totalLen) * beamLen;
    const freeEndX = endX;  // End of overhang (or end of beam if no overhang)

    // ── Draw Beam Line ──
    ctx.strokeStyle = "white";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(startX, beamY);
    ctx.lineTo(freeEndX, beamY);
    ctx.stroke();

    // ── Draw Supports ──
    drawSupport(ctx, supportAx, beamY, input.support_left);
    if (input.beam_type === "overhang") {
        drawSupport(ctx, supportBx, beamY, input.support_right || "roller");
    } else if (input.beam_type !== "cantilever") {
        drawSupport(ctx, freeEndX, beamY, input.support_right);
    }

    // ── Draw Load ──
    if (input.load_type === "udl") {
        drawUDL(ctx, startX, freeEndX, beamY, input.load);
    } else if (input.load_type === "point_load") {
        const pos = input.load_position || input.span / 2;
        const px = startX + (pos / totalLen) * beamLen;
        drawPointLoad(ctx, px, beamY, input.load);
    } else if (input.load_type === "triangular") {
        drawTriangularLoad(ctx, startX, freeEndX, beamY, input.load);
    }

    // ── Labels ──
    ctx.fillStyle = "white";
    ctx.font = "13px Arial";

    if (oh > 0) {
        // Label span and overhang separately
        const midSpan = (supportAx + supportBx) / 2;
        ctx.fillText(`Span: ${input.span}m`, midSpan - 25, beamY + 55);

        const midOH = (supportBx + freeEndX) / 2;
        ctx.fillText(`OH: ${oh}m`, midOH - 15, beamY + 55);

        // Label supports
        ctx.font = "11px Arial";
        ctx.fillText("A", supportAx - 3, beamY + 45);
        ctx.fillText("B", supportBx - 3, beamY + 45);
        ctx.fillText("C", freeEndX - 3, beamY + 10);
    } else {
        ctx.fillText(`Span: ${input.span}m`, canvas.width / 2 - 35, beamY + 55);
    }
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


// ═══════════════════════════════════════════════
//  MULTI-SPAN BEAM DIAGRAM
// ═══════════════════════════════════════════════

function drawContinuousBeamDiagram(contData) {
    const canvas = document.getElementById("beamCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    // Resize canvas for multi-span
    const totalLength = contData.spans.reduce((a, b) => a + b, 0);
    canvas.width = Math.max(600, 100 + contData.spans.length * 160);
    canvas.height = 200;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const marginL = 50;
    const marginR = 50;
    const beamY = 100;
    const usableW = canvas.width - marginL - marginR;

    // Scale: pixels per meter
    const scale = usableW / totalLength;

    // ── Draw beam line ──
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(marginL, beamY);
    ctx.lineTo(marginL + totalLength * scale, beamY);
    ctx.stroke();

    // ── Draw supports ──
    let xPos = marginL;
    ctx.lineWidth = 2;

    for (let i = 0; i < contData.supports.length; i++) {
        const supType = contData.supports[i];
        const label = String.fromCharCode(65 + i); // A, B, C, D...

        if (supType === "fixed") {
            drawFixedSupport(ctx, xPos, beamY);
        } else if (supType === "roller") {
            drawRollerSupport(ctx, xPos, beamY);
        } else {
            drawPinnedSupport(ctx, xPos, beamY);
        }

        // Label
        ctx.fillStyle = "#10b981";
        ctx.font = "bold 14px Arial";
        ctx.textAlign = "center";
        ctx.fillText(label, xPos, beamY + 45);

        // Move to next support
        if (i < contData.spans.length) {
            xPos += contData.spans[i] * scale;
        }
    }

    // ── Draw span labels ──
    let xLabel = marginL;
    ctx.fillStyle = "#e2e8f0";
    ctx.font = "12px Arial";
    ctx.textAlign = "center";

    for (let i = 0; i < contData.spans.length; i++) {
        const spanPx = contData.spans[i] * scale;
        const midX = xLabel + spanPx / 2;

        // Span dimension line
        ctx.strokeStyle = "#94a3b8";
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(xLabel + 5, beamY - 30);
        ctx.lineTo(xLabel + spanPx - 5, beamY - 30);
        ctx.stroke();
        ctx.setLineDash([]);

        // Span label
        ctx.fillStyle = "#f59e0b";
        ctx.font = "bold 12px Arial";
        ctx.fillText(contData.spans[i] + "m", midX, beamY - 35);

        xLabel += spanPx;
    }

    // ── Support moments (show non-zero) ──
    xPos = marginL;
    ctx.font = "11px Arial";
    ctx.fillStyle = "#ef4444";
    ctx.textAlign = "center";

    for (let i = 0; i < contData.support_moments.length; i++) {
        const m = contData.support_moments[i];
        if (Math.abs(m) > 0.01) {
            ctx.fillText("M=" + m.toFixed(1), xPos, beamY - 55);
        }
        if (i < contData.spans.length) {
            xPos += contData.spans[i] * scale;
        }
    }
}

function drawPinnedSupport(ctx, x, y) {
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 2;
    ctx.fillStyle = "transparent";

    // Triangle
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - 12, y + 22);
    ctx.lineTo(x + 12, y + 22);
    ctx.closePath();
    ctx.stroke();

    // Ground line under triangle
    ctx.beginPath();
    ctx.moveTo(x - 16, y + 25);
    ctx.lineTo(x + 16, y + 25);
    ctx.stroke();

    // Small hatching lines under ground
    for (let i = -12; i <= 12; i += 6) {
        ctx.beginPath();
        ctx.moveTo(x + i, y + 25);
        ctx.lineTo(x + i - 4, y + 30);
        ctx.stroke();
    }
}

function drawRollerSupport(ctx, x, y) {
    ctx.strokeStyle = "#f59e0b";
    ctx.lineWidth = 2;
    ctx.fillStyle = "transparent";

    // Triangle
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - 12, y + 18);
    ctx.lineTo(x + 12, y + 18);
    ctx.closePath();
    ctx.stroke();

    // Circle (roller) underneath
    ctx.beginPath();
    ctx.arc(x, y + 24, 5, 0, Math.PI * 2);
    ctx.stroke();

    // Ground line under circle
    ctx.beginPath();
    ctx.moveTo(x - 16, y + 30);
    ctx.lineTo(x + 16, y + 30);
    ctx.stroke();
}

function drawFixedSupport(ctx, x, y) {
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 3;

    // Vertical wall
    ctx.beginPath();
    ctx.moveTo(x, y - 20);
    ctx.lineTo(x, y + 25);
    ctx.stroke();

    // Hatching lines
    ctx.lineWidth = 1.5;
    for (let i = -15; i <= 20; i += 7) {
        ctx.beginPath();
        ctx.moveTo(x, y + i);
        ctx.lineTo(x - 10, y + i + 7);
        ctx.stroke();
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
    link.download = "ai_beam_report.pdf";
    link.click();
}

async function checkHealth() {
    const res = await fetch("/health");
    const data = await res.json();

    document.getElementById("status").innerText = data.status.toUpperCase();
}

checkHealth();
