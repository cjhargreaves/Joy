from fastapi import APIRouter, HTTPException, Body
import logging
from typing import List
from ocr.analyze_pdf import analyze_pdf

router = APIRouter(
    prefix="/ocr",
    tags=["ocr"]
)

logger = logging.getLogger(__name__)

@router.post("/batch")
async def get_ocr_text_batch(filenames: List[str] = Body(...)):
    """
    Endpoint to get OCR text from multiple PDF files
    """
    results = []
    errors = []

    for filename in filenames:
        try:
            ocr_text = analyze_pdf(filename)
            results.append({
                "filename": filename,
                "ocr_text": ocr_text,
                "status": "success"
            })
        except FileNotFoundError:
            errors.append({
                "filename": filename,
                "error": f"File not found",
                "status": "error"
            })
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}")
            errors.append({
                "filename": filename,
                "error": f"Error processing PDF: {str(e)}",
                "status": "error"
            })

    return {
        "results": results,
        "errors": errors
    }

