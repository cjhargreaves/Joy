from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import logging
from ..ocr.analyze_pdf import analyze_document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["ocr"])

@router.get("/ocr")
async def process_document():
    """
    Process the most recently uploaded file using OCR
    """
    try:
        # Get the upload directory path
        upload_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/uploads"
        
        # Get the most recent file
        files = os.listdir(upload_dir)
        if not files:
            raise HTTPException(status_code=404, detail="No files found in uploads directory")
        
        # Sort files by modification time (most recent first)
        latest_file = max(
            [os.path.join(upload_dir, f) for f in files],
            key=os.path.getmtime
        )
        latest_filename = os.path.basename(latest_file)
        
        logger.info(f"Processing latest file: {latest_filename}")
        
        # Perform OCR
        extracted_text = analyze_document(latest_filename)
        
        # Split the text into lines for better readability
        text_lines = extracted_text.split('\n')
        
        return JSONResponse(
            status_code=200,
            content={
                "filename": latest_filename,
                "text": text_lines,  # Return as array of lines for better readability
                "raw_text": extracted_text  # Also include the raw text
            }
        )
        
    except Exception as e:
        error_message = f"Error processing document: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message) 