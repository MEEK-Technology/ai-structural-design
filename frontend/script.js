async function generate() {
    const prompt = document.getElementById("prompt").value;

    const response = await fetch("http://127.0.0.1:8000/predict", {        
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: prompt })
    });

    const data = await response.json();

    document.getElementById("steel").innerText = data.results.steel_area;
    document.getElementById("moment").innerText = data.results.bending_moment;
}