from fastapi import APIRouter, HTTPException
import logging
from ocr.analyze_pdf import analyze_pdf
from model.clean_text import TextCleaner

router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)

logger = logging.getLogger(__name__)

@router.get("/{filename}")
async def analyze_pdf_endpoint(filename: str):
    """
    Endpoint to analyze a PDF file, extract its text, and clean it using Claude
    """
    try:
        # First get the OCR results
        ocr_result = analyze_pdf(filename)
        
        # Log the OCR results
        logger.info("OCR Results:")
        logger.info(ocr_result)
        
        # Clean the extracted text using Claude
        cleaner = TextCleaner()
        cleaned_data = cleaner.clean_medical_text(ocr_result["raw_text"])
        
        # Log the cleaned data
        logger.info("Cleaned Data Structure:")
        logger.info(cleaned_data)
        
        return {
            "ocr_result": ocr_result,
            "cleaned_data": cleaned_data
        }
    except Exception as e:
        logger.error(f"Error in analysis pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
