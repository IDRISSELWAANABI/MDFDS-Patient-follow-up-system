from fastapi import FastAPI
from ollama_client import OllamaLLM, InputData
import uvicorn
from pydantic import BaseModel


app = FastAPI()

class Prompt(BaseModel):
    model: str
    content: str
    temperature: float

@app.get("/")
def main():
    return {"health_check": "OK"}

@app.post("/predict/")
def predict(request: Prompt):
    input_data = InputData(
        model=request.model,
        content=request.content,
        temperature=request.temperature
    )
    llm = OllamaLLM(input_data=input_data)
    prediction = llm.predict()
    return prediction["content"]


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)