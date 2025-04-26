import os, sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.llm.query_llm import QueryLLM
from utils.read_config_file import read_config_file

class WebSearchFormatter:
    BASE_PROMPT_FILE = "./src/web_search_formatter/prompts/parse_disease_prompt.txt"
    CONFIG_FILE = "ollama_config.yml"

    def parse_disease(self, text: str) -> str:
        with open(WebSearchFormatter.BASE_PROMPT_FILE, 'r') as file:
            base_prompt = file.read()
        
        config = read_config_file(WebSearchFormatter.CONFIG_FILE)
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