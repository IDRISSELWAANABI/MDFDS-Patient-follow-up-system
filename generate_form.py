import requests
import json
import os
import time
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

class PatientFormSystem:
    def __init__(self, data_dir="patient_responses"):
        """Initialize the PatientFormSystem with API keys and settings"""
        # Load environment variables
        load_dotenv()
        # self.SENDGRID_API_KEY = "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"
        # self.TYPEFORM_API_KEY = 'tfp_1KA3bCkCw33ZtQkq6NjVLv73yK2PSgDu1FBf6Bk8srQ_3ssoYgYU3Burqm'
        self.SENDGRID_API_KEY = "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"
        self.TYPEFORM_API_KEY = "tfp_2a6h5U6F42fvmW5A84G2YD2kKggtUvESmRWVNtmrza9u_3pYMtD7KMHWAZg"
        # Email settings
        self.FROM_EMAIL = 'technobadr2003@gmail.com'
        self.TO_EMAIL = 'technobadr2003@gmail.com'
        
        # Directory for storing patient responses
        self.DATA_DIR = data_dir
        os.makedirs(self.DATA_DIR, exist_ok=True)
        
        # Track processed responses to avoid duplicates
        self.processed_responses = set()
        
        # Form details
        self.form_url = None
        self.form_id = None
        
        # Questions for the form
        self.questions = []
    
    def set_questions(self, questions):
        """Set the questions for the form"""
        self.questions = questions
    
    def save_response(self, response_data):
        """Save the response data to a file"""
        filename = f"{self.DATA_DIR}/patient_{response_data['response_id']}.json"
        with open(filename, 'w') as f:
            json.dump(response_data, f, indent=4)
        print(f"Data saved to {filename}")
        return filename
    
    def send_email(self):
        """Send an email with the patient form URL using SendGrid"""
        if not self.form_url or not self.form_id:
            print("Form hasn't been created yet. Create form first.")
            return False
            
        html_content = f"""
        <h2>Patient Health Assessment Form</h2>
        <p>A new patient health assessment form has been created.</p>
        <p><strong>Form ID:</strong> {self.form_id}</p>
        <p>Please use the link below to access the form:</p>
        <p><a href="{self.form_url}" target="_blank">Complete Patient Health Assessment</a></p>
        <p>Thank you for your participation!</p>
        """
        
        message = Mail(
            from_email=self.FROM_EMAIL,
            to_emails=self.TO_EMAIL,
            subject='Patient Health Assessment Form',
            html_content=html_content
        )
        
        try:
            sg = SendGridAPIClient(self.SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"Email sent successfully!")
            print(f"Status code: {response.status_code}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def create_form(self):
        """Create a new Typeform for patient health information"""
        if not self.questions:
            print("No questions set. Please set questions using set_questions() method.")
            return None, None
            
        response = requests.post(
            'https://api.typeform.com/forms',
            headers={
                'Authorization': f'Bearer {self.TYPEFORM_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                "title": "Patient Health Assessment",
                "fields": self.questions
            }
        )
        
        data = response.json()
        self.form_url = data['_links']['display']
        self.form_id = data['id']
        
        print(f"Patient form created successfully!")
        print(f"Form URL: {self.form_url}")
        print(f"Form ID: {self.form_id}")
        
        return self.form_url, self.form_id
    
    def process_response(self, item, question_mapping):
        """Process a single response from the Typeform API"""
        response_id = item['token']
        submission_time = datetime.fromisoformat(item['submitted_at'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
        
        # Process the answers
        processed_answers = {}
        raw_answers = item.get('answers', [])
        
        for answer in raw_answers:
            try:
                # Check if field is a dictionary before accessing it
                if isinstance(answer['field'], dict):
                    field_id = answer['field'].get('id')
                else:
                    # If it's not a dictionary, use a fallback approach
                    field_id = str(answer.get('field_id', f"unknown_field_{len(processed_answers)}"))
                
                field_title = question_mapping.get(field_id, f"Question {field_id}")
                
                # Extract answer value based on type
                if answer['type'] == 'text':
                    answer_value = answer['text']
                elif answer['type'] == 'boolean':
                    answer_value = answer['boolean']
                elif answer['type'] == 'number':
                    answer_value = answer['number']
                elif answer['type'] == 'choice':
                    answer_value = answer['choice']['label'] if isinstance(answer.get('choice'), dict) else str(answer.get('choice'))
                elif answer['type'] == 'choices':
                    if isinstance(answer.get('choices'), list):
                        answer_value = [choice.get('label') if isinstance(choice, dict) else str(choice) for choice in answer['choices']]
                    else:
                        answer_value = str(answer.get('choices', 'No choices provided'))
                else:
                    answer_value = f"Unsupported answer type: {answer['type']}"
                
                processed_answers[field_title] = answer_value
            except Exception as e:
                print(f"Error processing an answer: {str(e)}")
                print(f"Problematic answer structure: {json.dumps(answer, indent=2)}")
                # Skip this answer and continue with others
                continue
        
        patient_response = {
            "response_id": response_id,
            "submission_time": submission_time,
            "answers": processed_answers
        }
        
        return patient_response
    
    def get_question_mapping(self):
        """Get a mapping of field IDs to question titles"""
        if not self.form_id:
            print("Form hasn't been created yet. Create form first.")
            return {}
            
        response = requests.get(
            f'https://api.typeform.com/forms/{self.form_id}',
            headers={
                'Authorization': f'Bearer {self.TYPEFORM_API_KEY}'
            }
        )
        
        if response.status_code != 200:
            print(f"Error fetching form definition: {response.status_code}")
            return {}
        
        form_data = response.json()
        
        mapping = {}
        for field in form_data.get('fields', []):
            mapping[field['id']] = field.get('title', f"Field {field['id']}")
        
        return mapping
    
    def check_for_new_responses(self):
        """Check for new form submissions"""
        if not self.form_id:
            print("Form hasn't been created yet. Create form first.")
            return []
            
        # Get question mapping once
        question_mapping = self.get_question_mapping()
        
        response = requests.get(
            f'https://api.typeform.com/forms/{self.form_id}/responses',
            headers={
                'Authorization': f'Bearer {self.TYPEFORM_API_KEY}'
            }
        )
        
        if response.status_code != 200:
            print(f"Error fetching responses: {response.status_code}")
            print(response.text)
            return []
        
        responses_data = response.json()
        items = responses_data.get('items', [])
        
        new_responses = []
        new_responses_found = False
        
        for item in items:
            response_id = item['token']
            
            if response_id in self.processed_responses:
                continue
                
            new_responses_found = True
            try:
                patient_response = self.process_response(item, question_mapping)
                
                self.save_response(patient_response)
                self.processed_responses.add(response_id)
                new_responses.append(patient_response)
                
                # Simplified display format for responses
                print(f"\n=== Patient Response (ID: {response_id}) ===")
                for question, answer in patient_response['answers'].items():
                    print(f"Q: {question}")
                    print(f"A: {answer}")
                    print()
                    
            except Exception as e:
                print(f"Error processing response {response_id}: {str(e)}")
                # Add more detailed error information
                import traceback
                print(f"Detailed error: {traceback.format_exc()}")
        
        if not new_responses_found and len(self.processed_responses) > 0:
            print("No new responses found.")
        elif not items:
            print("No responses received yet.")
            
        return new_responses
    
    def start_monitoring(self, check_interval=30):
        """Start monitoring for new form submissions with a specified interval"""
        if not self.form_id:
            print("Form hasn't been created yet. Create form first.")
            return
            
        try:
            while True:
                print("\nChecking for new form submissions...")
                self.check_for_new_responses()
                print(f"Next check in {check_interval} seconds. Press Ctrl+C to exit.")
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    
    def initialize(self):
        """Initialize the system by creating form and sending email"""
        if not self.questions:
            print("No questions set. Please set questions using set_questions() method.")
            return False
        
        # Create the Typeform
        self.create_form()
        
        print("Patient Form System Ready!")
        print(f"Form URL: {self.form_url}")
        
        # Send email with form URL
        email_sent = self.send_email()
        if email_sent:
            print(f"Email with form URL sent successfully to {self.TO_EMAIL}")
        else:
            print("Failed to send email with form URL")
        
        return True
    

# def main():
#     # Initialize the patient form system
#     pfs = PatientFormSystem()
    
#     # Define the questions for the form
#     questions = [
#         {
#             "ref": "name",
#             "title": "What is your full name?",
#             "type": "short_text",
#             "validations": {"required": True}
#         },
#         {
#             "ref": "age",
#             "title": "What is your age?",
#             "type": "number",
#             "validations": {"required": True}
#         },
#         {
#             "ref": "symptoms",
#             "title": "What symptoms are you experiencing?",
#             "type": "long_text",
#             "validations": {"required": True}
#         },
#         {
#             "ref": "pain_level",
#             "title": "On a scale of 1-10, how would you rate your pain?",
#             "type": "number",
#             "validations": {
#                 "required": True,
#                 "min_value": 1,
#                 "max_value": 10
#             }
#         },
#         {
#             "ref": "medical_history",
#             "title": "Please describe any relevant medical history.",
#             "type": "long_text"
#         }
#     ]
    
#     # Set the questions
#     pfs.set_questions(questions)
    
#     # Initialize the system (creates the form and sends email)
#     if pfs.initialize():
#         # Start monitoring for responses
#         pfs.start_monitoring(check_interval=30)
#     else:
#         print("Failed to initialize patient form system.")

# if __name__ == "__main__":
#     main()