# app/agent/nodes/retrieve.py

from app.agent.state import AssessmentState
from app.rag.retriever import retrieve_chunks


# ------------------------------------------------------------------
# Indicator-specific semantic retrieval queries
# One query per Principle 6 indicator.
# These queries will be used in MVP-3 to retrieve the most relevant
# document chunks before LLM extraction.
# ------------------------------------------------------------------

INDICATOR_QUERIES = {
    "e6_energy_consumption": """
        energy consumption
        total energy
        energy use
        gigajoule
        terajoule
    """,

    "e6_scope1_emissions": """
        Scope 1 emissions
        direct greenhouse gas emissions
        direct GHG
        tCO2e
    """,

    "e6_scope2_emissions": """
        Scope 2 emissions
        indirect greenhouse gas emissions
        purchased electricity
        tCO2e
    """,

    "e6_scope3_emissions": """
        Scope 3 emissions
        upstream emissions
        downstream emissions
        value chain emissions
        purchased goods
        business travel
        employee commuting
        tCO2e
    """,

    "e6_ghg_methodology": """
        GHG Protocol
        greenhouse gas methodology
        ISO 14064
        IPCC
        emission factor
        global warming potential
    """,

    "e6_ghg_intensity": """
        GHG intensity
        emission intensity
        carbon intensity
        tCO2e per
        emission per unit
    """,

    "e6_climate_target": """
        climate target
        net zero
        carbon neutral
        science based target
        SBTi
        emission reduction target
    """,

    "e6_water_consumption": """
        water consumption
        water withdrawal
        water usage
        kilolitre
        water intensity
    """,

    "e6_waste_generated": """
        waste generated
        hazardous waste
        non-hazardous waste
        waste management
        waste disposed
    """,
}


def retrieve_context(state: AssessmentState) -> dict:
    print("[retrieve_context]")

    retrieved_context = {}

    for indicator_id, query in INDICATOR_QUERIES.items():

        print(f"[retrieve_context] Retrieving context for {indicator_id}")

        results = retrieve_chunks(
            query=query,
            k=5
        )

        docs = results.get("documents", [[]])[0]

        print(
            f"[retrieve_context] {indicator_id}: Retrieved {len(docs)} chunk(s)"
        )

        retrieved_context[indicator_id] = results

    print(
        f"[retrieve_context] Completed retrieval for {len(retrieved_context)} indicators"
    )

    return {
        "retrieved_context": retrieved_context
    }