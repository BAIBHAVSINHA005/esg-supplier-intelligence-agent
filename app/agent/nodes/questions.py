from app.agent.state import AssessmentState


QUESTION_LIBRARY = {
    "G-01": (
        "Please provide Scope 3 greenhouse gas emissions data, "
        "including categories covered, reporting boundary, "
        "calculation methodology, and latest reporting period."
    ),
    "G-02": (
        "Please identify the greenhouse gas accounting methodology "
        "used for emissions reporting (for example GHG Protocol, "
        "ISO 14064-1, or equivalent standard)."
    ),
    "G-03": (
        "Please provide the missing Principle 6 environmental "
        "disclosures, including energy consumption, Scope 1 and "
        "Scope 2 emissions, water consumption, waste generation, "
        "and related environmental performance indicators."
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