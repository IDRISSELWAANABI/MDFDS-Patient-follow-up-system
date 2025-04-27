import streamlit as st
import os
import time
import uuid
import shutil
from pathlib import Path

# Import your system
from src.text_extraction.pdf_to_text_classic import PDFToText
from src.web_search_formatter.web_search_formatter import WebSearchFormatter
from web_search import DiseaseInformation
from src.extracted_text_formater.extracted_text_formater import ExtractedTextFormatter
from src.llm.generate_followup_questions import FollowupPromptBuilder, FollowupQuestionGenerator
from generate_form import PatientFormSystem
from generate_report import PatientReportGenerator

# Setup directories
UPLOAD_DIR = Path("database/uploads")
REPORT_DIR = Path("database/reports")
PATIENTS_DIR = Path("database/patients")
for directory in [UPLOAD_DIR, REPORT_DIR, PATIENTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Helper to process a patient
def process_patient(pdf_path, patient_name, patient_email):
    parser = PDFToText(pdf_file=str(pdf_path))
    extracted_text = parser.extract_text()

    formater = WebSearchFormatter()
    json_disease = formater.parse_disease(text=extracted_text)
    disease = json_disease["disease"]

    disease_info = DiseaseInformation("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")
    search_results_list = disease_info.search_disease(disease)["results"]
    contents = [result["content"] for result in search_results_list]

    extracted_text_formater = ExtractedTextFormatter()
    formated_extracted_text = extracted_text_formater.format_text(text=extracted_text)

    prompt = FollowupPromptBuilder.build(
        extracted_data=formated_extracted_text,
        websearch_results=contents
    )
    generator = FollowupQuestionGenerator()
    questions = generator.generate(prompt)

    pfs = PatientFormSystem()
    pfs.set_questions(questions)

    if pfs.initialize():
        with st.spinner("Waiting for patient to respond..."):
            while True:
                results_list = pfs.check_for_new_responses()
                if results_list:
                    for result_list in results_list:
                        generate_rep = PatientReportGenerator()
                        report = generate_rep.generate_report(
                            patient_form_data=result_list,
                            disease_search_results=contents
                        )
                        patient_folder = PATIENTS_DIR / f"{patient_name}_{pfs.form_id}"
                        patient_folder.mkdir(exist_ok=True)
                        shutil.copy(str(pdf_path), str(patient_folder / "medical_report.pdf"))
                        with open(patient_folder / "generated_report.txt", "w") as f:
                            f.write(report)
                        return  # Done!
                else:
                    time.sleep(10)
    else:
        st.error("Failed to initialize patient form system.")

# Streamlit Pages
st.set_page_config(page_title="Patient Monitoring System", layout="wide")

menu = ["Add Patient", "View Patients"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Add Patient":
    st.title("Add a New Patient")

    with st.form(key="patient_form"):
        patient_name = st.text_input("Patient Name")
        patient_email = st.text_input("Patient Email")
        uploaded_pdf = st.file_uploader("Upload Medical Report (PDF)", type=["pdf"])
        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if patient_name and patient_email and uploaded_pdf:
            patient_id = str(uuid.uuid4())
            save_path = UPLOAD_DIR / f"{patient_id}.pdf"
            with open(save_path, "wb") as f:
                f.write(uploaded_pdf.read())

            st.success("Patient added! Processing...")
            process_patient(save_path, patient_name, patient_email)
            st.success("Patient report generated and saved!")
        else:
            st.error("Please fill all fields and upload a PDF.")

elif choice == "View Patients":
    st.title("Patient List")

    patient_folders = list(PATIENTS_DIR.glob("*"))

    if not patient_folders:
        st.info("No patients found.")
    else:
        for patient_folder in patient_folders:
            with st.expander(patient_folder.name):
                pdf_path = patient_folder / "medical_report.pdf"
                report_path = patient_folder / "generated_report.txt"

                if pdf_path.exists():
                    st.subheader("Medical Report (PDF)")
                    st.download_button("Download Medical Report", data=pdf_path.read_bytes(), file_name=pdf_path.name)

                if report_path.exists():
                    st.subheader("Generated Report")
                    st.text_area("", report_path.read_text(), height=300)
