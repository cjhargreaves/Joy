import os
import json
from typing import Dict, Any
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize Claude client
claude = anthropic.Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY')
)

class TextCleaner:
    """Handles cleaning and structuring of OCR text using Claude"""
    
    @staticmethod
    def clean_medical_text(texts: list[str]) -> Dict[str, Any]:
        """
        Process multiple OCR text using Claude to extract structured medical information
        
        Args:
            text (list[str]): Raw OCR text from the PDF
            
        Returns:
            Dict[str, Any]: Structured JSON with medical information
        """
        # Prompt engineering for Claude
        prompt = f"""
        Please analyze this medical document text and extract key information into a structured format.
        Format the response as a JSON object with the following schema:
        {{
            "document_type": "Type of medical document (e.g., prescription, lab report, clinical notes)",
            "patient_info": {{
                "name": "Patient's full name if present",
                "dob": "Date of birth if present",
                "id": "Any patient ID numbers"
            }},
            "provider_info": {{
                "name": "Healthcare provider's name",
                "facility": "Healthcare facility name",
                "contact": "Contact information"
            }},
            "clinical_info": {{
                "diagnosis": ["List of diagnoses"],
                "medications": [
                    {{
                        "name": "Medication name",
                        "dosage": "Dosage information",
                        "instructions": "Usage instructions"
                    }}
                ],
                "vital_signs": {{
                    "blood_pressure": "BP reading if present",
                    "heart_rate": "HR if present",
                    "temperature": "Temp if present"
                }}
            }},
            "date_of_service": "Date of service/visit",
            "additional_notes": "Any other relevant information"
        }}

        Here's the text to analyze:
        {texts}

        Return only the JSON object, no additional text. If any field is not found in the document, use null instead of empty strings.
        """

        try:
            # Get Claude's response
            response = claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,  # Reduced to be within Claude-3's limits
                temperature=0.2,  # Lower temperature for more consistent JSON output
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract and parse the JSON response
            cleaned_data = json.loads(response.content[0].text)
            return cleaned_data
            
        except Exception as e:
            raise Exception(f"Error processing text with Claude: {str(e)}")
