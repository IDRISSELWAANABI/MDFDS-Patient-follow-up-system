from src.text_extraction.pdf_to_text_classic import PDFToText
from src.web_search_formatter.web_search_formatter import WebSearchFormatter
from web_search import DiseaseInformation
from src.extracted_text_formater.extracted_text_formater import ExtractedTextFormatter
from src.llm.generate_followup_questions import FollowupPromptBuilder, FollowupQuestionGenerator
from generate_form import PatientFormSystem
from generate_report import PatientReportGenerator
import time

pdf_file = "/home/balk/Downloads/gen_med_rep_sample.pdf"

parser = PDFToText(
    pdf_file=pdf_file
)
extracted_text = parser.extract_text()

formater = WebSearchFormatter()
json_disease = formater.parse_disease(
    text=extracted_text
)
disease = json_disease["disease"]

disease_info = DiseaseInformation("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")
search_results_list = disease_info.search_disease(disease)["results"]
contents = []
for result in search_results_list:
    content = result["content"]
    contents.append(content)

extracted_text_formater = ExtractedTextFormatter()
formated_extracted_text = extracted_text_formater.format_text(
    text=extracted_text
)

prompt = FollowupPromptBuilder.build(
    extracted_data=formated_extracted_text,
    websearch_results=contents
)
generator = FollowupQuestionGenerator()
questions = generator.generate(prompt)

pfs = PatientFormSystem()    
pfs.set_questions(questions)
    
if pfs.initialize():
    while True:
        print("\nChecking for new form submissions...")
        results_list = pfs.check_for_new_responses()
        if results_list:
            for result_list in results_list:
                generate_rep = PatientReportGenerator()
                report = generate_rep.generate_report(
                    patient_form_data=result_list,
                    disease_search_results=contents
                )
                with open(f"./report/{pfs.form_id}.txt", 'w') as file:
                    file.write(report)
        else:
            time.sleep(30)
            continue
else:
    print("Failed to initialize patient form system.")