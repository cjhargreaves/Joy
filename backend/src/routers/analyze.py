from fastapi import APIRouter, HTTPException
from typing import List
import os
import logging
from ..ocr.analyze_pdf import analyze_document
from ..model.clean_text_noAI import TextCleanerNoAI
from ..agents.agent import EMRFormFiller 

router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)

logger = logging.getLogger(__name__)

@router.get("/all")
async def analyze_pdfs_endpoint():
    """
    Endpoint to analyze multiple PDF files and extract structured information
    """
    try:
        # Construct the path to uploads directory (it's in the backend folder, parallel to src)
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # go up from routers/src to backend
        upload_dir = os.path.join(current_dir, "uploads")
        all_ocr_text = []
        
        # Get all files
        files = [f for f in os.listdir(upload_dir)]
        
        if not files:
            raise HTTPException(
                status_code=404,
                detail="No files found in uploads directory"
            )
            
        # Process each file
        for filename in files:
            try:
                ocr_result = analyze_document(filename)
                all_ocr_text.append(ocr_result)
                logger.info(f"Successfully processed {filename}")
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                continue
                
        if not all_ocr_text:
            raise HTTPException(
                status_code=500,
                detail="Failed to process any files"
            )
            
        # Clean and structure the text using rule-based parsing
        cleaner = TextCleanerNoAI()
        cleaned_data = cleaner.clean_medical_text(all_ocr_text)
        
        # Log the structured data
        logger.info("Structured Data:")
        logger.info(cleaned_data)

        # Optional: Send to EMR form filler
        try:
            agent = EMRFormFiller()
            await agent.fill_form({"cleaned_data": cleaned_data})
        except Exception as e:
            logger.error(f"Error filling EMR form: {str(e)}")
            # Continue even if EMR filling fails
        
        return {
            "num_files_processed": len(all_ocr_text),
            "raw_text": all_ocr_text,  # Include the raw OCR text
            "structured_data": cleaned_data  # Include the structured data
        }
    except Exception as e:
        logger.error(f"Error in analysis pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents: {str(e)}"
        )
