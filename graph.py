from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain.chat_models import FakeListChatModel
from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.tools import analyze_imaging_study, fetch_ehr_context, search_clinical_guidelines

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# --- REAL LLM SETUP (OpenRouter) ---
# Using a performant model via OpenRouter
llm = ChatOpenAI(
    model="meta-llama/llama-3.1-70b-instruct",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# --- NODES ---

def supervisor_node(state: AgentState):
    """
    The Supervisor determines the next step based on the current state.
    """
    # Strict Clinical Protocol: Vision -> EHR -> Guidelines -> Report
    if not state.get("visual_findings"):
        return {"next_agent": "VISION"}
    elif not state.get("ehr_summary"):
        return {"next_agent": "EHR"}
    elif not state.get("active_guidelines"):
        return {"next_agent": "GUIDELINES"}
    else:
        return {"next_agent": "FINISH"}

def vision_node(state: AgentState):
    print("--- Vision Agent: Analyzing Images ---")
    patient_id = state['patient_id']
    modality = state['modality']
    result = analyze_imaging_study.invoke({"patient_id": patient_id, "modality": modality})
    return {
        "visual_findings": result['findings'],
        "radiological_measurements": result['measurements'],
        "confidence_score": result['confidence'],
        "messages": [AIMessage(content=f"Vision Analysis: {result['findings']}")]
    }

def ehr_node(state: AgentState):
    print("--- EHR Agent: Fetching Context ---")
    patient_id = state['patient_id']
    result = fetch_ehr_context.invoke({"patient_id": patient_id})
    return {
        "ehr_summary": result,
        "messages": [AIMessage(content=f"EHR Context: {result}")]
    }

def guidelines_node(state: AgentState):
    print("--- Guidelines Agent: Checking Protocols ---")
    findings = state.get('visual_findings', [])
    query = findings[0] if findings else "general"
    result = search_clinical_guidelines.invoke({"query": query})
    return {
        "active_guidelines": [result],
        "messages": [AIMessage(content=f"Guidelines: {result}")]
    }

def final_report_node(state: AgentState):
    print("--- Generating Final Report (Using LLM) ---")
    
    # Construct a prompt for the LLM to synthesize the report
    findings = state.get('visual_findings', [])
    ehr = state.get('ehr_summary', "N/A")
    guidelines = state.get('active_guidelines', [])
    confidence = state.get('confidence_score', 0.0)
    
    system_prompt = f"""You are an expert Triage Radiologist. 
    Synthesize the following data into a short clinically precise impression.
    
    Context:
    - Imagery Findings: {findings} (Confidence: {confidence})
    - Patient History: {ehr}
    - Guidelines: {guidelines}
    
    Task:
    1. State the Provisional Diagnosis.
    2. Recommend the immediate next step (stat consult vs routine).
    3. Format as "Diagnosis: [X]. Recommendation: [Y]."
    """
    
    try:
        response = llm.invoke(system_prompt)
        diagnosis_text = response.content
    except Exception as e:
        print(f"LLM Error: {e}")
        diagnosis_text = f"Manual Fallback: {findings} identified."

    # Determine Priority Logic (Safety Layer - Keep this rule-based for now)
    priority = "ROUTINE"
    critical_keywords = ["Pneumothorax", "Hemorrhage", "Filling defect", "Midline shift"]
    findings_str = str(findings)
    if confidence and confidence > 0.8 and any(k in findings_str for k in critical_keywords):
        priority = "STAT"
        
    return {
        "triage_score": 1 if priority == "STAT" else 3,
        "provisional_diagnosis": diagnosis_text,
        "next_agent": "END"
    }

# --- GRAPH DEFINITION ---

workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("vision_agent", vision_node)
workflow.add_node("ehr_agent", ehr_node)
workflow.add_node("guidelines_agent", guidelines_node)
workflow.add_node("reporter", final_report_node)

# Edges
workflow.set_entry_point("supervisor")

def decide_next_step(state):
    return state["next_agent"]

workflow.add_conditional_edges(
    "supervisor",
    decide_next_step,
    {
        "VISION": "vision_agent",
        "EHR": "ehr_agent",
        "GUIDELINES": "guidelines_agent",
        "FINISH": "reporter"
    }
)

workflow.add_edge("vision_agent", "supervisor")
workflow.add_edge("ehr_agent", "supervisor")
workflow.add_edge("guidelines_agent", "supervisor")
workflow.add_edge("reporter", END)

# Compile
triage_graph = workflow.compile()
