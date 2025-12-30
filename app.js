const API_URL = "http://localhost:8000/triage";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("triage-form");
    const outputSection = document.getElementById("output-section");
    const submitBtn = document.getElementById("submit-btn");
    const loader = submitBtn.querySelector(".loader");
    const btnText = submitBtn.querySelector(".btn-text");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // 1. Get Values
        const patientId = document.getElementById("patient-id").value;
        const modality = document.getElementById("modality").value;
        const history = document.getElementById("history").value;

        // 2. Set Loading State
        setLoading(true);

        try {
            // 3. Call API
            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    patient_id: patientId,
                    modality: modality,
                    clinical_history: history
                })
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json();

            // 4. Render Results
            renderResult(data);
        } catch (error) {
            console.warn("Backend connection failed. Switching to Offline Mock Mode.", error);

            // Fallback: Generate Mock Response locally if backend is down
            const mockData = getOfflineMockResponse(patientId);
            if (mockData) {
                renderResult(mockData);

                // Show a small toast/alert that we are in offline mode
                const statusDot = document.querySelector(".status-indicator");
                statusDot.innerHTML = '<span class="dot" style="background: orange"></span> Offline Mode';
            } else {
                outputSection.innerHTML = `
                    <div class="card glass-panel" style="border-color: var(--danger)">
                        <h3 style="color: var(--danger)">System Error</h3>
                        <p>Failed to connect to the Triage Agent Backend, and no local mock data exists for this ID.</p>
                        <p>Please run the backend or try a known test ID (e.g., PT-001).</p>
                    </div>
                `;
            }
        } finally {
            setLoading(false);
        }
    });

    // --- Offline Mock Logic ---
    function getOfflineMockResponse(id) {
        id = id.toUpperCase();
        if (id === "PT-001") {
            return {
                patient_id: "PT-001",
                priority: "STAT",
                findings: ["Large Right-sided Pneumothorax", "Tracheal Deviation", "(OFFLINE SIMULATION)"],
                recommendation: "Immediate chest tube placement recommended.",
                confidence: 0.95
            };
        } else if (id === "PT-002") {
            return {
                patient_id: "PT-002",
                priority: "ROUTINE",
                findings: ["Normal Cardiac Silhouette", "No acute bony abnormality", "(OFFLINE SIMULATION)"],
                recommendation: "Routine post-op screening cleared.",
                confidence: 0.98
            };
        } else if (id === "PT-CRIT") {
            return {
                patient_id: "PT-CRIT",
                priority: "STAT",
                findings: ["Dense MCA Sign", "Hypodensity in left temporal lobe", "(OFFLINE SIMULATION)"],
                recommendation: "Mechanical Thrombectomy candidate.",
                confidence: 0.88
            };
        } else if (id === "PT-PE") {
            return {
                patient_id: "PT-PE",
                priority: "STAT",
                findings: ["Filling defect in pulmonary artery", "Right heart strain", "(OFFLINE SIMULATION)"],
                recommendation: "Anticoagulation / Thrombolysis protocol initiated.",
                confidence: 0.90
            };
        }
        return null;
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loader.classList.remove("hidden");
            btnText.style.opacity = "0";
            submitBtn.disabled = true;
        } else {
            loader.classList.add("hidden");
            btnText.style.opacity = "1";
            submitBtn.disabled = false;
        }
    }

    function renderResult(data) {
        const template = document.getElementById("result-template");
        const clone = template.content.cloneNode(true);

        // Populate Data
        clone.getElementById("res-patient-id").textContent = data.patient_id;

        const priorityEl = clone.getElementById("res-priority");
        priorityEl.textContent = data.priority;
        priorityEl.className = `badge ${data.priority.toLowerCase()}`;

        clone.getElementById("res-confidence").textContent = `Confidence: ${(data.confidence * 100).toFixed(0)}%`;

        const findingsList = clone.getElementById("res-findings");
        findingsList.innerHTML = ""; // Clear previous
        data.findings.forEach(finding => {
            const li = document.createElement("li");
            li.textContent = finding;
            findingsList.appendChild(li);
        });

        clone.getElementById("res-recommendation").textContent = data.recommendation;

        // Animate clear and inject
        outputSection.innerHTML = "";
        outputSection.appendChild(clone);
    }
});
