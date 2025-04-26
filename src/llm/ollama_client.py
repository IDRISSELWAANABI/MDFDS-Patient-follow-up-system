import ollama
from pydantic import BaseModel


class InputData(BaseModel):
  model: str
  content: str
  temperature: float

class OllamaLLM:
  def __init__(self, input_data: InputData):
      self.model = input_data.model
      self.content = input_data.content
      self.temperature = input_data.temperature
  
  def predict(self):
    response = ollama.chat(
      model=self.model,
      messages=[
        {
          "role": "user",
          "content": self.content
        }
      ],
      options={
        "temperature": self.temperature
      }
    )
    return {
      "role": "assistant",
      "content": response.message.content
    }
  
  def __repr__(self):
    return f"OllamaLLM(model={self.model})"