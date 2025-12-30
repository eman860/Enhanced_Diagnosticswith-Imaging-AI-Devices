from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    The shared state of the Radiology Triage Agent.
    """
    # The conversation history between agents (optional, mostly for debugging)
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Input Data
    patient_id: str
    modality: str  # e.g., "CXR", "CT_HEAD"
    
    # Derived Clinical Context
    ehr_summary: Optional[str]
    
    # Analysis Results
    visual_findings: List[str]
    radiological_measurements: dict  # e.g., {"midline_shift_mm": 0, "pneumothorax_percent": 25}
    
    # Clinical Reasoning
    active_guidelines: List[str]
    
    # Final Output
    provisional_diagnosis: Optional[str]
    triage_score: int  # 1 (Critical) to 5 (Routine)
    confidence_score: float
    
    # Supervisor State
    next_agent: Optional[str]
