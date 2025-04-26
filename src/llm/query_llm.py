import requests
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.read_config_file import read_config_file


def query_llm(prompt: str, model: str, temperature: float, config_file: str = "ollama_config.yaml") -> str:
    try:
        config = read_config_file(file_path=config_file)
        model, url = config.get("model"), config.get("url")

        if not model:
            raise ValueError("Model name not found in configuration file.")
        if not url:
            raise ValueError("API url not found in configuration file.")

        response = requests.post(
            url=url,
            json={
                "model": model,
                "content": prompt,
                "temperature": temperature
            }
        )
        response.raise_for_status()
        
        return response.text
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return ""