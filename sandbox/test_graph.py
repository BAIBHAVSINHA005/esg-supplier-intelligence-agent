from app.agent.graph import esg_graph


def make_initial_state(supplier_name: str, document_failure: bool = False) -> dict:
    """
    Helper that builds a fully-initialised state dict.
    Every TypedDict field must be present at invoke() time.
    Build this function now — you will reuse it in every test.
    """
    return {
        # Input
        "assessment_id":    "test-001",
        "supplier_name":    supplier_name,
        "source_filename":  "test_brsr.pdf",
        "document_bytes":   b"",

        # Ingestion
        "document_text":    "",
        "document_chunks":  [],
        "num_pages":        0,

        # Quality check
        "is_machine_readable":        False,
        "brsr_section_found":         False,
        "brsr_section_text":          "",
        "extraction_confidence_score": 0.0,
        "document_failure":           document_failure,
        "document_failure_reason":    None,

        # Extraction
        "extracted_indicators": {},

        # Analysis
        "scope3_verdict":       {},
        "completeness_results": [],
        "gaps":                 [],

        # Confidence
        "confidence_level":    "low",
        "confidence_directive": "",
        "hitl_flag":           False,
        "uncertain_fields":    [],

        # Output
        "followup_questions": [],
        "brief":              None,
        "error":              None,
    }



if __name__ == "__main__":

    # ── Test 1: Happy path (document_failure stays False after quality_check) ──
    print("\n" + "=" * 60)
    print("TEST 1: Happy path — all nodes should run")
    print("=" * 60)
    result = esg_graph.invoke(make_initial_state("Infosys Limited"))

    print("\nFINAL STATE — selected fields:")
    print(f"  brief.header.supplier_name : {result['brief']['header']['supplier_name']}")
    print(f"  confidence_level           : {result['confidence_level']}")
    print(f"  scope3_verdict.level       : {result['scope3_verdict']['level']}")
    print(f"  hitl_flag                  : {result['hitl_flag']}")
    print(f"  brief.status               : {result['brief']['status']}")

    # ── Test 2: Failure path (pre-set document_failure=True) ──
    # Note: In this placeholder, quality_check always returns document_failure=False.
    # To test the failure path, we pre-set it in the initial state AND it will be
    # overwritten to False by quality_check. To genuinely test failure routing,
    # temporarily change quality_check to return document_failure=True.
    #
    # Alternatively, test the routing function directly:
    from app.agent.edges.routing import route_after_quality_check
    print("\n" + "=" * 60)
    print("TEST 2: Routing function unit test")
    print("=" * 60)
    route_on_failure = route_after_quality_check({"document_failure": True})
    route_on_success = route_after_quality_check({"document_failure": False})
    print(f"  document_failure=True  → {route_on_failure}")   # expect: handle_failure
    print(f"  document_failure=False → {route_on_success}")   # expect: extract_indicators