from fastapi import APIRouter, UploadFile, File
import os
import pathlib

# Get the upload directory path
BACKEND_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("/")
async def upload_files(files: list[UploadFile] = File(...)):
    print(f"Received upload request for {len(files)} files")
    
    for file in files:
        contents = await file.read()
        print(f"File {file.filename}: {len(contents)} bytes")
        
        safe_filename = pathlib.Path(file.filename).name  # Get just the filename part, no path
        file_path = pathlib.Path(UPLOAD_DIR) / safe_filename
        
        try:
            file_path.relative_to(UPLOAD_DIR)
        except ValueError:
            return {"error": "Invalid file path"}, 400
            
        file_path.write_bytes(contents)
        await file.seek(0)
    
    return {"message": f"Successfully received {len(files)} files"}

@router.get("/")
async def list_uploads():
    """List all uploaded files"""
    files = []
    for f in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, f)
        if os.path.isfile(file_path):
            files.append({
                "name": f,
            })
    return {"files": files}

