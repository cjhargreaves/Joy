from fastapi import APIRouter, HTTPException
from ocr.analyze_pdf import analyze_pdf

router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)

@router.get("/{filename}")
async def analyze_pdf_endpoint(filename: str):
    """
    Endpoint to analyze a PDF file and extract its text
    """
    return analyze_pdf(filename)
