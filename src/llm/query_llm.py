import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.llm.ollama_client import OllamaLLM, InputData

class QueryLLM:
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature

    def query(self, prompt: str) -> str:
        input_data = InputData(
            model=self.model,
            content=prompt,
            temperature=self.temperature
        )
        llm = OllamaLLM(input_data=input_data)
        prediction = llm.predict()
        return prediction["content"]


# Example usage:
if __name__ == "__main__":
    llm = QueryLLM(
        model="gemma3:12b",
        temperature=0.7
    )
    prompt="Hello"
    print(llm.query(prompt=prompt))