import asyncio
from app.graph import triage_graph
from langchain_core.messages import HumanMessage

async def run_scenario(name, patient_id, modality, expected_priority):
    print(f"\n--- Running Scenario: {name} ---")
    print(f"Input: {patient_id} ({modality})")
    
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
        
        # Verify Results
        score = final_state.get('triage_score')
        priority = "STAT" if score == 1 else "ROUTINE"
        findings = final_state.get('visual_findings')
        
        print(f"Diagnosis: {final_state.get('provisional_diagnosis')}")
        print(f"Findings: {findings}")
        print(f"Priority: {priority} (Expected: {expected_priority})")
        
        if priority == expected_priority:
            print("✅ TEST PASSED")
        else:
            print("❌ TEST FAILED")
            
    except Exception as e:
        print(f"ERROR: {e}")

async def main():
    print("Beginning Expanded Clinical Verification...\n")
    
    # 1. Pneumonia (Usually Routine/Urgent but not Immediate Life Threat like Pneumothorax)
    # Note: Our logic marks STAT only for Pneumothorax/Hemorrhage currently.
    await run_scenario("Pneumonia Case", "PT-PNEUMO", "CXR", "ROUTINE")
    
    # 2. Rib Fractures
    await run_scenario("Rib Fracture Case", "PT-FRAC", "CXR", "ROUTINE")
    
    # 3. Pulmonary Embolism (Should be Critical/STAT based on medical severity)
    # logic updated to catch "Filling defect"
    await run_scenario("Pulmonary Embolism", "PT-PE", "CT_PA", "STAT") 
    # Wait, looking at graph.py, the logic is:
    # if confidence > 0.8 and ("Pneumothorax" in str(findings) or "Hemorrhage" in str(findings)):
    # So PE will likely fail to be marked STAT unless we update the reporter logic!
    # This test will reveal that 'bug' (feature gap).

if __name__ == "__main__":
    asyncio.run(main())
