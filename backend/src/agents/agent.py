from playwright.async_api import async_playwright
import asyncio

# Initialize the model
class EMRFormFiller:
    def __init__(self):
        self.url = "https://v0-mock-emr-page.vercel.app/"
    
    async def fill_form(self, patient_data):
        """
        Fill the EMR form with the provided patient data using Playwright
        
        Args:
            patient_data (Dict[str, Any]): JSON data containing patient information
        """

        data = patient_data["cleaned_data"]

        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Navigate to the URL
            await page.goto(self.url)
            
            # Click Create New Patient Intake button
            await page.click('text="Create New Patient Record"')
            
            # Fill in Document Type
            await page.fill('#document_type', data['document_type'])
            
            # Fill Patient Information
            await page.fill('#patient_name', data['patient_info']['name'])
            await page.fill('#patient_dob', data['patient_info']['dob'])
            await page.fill('#patient_id', data['patient_info']['id'])

            # Fill Provider Information
            await page.fill('#provider_name', data['provider_info']['name'])
            await page.fill('#provider_facility', data['provider_info']['facility'])
            await page.fill('#provider_contact', data['provider_info']['contact'])
            
            
            # Fill Clinical Information
            diagnosis_data = data['clinical_info']['diagnosis']
            if isinstance(diagnosis_data, list):
                await page.fill('#diagnosis', "\n".join(diagnosis_data))
            else:
                await page.fill('#diagnosis', str(diagnosis_data))
            
            # Fill Medications
            count = 0
            for medication in data['clinical_info']['medications']:
                await page.click('text="Add Medication"')
                await page.fill(f'#med_name_{count}', medication['name'])
                await page.fill(f'#med_dosage_{count}', medication['dosage'])
                await page.fill(f'#med_instructions_{count}', medication['instructions'])
                count += 1
            
            # Fill Vital Signs
            await page.fill('#blood_pressure', data['clinical_info']['vital_signs']['blood_pressure'])
            await page.fill('#heart_rate', data['clinical_info']['vital_signs']['heart_rate'])
            await page.fill('#temperature', data['clinical_info']['vital_signs']['temperature'])
            
            # Fill Date of Service with today's date
            await page.fill('#date_of_service', data['date_of_service'])
            await page.fill('#additional_notes', data['additional_notes'])

            # Wait for a moment to see the filled form
            await asyncio.sleep(20)
            
            # Close the browser
            await browser.close()


async def main():
    # Mock patient data that matches the expected structure
    mock_data = {
        "cleaned_data": {
            "document_type": "Initial Assessment",
            "patient_info": {
                "name": "John Doe",
                "dob": "1990-01-01",
                "id": "P12345"
            },
            "provider_info": {
                "name": "Dr. Sarah Smith",
                "facility": "General Hospital",
                "contact": "555-0123"
            },
            "clinical_info": {
                "diagnosis": "Hypertension",
                "medications": [
                    {
                        "name": "Lisinopril",
                        "dosage": "10mg",
                        "instructions": "Take once daily"
                    },
                    {
                        "name": "Amlodipine",
                        "dosage": "5mg",
                        "instructions": "Take in the morning"
                    }
                ],
                "vital_signs": {
                    "blood_pressure": "120/80",
                    "heart_rate": "72",
                    "temperature": "98.6"
                }
            }
        }
    }

    # Create an instance of EMRFormFiller
    form_filler = EMRFormFiller()
    
    # Run the form filler with mock data
    try:
        await form_filler.fill_form(mock_data)
        print("Form filling completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

