"""FastAPI application entry point."""

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.api.schemas import AssessmentEnvelope
from app.services.supplier_assessment import run_supplier_assessment


app = FastAPI(
    title="Supplier ESG Intelligence API",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Report whether the API process is available."""
    return {
        "status": "ok",
        "service": "supplier-esg-intelligence-api",
    }


@app.post("/v1/assessments", response_model=AssessmentEnvelope)
def create_supplier_assessment(
    file: UploadFile = File(...),
    supplier_name: str = Form(""),
) -> AssessmentEnvelope:
    """Run a supplier assessment for an uploaded PDF."""
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    allowed_content_types = {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    }
    if not filename.lower().endswith(".pdf") or (
        file.content_type and file.content_type.lower() not in allowed_content_types
    ):
        raise HTTPException(status_code=400, detail="A PDF upload is required.")

    try:
        pdf_bytes = file.file.read()
        result = run_supplier_assessment(
            pdf_bytes=pdf_bytes,
            supplier_name=supplier_name,
            source_filename=filename,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="The supplier assessment could not be completed.",
        ) from None

    return AssessmentEnvelope(
        brief=result.get("brief"),
        error=result.get("error"),
    )
