from copy import deepcopy
from typing import Any

from fastapi.testclient import TestClient

import app.api.main as api_main


client = TestClient(api_main.app)


def _header() -> dict[str, Any]:
    return {
        "supplier_name": "Example Supplier",
        "source_filename": "supplier.pdf",
        "assessment_id": "test-001",
        "generated_at": "2026-08-27T12:00:00",
        "confidence_level": "high",
        "confidence_directive": "Suitable for preliminary review.",
        "hitl_flag": False,
    }


def _success_brief() -> dict[str, Any]:
    return {
        "executive_summary": "Example Supplier's BRSR was assessed.",
        "disclaimer": "Based solely on the uploaded BRSR filing.",
        "header": _header(),
        "completeness_assessment": [
            {
                "principle_number": 6,
                "principle_name": "Environment",
                "state": "partial",
                "citation": "Principle 6, Section C",
                "essential_total": 8,
                "essential_disclosed": 6,
                "essential_partial": 1,
                "essential_not_found": 1,
                "essential_unassessed": 0,
                "partial_indicators": ["e6_water_consumption"],
                "not_found_indicators": ["e6_climate_target"],
                "unassessed_indicators": [],
                "leadership_disclosed": ["e6_scope3_emissions"],
            }
        ],
        "scope3_verdict": {
            "level": "scope3_ready",
            "level_number": 3,
            "label": "Scope 3 Ready",
            "evidence": "Scope 3 emissions were 1,250 tCO2e.",
            "citation": "Page 42",
            "maturity_signals": {
                "assurance": "not_assessed",
                "category_boundary": "found",
                "sbti": "not_found",
                "significant_partners": "not_assessed",
                "trend_data": "not_assessed",
            },
        },
        "scope3_assessment_narrative": "Scope 3 is usable as a preliminary input.",
        "confidence_explanation": "Overall confidence is High.",
        "gaps": [
            {
                "rank": 1,
                "gap_id": "G-05",
                "gap_name": "Climate target not disclosed",
                "brsr_reference": "Principle 6",
                "severity": "critical",
                "description": "No climate target was identified.",
                "citation": "Principle 6 checked",
            }
        ],
        "gap_references": {"G-05": "Principle 6 checked"},
        "recommended_actions": [
            {
                "rank": 1,
                "gap_id": "G-05",
                "gap_name": "Climate target not disclosed",
                "action": "Request climate target details.",
            }
        ],
        "procurement_recommendations": [
            {
                "rank": 1,
                "gap_id": "G-05",
                "gap_name": "Climate target not disclosed",
                "severity": "critical",
                "recommendation": "Request climate target details.",
                "basis": "No climate target was identified.",
                "reference": "Principle 6 checked",
            }
        ],
        "followup_questions": [
            {
                "rank": 1,
                "gap_id": "G-05",
                "gap_name": "Climate target not disclosed",
                "question": "Please provide current climate target details.",
                "linked_gap_id": "G-05",
                "basis": "No climate target was identified.",
                "citation": "Principle 6 checked",
                "reference": "Principle 6 checked",
            }
        ],
        "question_references": {"G-05": "Principle 6 checked"},
        "uncertain_fields": [],
        "extraction_errors": [],
        "evidence_register": [
            {
                "indicator_id": "e6_scope3_emissions",
                "indicator_name": "Scope 3 GHG Emissions",
                "state": "disclosed",
                "value": "1,250 tCO2e",
                "evidence_excerpt": "Scope 3 emissions were 1,250 tCO2e.",
                "citation": "Page 42",
                "raw_citation": "Page 42",
                "assessment_reference": "Principle 6, Leadership Indicator",
                "evidence_status": "source_matched",
                "source_locations": [
                    {
                        "page": 42,
                        "chunk_id": "chunk-42",
                        "retrieval_rank": 1,
                        "distance": 0.08,
                    }
                ],
                "extraction_method": "llm",
                "extraction_confidence": 0.95,
                "error_code": None,
            }
        ],
        "status": "brief_generated",
    }


def _failure_brief() -> dict[str, Any]:
    header = _header()
    header.update(
        confidence_level="low",
        confidence_directive="Do not use this output for a decision.",
        hitl_flag=True,
    )
    return {
        "executive_summary": "The assessment could not be completed.",
        "disclaimer": "Document processing failed.",
        "header": header,
        "error": "The uploaded document could not be assessed.",
        "completeness_assessment": [],
        "scope3_verdict": None,
        "scope3_assessment_narrative": "Scope 3 could not be assessed.",
        "confidence_explanation": "Low confidence because processing failed.",
        "gaps": [],
        "gap_references": {},
        "recommended_actions": [],
        "followup_questions": [],
        "question_references": {},
        "extraction_errors": [],
        "evidence_register": [],
    }


def _post() -> Any:
    return client.post(
        "/v1/assessments",
        files={"file": ("supplier.pdf", b"%PDF-test", "application/pdf")},
    )


def test_successful_pdf_upload(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}
    brief = _success_brief()

    def fake_assessment(**kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {"brief": brief, "error": None}

    monkeypatch.setattr(api_main, "run_supplier_assessment", fake_assessment)
    response = client.post(
        "/v1/assessments",
        files={"file": ("supplier.pdf", b"%PDF-test", "application/pdf")},
        data={"supplier_name": "Example Supplier"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["brief"]["header"] == brief["header"]
    assert body["brief"]["scope3_verdict"]["level"] == "scope3_ready"
    assert body["brief"]["evidence_register"] == brief["evidence_register"]
    assert body["brief"]["status"] == "brief_generated"
    assert body["error"] is None
    assert captured == {
        "pdf_bytes": b"%PDF-test",
        "supplier_name": "Example Supplier",
        "source_filename": "supplier.pdf",
    }


def test_supplier_name_defaults_to_blank(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_assessment(**kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {"brief": _success_brief(), "error": None}

    monkeypatch.setattr(api_main, "run_supplier_assessment", fake_assessment)
    assert _post().status_code == 200
    assert captured["supplier_name"] == ""


def test_non_pdf_upload_is_rejected(monkeypatch: Any) -> None:
    def unexpected_assessment(**kwargs: Any) -> dict[str, Any]:
        raise AssertionError("Assessment service should not be called")

    monkeypatch.setattr(api_main, "run_supplier_assessment", unexpected_assessment)
    response = client.post(
        "/v1/assessments",
        files={"file": ("notes.txt", b"not a PDF", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "A PDF upload is required."}


def test_structured_document_failure_returns_200(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        api_main,
        "run_supplier_assessment",
        lambda **kwargs: {
            "brief": _failure_brief(),
            "error": "The uploaded document could not be assessed.",
        },
    )
    response = _post()

    assert response.status_code == 200
    body = response.json()
    assert body["brief"]["scope3_verdict"] is None
    assert body["brief"]["procurement_recommendations"] == []
    assert body["brief"]["uncertain_fields"] == []
    assert body["error"] == "The uploaded document could not be assessed."


def test_extraction_error_unassessed_result_returns_200(monkeypatch: Any) -> None:
    brief = deepcopy(_success_brief())
    brief["header"]["confidence_level"] = "low"
    brief["header"]["hitl_flag"] = True
    brief["scope3_verdict"] = {
        "level": "unassessed",
        "level_number": None,
        "label": "Unassessed due to extraction error",
        "evidence": "Scope 3 extraction timed out.",
        "citation": "Principle 6, Leadership Indicator",
        "maturity_signals": {
            "assurance": "not_assessed",
            "category_boundary": "not_assessed",
            "sbti": "not_found",
            "significant_partners": "not_assessed",
            "trend_data": "not_assessed",
        },
    }
    brief["extraction_errors"] = [
        {
            "indicator_id": "e6_scope3_emissions",
            "indicator_name": "Scope 3 GHG Emissions",
            "error_code": "timeout_error",
            "error_message": "Scope 3 extraction timed out.",
            "citation": "Principle 6, Leadership Indicator",
        }
    ]
    brief["evidence_register"] = [
        {
            "indicator_id": "e6_scope3_emissions",
            "indicator_name": "Scope 3 GHG Emissions",
            "state": "extraction_error",
            "value": None,
            "evidence_excerpt": None,
            "citation": "Principle 6, Leadership Indicator",
            "raw_citation": "Principle 6, Leadership Indicator",
            "assessment_reference": "Principle 6, Leadership Indicator",
            "evidence_status": "extraction_error",
            "source_locations": [],
            "extraction_method": "llm",
            "extraction_confidence": 0.0,
            "error_code": "timeout_error",
        }
    ]
    monkeypatch.setattr(
        api_main,
        "run_supplier_assessment",
        lambda **kwargs: {"brief": brief, "error": None},
    )
    response = _post()

    assert response.status_code == 200
    body = response.json()["brief"]
    assert body["scope3_verdict"]["level"] == "unassessed"
    assert body["scope3_verdict"]["level_number"] is None
    assert body["extraction_errors"][0]["error_code"] == "timeout_error"
    assert body["evidence_register"][0]["source_locations"] == []


def test_unexpected_service_exception_returns_safe_500(monkeypatch: Any) -> None:
    def failing_assessment(**kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("private implementation detail")

    monkeypatch.setattr(api_main, "run_supplier_assessment", failing_assessment)
    response = _post()

    assert response.status_code == 500
    assert response.json() == {
        "detail": "The supplier assessment could not be completed."
    }
    assert "private implementation detail" not in response.text


def test_openapi_exposes_named_brief_fields() -> None:
    schemas = api_main.app.openapi()["components"]["schemas"]

    assert "FinalBrief" in schemas
    assert "BriefHeader" in schemas
    assert "EvidenceEntry" in schemas
    assert "completeness_assessment" in schemas["FinalBrief"]["properties"]
    assert "scope3_verdict" in schemas["FinalBrief"]["properties"]
    assert "evidence_register" in schemas["FinalBrief"]["properties"]
