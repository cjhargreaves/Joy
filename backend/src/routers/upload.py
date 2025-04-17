from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import pathlib
import shutil
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the upload directory path
BACKEND_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")

# Create router without a prefix to avoid redirects
router = APIRouter(tags=["upload"])

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        logger.info("=== Starting file upload ===")
        logger.info(f"Received {len(files)} files for upload")
        logger.info(f"Upload directory: {UPLOAD_DIR}")
        
        saved_files = []
        for file in files:
            logger.info(f"Processing file: {file.filename}")
            
            # Get file details for debugging
            file_content = await file.read()
            file_size = len(file_content)
            logger.info(f"File size: {file_size} bytes")
            
            # Create a safe file path
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            logger.info(f"Saving to: {file_path}")
            
            # Save the file
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            saved_files.append(file.filename)
            logger.info(f"Successfully saved {file.filename}")
            
            # Reset file position for potential future reads
            await file.seek(0)
        
        success_message = f"Successfully uploaded {len(saved_files)} files"
        logger.info(success_message)
        logger.info("=== Upload complete ===")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": success_message,
                "files": saved_files
            }
        )
    except Exception as e:
        error_message = f"Error during file upload: {str(e)}"
        logger.error(error_message)
        logger.error("=== Upload failed ===")
        raise HTTPException(status_code=500, detail=error_message)

@router.get("/upload")
async def list_uploads():
    """List all uploaded files"""
    try:
        if not os.path.exists(UPLOAD_DIR):
            return {"files": []}
            
        files = []
        for f in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, f)
            if os.path.isfile(file_path):
                files.append({
                    "name": f,
                    "size": os.path.getsize(file_path)
                })
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

