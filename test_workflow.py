import asyncio
from app.graph import triage_graph
from langchain_core.messages import HumanMessage

async def run_test(patient_id, modality):
    print(f"\nScanning Patient: {patient_id} ({modality})...")
    
    initial_state = {
        "messages": [HumanMessage(content=f"Test run for {patient_id}")],
        "patient_id": patient_id,
        "modality": modality,
        "visual_findings": [],
        "ehr_summary": None,
        "active_guidelines": [],
        "confidence_score": 0.0
    }
    
    try:
        final_state = await triage_graph.ainvoke(initial_state)
        
        print(f"--- RESULT FOR {patient_id} ---")
        print(f"Diagnosis: {final_state.get('provisional_diagnosis')}")
        print(f"Triage Score: {final_state.get('triage_score')} (1=Critical, 5=Routine)")
        print(f"Confidence: {final_state.get('confidence_score')}")
        print(f"Trace: {[m.content for m in final_state['messages'] if not isinstance(m, HumanMessage)]}")
        
    except Exception as e:
        print(f"ERROR: {e}")

async def main():
    print("Starting Agentic Diagnostic Verification...")
    
    # Test Case 1: Critical (Pneumothorax)
    await run_test("PT-001", "CXR")
    
    # Test Case 2: Routine (Normal)
    await run_test("PT-002", "CXR")
    
    # Test Case 3: Critical Stroke
    await run_test("PT-CRIT", "CT_HEAD")

if __name__ == "__main__":
    asyncio.run(main())
