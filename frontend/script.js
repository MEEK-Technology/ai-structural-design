// async function generate() {
//     const prompt = document.getElementById("prompt").value;

//     const response = await fetch("http://127.0.0.1:8000/predict", {        
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json"
//         },
//         body: JSON.stringify({ prompt: prompt })
//     });

//     const data = await response.json();

//     document.getElementById("steel").innerText = data.results.steel_area;
//     document.getElementById("moment").innerText = data.results.bending_moment;
// }


let shearChart, momentChart, loadChart;

// async function generate() {
//     const prompt = document.getElementById("prompt").value;

//     const response = await fetch("http://127.0.0.1:8000/predict", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json"
//         },
//         body: JSON.stringify({ prompt: prompt })
//     });

//     const data = await response.json();

//     document.getElementById("steel").innerText = data.results.steel_area;
//     document.getElementById("moment").innerText = data.results.bending_moment;
//     document.getElementById("wall").innerText = data.results.wall_load;
//     document.getElementById("total").innerText = data.results.total_load;
//     document.getElementById("reinf").innerText = data.reinforcement.recommended + " (As provided: " + data.reinforcement.provided_area + " mm²)";

//     drawCharts(data.graphs);
// }

async function generate() {
    const prompt = document.getElementById("prompt").value;
    const loader = document.getElementById("loader");

    loader.style.display = "block";

    const response = await fetch("http://127.0.0.1:8000/predict", {
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
}

async function downloadReport() {
    const prompt = document.getElementById("prompt").value;

    const response = await fetch("http://127.0.0.1:8000/download-report", {
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