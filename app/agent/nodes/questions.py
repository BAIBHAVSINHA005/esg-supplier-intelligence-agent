from app.agent.state import AssessmentState


QUESTION_LIBRARY = {
    "G-01": (
        "Your uploaded BRSR filing does not provide a usable Scope 3 emissions "
        "inventory. Please provide the latest Scope 3 emissions data, including "
        "the reporting period, organisational and operational boundary, categories "
        "covered, calculation methodology, and supporting calculation evidence."
    ),
    "G-02": (
        "Your uploaded BRSR filing does not identify the methodology used for GHG "
        "reporting. Please confirm the applicable standard or protocol, reporting "
        "period and boundary, emissions factors used, and any assurance or supporting "
        "documentation available for buyer ESG due diligence."
    ),
    "G-03": (
        "Your uploaded BRSR filing contains limited Principle 6 environmental "
        "disclosures. Please provide the latest reporting-period data and supporting "
        "evidence for energy consumption, Scope 1 and Scope 2 emissions, water "
        "consumption, waste generation, and the reporting boundary for each metric."
    ),
}


def generate_questions(state: AssessmentState) -> dict:
    """
    Generate supplier-facing follow-up questions from detected gaps.

    Inputs:
        state["gaps"]

    Outputs:
        followup_questions
    """

    gaps = state.get("gaps", [])

    print(
        f"[generate_questions] Building follow-up questions from "
        f"{len(gaps)} gap(s)"
    )

    questions = []

    for gap in gaps:

        gap_id = gap.get("gap_id")

        question_text = QUESTION_LIBRARY.get(
            gap_id,
            (
                "Please provide additional information regarding "
                f"the identified disclosure gap: {gap.get('gap_name')}."
            ),
        )

        questions.append(
            {
                "rank": gap.get("rank", len(questions) + 1),
                "gap_id": gap_id,
                "gap_name": gap.get("gap_name"),
                "question": question_text,
            }
        )

    print(
        f"[generate_questions] Generated "
        f"{len(questions)} follow-up question(s)"
    )

    return {
        "followup_questions": questions
    }
