from app.agent.state import AssessmentState


def generate_questions(state: AssessmentState) -> dict:
    """
    PHASE 3 PLACEHOLDER — Real implementation in Phase 3 (Day 20).

    Real responsibility:
    - Read gaps from state (written by analysis_layer)
    - If no gaps: return empty list
    - Build a prompt listing the gaps and asking Claude to generate follow-up questions
    - Apply question generation rules from the PRD:
        * Maximum five questions
        * Priority: Critical gaps first, then Notable, then Minor
        * One question per gap
        * Supplier-facing language (addressed to the supplier, not internal jargon)
        * Each question names the specific missing item
    - Parse Claude's response into the followup_questions list structure
    - Each question links back to its source gap_id

    This node DOES call Claude.
    This node reads: gaps, supplier_name
    This node writes: followup_questions
    """
    print(
    "[generate_questions] PLACEHOLDER — would generate "
    f"follow-up questions from {len(state.get('gaps', []))} gaps"
)
    

    return {
        "followup_questions": []
    }

