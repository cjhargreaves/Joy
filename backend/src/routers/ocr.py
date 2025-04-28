from fastapi import APIRouter, HTTPException
from typing import List
import os
import logging
from ocr.analyze_pdf import analyze_pdf
from model.clean_text import TextCleaner

router = APIRouter(
    prefix="/ocr",
    tags=["ocr"]
)

logger = logging.getLogger(__name__)

@router.get("/batch")
async def analyze_pdfs_endpoint():
    """
    Endpoint to analyze multiple PDF files, combine their text, and clean it using Claude
    """
    try:
        # Construct the path to uploads directory (it's in the backend folder, parallel to src)
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # go up from routers/src to backend
        upload_dir = os.path.join(current_dir, "uploads")
        all_ocr_text = []
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(upload_dir)]
        
        if not pdf_files:
            raise HTTPException(
                status_code=404,
                detail="No PDF files found in uploads directory"
            )
            
        # Process each PDF file
        for filename in pdf_files:
            try:
                ocr_result = analyze_pdf(filename)
                # Extract raw_text from OCR result
                all_ocr_text.append(ocr_result)
                logger.info(f"Successfully processed {filename}")
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")

                continue
                
        
        return {
            "num_files_processed": len(all_ocr_text),
            "cleaned_data":all_ocr_text 
        }
    except Exception as e:
        logger.error(f"Error in analysis pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents: {str(e)}"
        )

