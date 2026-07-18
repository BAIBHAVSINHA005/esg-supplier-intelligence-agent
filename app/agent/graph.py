#app\agent\graph.py

from langgraph.graph import StateGraph, END

from app.agent.state import AssessmentState
from app.agent.nodes.ingest import ingest_document
from app.agent.nodes.quality import quality_check
from app.agent.nodes.extract import extract_indicators
from app.agent.nodes.analysis import analysis_layer
from app.agent.nodes.confidence import assess_confidence
from app.agent.nodes.questions import generate_questions
from app.agent.nodes.brief import compile_brief
from app.agent.nodes.failure import handle_failure
from app.agent.edges.routing import route_after_quality_check
from app.agent.nodes.retrieve import retrieve_context
from app.agent.nodes.index import index_document


def build_graph():
    """
    Assemble and compile the ESG Intelligence Agent LangGraph graph.

    Graph structure:
    
    Graph structure:

START
  └─ ingest_document
        └─ index_document
              └─ quality_check
                    ├─ [document_failure=True]  → handle_failure → END
                    └─ [document_failure=False] → retrieve_context
                                                     └─ extract_indicators
                                                            └─ analysis_layer
                                                                   └─ assess_confidence
                                                                          └─ generate_questions
                                                                                 └─ compile_brief
                                                                                        └─ END
"""

    workflow = StateGraph(AssessmentState)

    # ── Register nodes ─────────────────────────────────────────────────────
    # Every node used in any edge must be registered here first.
    workflow.add_node("ingest_document", ingest_document)
    workflow.add_node("quality_check", quality_check)
    workflow.add_node("extract_indicators", extract_indicators)
    workflow.add_node("analysis_layer", analysis_layer)
    workflow.add_node("assess_confidence", assess_confidence)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("compile_brief", compile_brief)
    workflow.add_node("handle_failure", handle_failure)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("index_document", index_document)

    # ── Entry point ────────────────────────────────────────────────────────
    workflow.set_entry_point("ingest_document")

    
    workflow.add_edge("ingest_document", "index_document")
    workflow.add_edge("index_document", "quality_check")

    # Note: no edge from quality_check here — it uses a conditional edge below

    workflow.add_edge("extract_indicators", "analysis_layer")
    workflow.add_edge("analysis_layer", "assess_confidence")
    workflow.add_edge("assess_confidence", "generate_questions")
    workflow.add_edge("generate_questions", "compile_brief")
    workflow.add_edge("retrieve_context","extract_indicators")
    workflow.add_edge("compile_brief", END)
    workflow.add_edge("handle_failure", END)
    

    # ── Conditional edge — quality_check branches on document_failure ──────
    # route_after_quality_check reads state["document_failure"] and returns
    # one of the two strings below. Both strings must be in this mapping dict.
    # If route_after_quality_check returns a string not in this dict,
    # LangGraph raises a ValueError at runtime — not at compile time.
    workflow.add_conditional_edges(
        "quality_check",              # source node
        route_after_quality_check,    # routing function
        {
            "retrieve_context": "retrieve_context",
            "handle_failure":     "handle_failure",
        }
    )

    return workflow.compile()

# Build once at import time.
# Import this object in Streamlit and in test files:
#   from app.agent.graph import esg_graph
esg_graph = build_graph()
