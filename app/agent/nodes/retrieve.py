# app/agent/nodes/retrieve.py

from app.agent.state import AssessmentState
from app.rag.retriever import retrieve_chunks

def retrieve_context(state: AssessmentState) -> dict:
    print("[retrieve_context]")

    results = retrieve_chunks(
        query="""
        Scope 1 emissions
        Scope 2 emissions
        Scope 3 emissions
        greenhouse gas
        GHG methodology
        climate target
        carbon emissions
        tCO2e
        """,
        k=10
    )

    docs = results.get("documents", [[]])[0]

    print(
        f"[retrieve_context] Retrieved {len(docs)} chunks"
    )

   

    return {
        "retrieved_context": results
    }