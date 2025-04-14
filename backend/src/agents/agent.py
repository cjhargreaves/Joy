from langchain_anthropic import ChatAnthropic
from browser_use import Agent
import asyncio

# Initialize the model
class EMRFormFiller:
    def __init__(self):
        self.url = "https://v0-mock-emr-page.vercel.app/"
    
    async def fill_form(self, patient_data):
        """
        Fill the EMR form with the provided patient data
        
        Args:
            patient_data (Dict[str, Any]): JSON data containing patient information
        """
        # Initialize the model
        llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            temperature=0.0,
            timeout=100, # Increase for complex tasks
        )

        initial_actions = [
            {'open_tab': {'url': self.url}},
        ]

        data = patient_data["cleaned_data"]

        task = f"""
        please on the opened tab click Create New Patient Intake
        Then you are now going to use the json passed to input data into this EMR form,
        These are going to be the field name, index, and the data to put in

        Document Type: {data['document_type']}

        Full Name: {data['patient_info']['name']}
        Date of Birth: {data['patient_info']['dob']}
        Patient ID: {data['patient_info']['id']}

        Provider Name: {data['provider_info']['name']}
        Facility: {data['provider_info']['facility']}
        Contact: {data['provider_info']['contact']}

        Diagnosis: {data['clinical_info']['diagnosis']}
        
        Context for adding Medication: Make sure to click Add Medication iteration of the loop
        Medication Name: {[med['name'] for med in data['clinical_info']['medications']]}
        Medication Dosage: {[med['dosage'] for med in data['clinical_info']['medications']]}
        Medication Instructions: {[med['instructions'] for med in data['clinical_info']['medications']]}

        Vital Sign Blood Pressure: {data['clinical_info']['vital_signs']['blood_pressure']}
        Vital Sign Heart Rate: {data['clinical_info']['vital_signs']['heart_rate']}
        Vital Sign Temperature: {data['clinical_info']['vital_signs']['temperature']}
        """
        # Create agent with the model
        agent = Agent(
            task = task,
            initial_actions = initial_actions,
            llm=llm

        )

        await agent.run()
        await asyncio.sleep(10)


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

