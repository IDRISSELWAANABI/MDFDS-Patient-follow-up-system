import ollama
import json

class PatientReportGenerator:
    def __init__(self, model_name="gemma3:12b"):
        """
        Initialize the PatientReportGenerator with the specified LLM model.
        
        Args:
            model_name (str): Name of the Ollama model to use (default: gemma3)
        """
        self.model_name = model_name
    
    def generate_report(self, patient_form_data, disease_search_results):
        """
        Generate a comprehensive patient report using the local LLM.
        
        Args:
            patient_form_data (dict): The form data submitted by the patient
            disease_search_results (list): The web search results about the disease
            
        Returns:
            str: Generated patient report
        """
        # Create the prompt for the LLM
        prompt = self._create_prompt(patient_form_data, disease_search_results)
        
        # Call the local Ollama model
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2048
            }
        )
        
        # Extract the generated report from the response
        report = response['response']
        return report
    
    def _create_prompt(self, patient_form_data, disease_search_results):
        """
        Create a prompt for the LLM based on patient data and search results.
        
        Args:
            patient_form_data (dict): The form data submitted by the patient
            disease_search_results (list): The web search results about the disease
            
        Returns:
            str: Formatted prompt for the LLM
        """
        # Convert the patient form data to a readable format
        patient_info = json.dumps(patient_form_data, indent=2)
        
        # Format the search results
        search_info = ""
        for i, result in enumerate(disease_search_results, 1):
            search_info += f"Result {i}:\n"
            if isinstance(result, dict):
                for key, value in result.items():
                    search_info += f"{key}: {value}\n"
            else:
                search_info += f"{result}\n"
            search_info += "\n"
        
        # Create the final prompt
        prompt = f"""
Generate a comprehensive medical report for a patient based on the following information:

## Patient Form Data:
{patient_info}

## Disease Information (Web Search Results):
{search_info}

Instructions:
1. Create a professional medical report summarizing the patient's condition
2. Include relevant insights from the disease information
3. Structure the report with clear sections including background, analysis, and recommendations
4. Use professional medical terminology where appropriate
5. Be concise yet thorough

Report:
"""
        return prompt


# Example usage:
# if __name__ == "__main__":
#     # Sample input data (these would come from your existing inputs)
#     patient_data = {
#         "name": "John Doe",
#         "age": 45,
#         "symptoms": ["persistent cough", "fatigue", "shortness of breath"],
#         "medical_history": "Hypertension, Former smoker (quit 5 years ago)",
#         "current_medications": ["Lisinopril 10mg daily"]
#     }
    
#     disease_info = [
#         {
#             "title": "Chronic Obstructive Pulmonary Disease (COPD)",
#             "content": "COPD is a chronic inflammatory lung disease that causes obstructed airflow from the lungs..."
#         },
#         {
#             "title": "COPD Treatment Options",
#             "content": "Treatment options include bronchodilators, inhaled steroids, pulmonary rehabilitation..."
#         }
#     ]
    
#     # Generate the report
#     generator = PatientReportGenerator()
#     report = generator.generate_report(patient_data, disease_info)
#     print(report)