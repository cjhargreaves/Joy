import logging
import os
from pathlib import Path
from pdf2image import convert_from_path
from google.cloud import vision
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"

def init_vision_client():
    """Initialize and test the Vision API client"""
    try:
        # Print the credentials path to verify it's correct
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        logger.info(f"Using Google Cloud credentials from: {creds_path}")
        
        # Initialize the Vision client
        client = vision.ImageAnnotatorClient()
        logger.info("Successfully initialized Vision client!")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Vision client: {str(e)}")
        raise

def perform_ocr_on_image(client, image_path):
    """
    Perform OCR on a single image using Google Cloud Vision
    """
    try:
        # Read the image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        # Create vision image object
        image = vision.Image(content=content)
        
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            logger.warning("No text detected in the image")
            return ""
            
        # The first text annotation contains all the text in the image
        full_text = texts[0].description
        
        if response.error.message:
            raise Exception(
                f'{response.error.message}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'
            )
            
        return full_text.strip()
        
    except Exception as e:
        logger.error(f"Error performing OCR on image: {str(e)}")
        raise

def analyze_document(filename: str) -> str: 
    """
    Analyzes both PDF and image files to extract text using Google Cloud Vision
    Handles single-page documents with improved error handling
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"File {filename} not found")
    
    try:
        logger.info(f"Processing document: {filename}")
        
        # Initialize Vision client
        client = init_vision_client()
        
        # Check if file is PDF or image
        is_pdf = filename.lower().endswith('.pdf')
        
        if is_pdf:
            # Convert PDF to images
            logger.info(f"Converting PDF: {filename}")
            images = convert_from_path(
                str(file_path),
                first_page=1,
                last_page=1,  # Only process first page
                dpi=300,  # Higher DPI for better quality
            )
            
            if not images:
                raise ValueError("No pages found in PDF")
            
            # Save the first page temporarily
            temp_image_path = UPLOAD_DIR / f"temp_{filename}.jpg"
            images[0].save(temp_image_path, 'JPEG')
            
            # Perform OCR on the temporary image
            text = perform_ocr_on_image(client, temp_image_path)
            
            # Clean up temporary file
            os.remove(temp_image_path)
        else:
            # Process image directly
            text = perform_ocr_on_image(client, file_path)
        
        logger.info("OCR completed successfully")
        return text
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

