import logging
import numpy
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from model.clean_text import TextCleaner


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"

def analyze_pdf(filename: str) -> str: 
    """
    Basic PDF analysis that extracts text from the PDF
    Handles single-page PDFs with improved error handling
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"File {filename} not found")
    
    try:
        # Convert PDF to images with specific parameters for better handling
        logger.info(f"Converting PDF: {filename}")
        images = convert_from_path(
            str(file_path),
            first_page=1,
            last_page=1,  # Only process first page
            dpi=300,  # Higher DPI for better quality
        )
        
        if not images:
            raise ValueError("No pages found in PDF")
        
        # Process the first (and only) page
        logger.info("Performing OCR on the page")
        image = images[0]
        
        # Improve image quality for OCR
        image = Image.fromarray(numpy.array(image))
        
        # Configure tesseract for better accuracy
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        logger.info("OCR completed successfully")
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise

