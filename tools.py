from langchain_core.tools import tool
import random

@tool
def analyze_imaging_study(patient_id: str, modality: str):
    """
    Simulates a Deep Learning Vision Model analysis.
    Returns structured findings and bounding boxes.
    """
    # Mock Logic: Deterministic results based on Patient ID for testing
    if patient_id == "PT-001":
        return {
            "findings": ["Large Right-sided Pneumothorax", "Tracheal Deviation"],
            "measurements": {"lung_collapse_percent": 45},
            "confidence": 0.95
        }
    elif patient_id == "PT-002":
        return {
            "findings": ["Normal Cardiac Silhouette", "No acute bony abnormality"],
            "measurements": {},
            "confidence": 0.98
        }
    elif patient_id == "PT-CRIT":
        return {
            "findings": ["Dense MCA Sign", "Hypodensity in left temporal lobe"],
            "measurements": {"aspects_score": 6},
            "confidence": 0.88
        }
    elif patient_id == "PT-PNEUMO":
        return {
            "findings": ["Right Lower Lobe Consolidation", "Air Bronchograms"],
            "measurements": {"opacity_density": "high"},
            "confidence": 0.92
        }
    elif patient_id == "PT-FRAC":
        return {
            "findings": ["Displaced fractures of left 4th and 5th ribs"],
            "measurements": {"displacement_mm": 4},
            "confidence": 0.96
        }
    elif patient_id == "PT-PE":
        return {
            "findings": ["Filling defect in right main pulmonary artery"],
            "measurements": {"qanadli_score": 25},
            "confidence": 0.89
        }
    else:
        return {
            "findings": ["No acute findings detected"],
            "measurements": {},
            "confidence": 0.70
        }

@tool
def fetch_ehr_context(patient_id: str):
    """
    Simulates a FHIR query to get relevant patient history.
    """
    if patient_id == "PT-001":
        return "Male, 24yo. Presented after MVC (Motor Vehicle Collision). C/O Shortness of Breath. SpO2 88% on RA."
    elif patient_id == "PT-002":
        return "Female, 55yo. Routine pre-op screening. Asymptomatic."
    elif patient_id == "PT-CRIT":
        return "Male, 68yo. Sudden onset right-sided weakness. Last known well: 2 hours ago."
    elif patient_id == "PT-PNEUMO":
        return "Female, 72yo. High fever (39.5C), productive cough for 3 days. History of COPD."
    elif patient_id == "PT-FRAC":
        return "Male, 45yo. Fell from ladder. Left-sided chest pain."
    elif patient_id == "PT-PE":
        return "Female, 32yo. Post-partum day 5. Sudden onset dyspnea and tachycardia."
    else:
        return "No significant medical history derived."

@tool
def search_clinical_guidelines(query: str):
    """
    Simulates a RAG retrieval system for medical guidelines.
    """
    query = query.lower()
    if "pneumothorax" in query:
        return "Fleischner Society: For large pneumothorax (>2cm), immediate chest tube placement is recommended if patient is unstable."
    elif "stroke" in query or "mca" in query:
        return "AHA Guidelines: Candidate for mechanical thrombectomy if occlusion confirmed within 6 hours."
    elif "consolidation" in query or "pneumonia" in query:
        return "IDSA Guidelines: Start empiric antibiotics for CAP. Assess CURB-65 score."
    elif "fracture" in query or "rib" in query:
        return "Trauma Guidelines: Assess for flail chest and pulmonary contusion. Pain management is priority."
    elif "filling defect" in query or "pulmonary artery" in query:
        return "ACCP Guidelines: Anticoagulation indicated for acute PE. Assess for thrombolysis eligibility if hemodynamically unstable."
    else:
        return "General ACR Appropriateness Criteria: correlate with clinical presentation."

# List of tools to be bound to agents
vision_tools = [analyze_imaging_study]
ehr_tools = [fetch_ehr_context]
guideline_tools = [search_clinical_guidelines]
