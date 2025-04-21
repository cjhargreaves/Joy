from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, analyze, ocr

import os
import pathlib

BACKEND_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(ocr.router)

@app.get("/")
async def home():
    return {"message": "Welcome"}
