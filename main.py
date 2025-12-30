import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.graph import triage_graph
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Agentic Radiology Triage System",
    description="Multi-Agent AI system for prioritizing acute care radiology cases.",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for MVP simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TriageRequest(BaseModel):
    patient_id: str
    modality: str
    clinical_history: Optional[str] = None

class TriageResponse(BaseModel):
    patient_id: str
    priority: str
    findings: List[str]
    recommendation: str
    confidence: float

@app.get("/")
def read_root():
    return {"status": "System Online", "service": "Radiology Triage Agent"}

@app.post("/triage", response_model=TriageResponse)
async def triage_case(request: TriageRequest):
    """
    Submit a case for AI Triage.
    This endpoint invokes the LangGraph workflow.
    """
    # Initialize State
    initial_state = {
        "messages": [HumanMessage(content=f"Triage request for {request.patient_id} ({request.modality})")],
        "patient_id": request.patient_id,
        "modality": request.modality,
        "visual_findings": [],
        "ehr_summary": None,
        "active_guidelines": [],
        "confidence_score": 0.0
    }
    
    # Run the Graph
    final_state = await triage_graph.ainvoke(initial_state)
    
    # Extract Results
    return {
        "patient_id": final_state.get("patient_id"),
        "priority": "STAT" if final_state.get("triage_score", 3) == 1 else "ROUTINE",
        "findings": final_state.get("visual_findings", ["No findings logged"]),
        "recommendation": final_state.get("provisional_diagnosis", "Review required"),
        "confidence": final_state.get("confidence_score", 0.0)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
