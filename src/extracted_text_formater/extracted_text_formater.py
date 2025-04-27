import os, sys
import json
from typing import Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.llm.query_llm import QueryLLM
from utils.read_config_file import read_config_file
        

class ExtractedTextFormatter:
    BASE_PROMPT_FILE = "./src/extracted_text_formater/prompts/format_extracted_text_prompt.txt"
    CONFIG_FILE = "ollama_config.yml"

    def format_text(self, text: str) -> Dict:
        with open(ExtractedTextFormatter.BASE_PROMPT_FILE, 'r') as file:
            base_prompt = file.read()
        
        config = read_config_file(ExtractedTextFormatter.CONFIG_FILE)
        model, temperature = config.get("model"), config.get("temperature")
        if model is None or temperature is None:
            raise ValueError("Model and temperature must be specified in the configuration file.")

        prompt = base_prompt.format(text)

        llm = QueryLLM(
            model=model,
            temperature=temperature
        )
        response = llm.query(
            prompt=prompt
        )
        if response is None:
            raise ValueError("LLM returned no response.")

        try:
            json_response = json.loads(response)
            return json_response
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    

if __name__ == "__main__":
    from src.text_extraction.pdf_to_text_classic import PDFToText

    pdf_file = "/home/balk/Downloads/gen_med_rep_sample.pdf"

    parser = PDFToText(
        pdf_file=pdf_file
    )
    extracted_text = parser.extract_text()
    formatter = ExtractedTextFormatter()
    formatted_text = formatter.format_text(
        text=extracted_text
    )
    print(formatted_text)
    print(type(formatted_text))