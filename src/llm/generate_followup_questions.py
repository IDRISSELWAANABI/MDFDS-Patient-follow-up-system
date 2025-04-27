import os, sys
from typing import List, Dict, Any
import json


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.llm.ollama_client import OllamaLLM, InputData

class FollowupPromptBuilder:
    @staticmethod
    def build(extracted_data: Dict, websearch_results: List[str]) -> str:
        patient_summary = f"""
Nom: {extracted_data.get('patient_name', 'Non spécifié')}
Diagnostic principal: {extracted_data.get('diagnosis', 'Non spécifié')}
Symptômes actuels: {', '.join(extracted_data.get('symptoms', []))}
Traitement actuel: {extracted_data.get('treatment_plan', 'Non spécifié')}
"""
        medical_updates = "\n".join([f"- {article}" for article in websearch_results])

        prompt = f"""
# Objectif :
Générer des questions de suivi médicales pour un patient, au format JSON strict.

# Données du patient :
{patient_summary}

# Informations médicales récentes :
{medical_updates}

# Règles :
- Générer entre 5 et 7 questions de suivi personnalisées.
- Diversifier les types de questions : short_text, yes_no, number, multiple_choice.
- Chaque question doit être un objet avec exactement les clés suivantes :
  - "ref" : identifiant unique et court en snake_case (ex: "suivi_fatigue", "suivi_glycemie")
  - "title" : texte de la question (formulé pour un patient)
  - "type" : type de question ("short_text", "long_text", "number", "multiple_choice", "yes_no", "rating", "opinion_scale", "date", "email", "phone_number", "dropdown")
  - "validations" : dictionnaire des règles de validation (ex: {{"required": true}})

- Si le type est "multiple_choice", ajouter une clé "properties" avec :
  - "choices" : une liste d'objets {{"label": "texte choix"}}.

- Exemple de bonne structure pour une question :
  {{
    "ref": "suivi_douleur",
    "title": "Ressentez-vous encore des douleurs ?",
    "type": "yes_no",
    "validations": {{"required": true}}
  }}
  ou pour une question multiple_choice :
  {{
    "ref": "suivi_symptomes",
    "title": "Quels symptômes avez-vous ressentis ?",
    "type": "multiple_choice",
    "validations": {{"required": true}},
    "properties": {{"choices": [{{"label": "Fatigue"}}, {{"label": "Douleur"}}, {{"label": "Essoufflement"}}]}}
  }}

# Contraintes sur la sortie :
- Sortie = **une seule ligne JSON** commençant par [ et finissant par ].
- Ne pas ajouter de balises ("```json") ni d'introduction ("json", "réponse:", etc.).
- Aucune explication, seulement la liste JSON.
- Aucun retour à la ligne.

# Consignes linguistiques :
- Formuler les questions en français naturel, clair, bienveillant et accessible au grand public.
- Varier les formulations : "Avez-vous constaté...", "Ressentez-vous...", "Avez-vous eu des difficultés avec...", etc.
- Éviter tout jargon médical technique.

# Exemple de sortie correcte :
[{{"type":"short_text","title":"Comment vous sentez-vous aujourd'hui?"}},{{"type":"yes_no","title":"Avez-vous ressenti de la douleur récemment?"}},{{"type":"number","title":"Combien de fois par jour prenez-vous votre traitement?"}},{{"type":"multiple_choice","title":"Quel symptôme avez-vous ressenti?", "properties":{{"choices":[{{"label":"Fatigue"}},{{"label":"Douleur"}},{{"label":"Essoufflement"}}],"allow_multiple_selection":true}}}}]

# Tâche :
Analyser les données ci-dessus et générer les questions de suivi au bon format.
"""
        return prompt



class FollowupQuestionGenerator:
    def __init__(self, model_name: str = "gemma3:12b", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, prompt: str) -> List[Dict[str, Any]]:
        input_data = InputData(
            model=self.model_name,
            content=prompt,
            temperature=self.temperature
        )
        llm = OllamaLLM(input_data=input_data)
        prediction = llm.predict()

        try:
            questions = json.loads(prediction.get("content", ""))
            if not isinstance(questions, list):
                raise ValueError("Invalid output structure: Expected a list.")
            return questions
        except Exception as e:
            print(f"Error parsing LLM output: {e}\nRaw output:\n{prediction.get('content', '')}")
            return []
    


class FollowupQuestionSaver:
    @staticmethod
    def save(questions: List[Dict[str, Any]], filename: str = "patient_questions.json") -> None:
        os.makedirs("outputs", exist_ok=True)
        filepath = os.path.join("outputs", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=4)
        print(f"Questions saved at: {filepath}")



def main():
    extracted_data = {
        "patient_name": "Ahmed B.",
        "diagnosis": "Type 2 Diabetes",
        "symptoms": ["fatigue", "excessive thirst", "frequent urination"],
        "treatment_plan": "Metformin 500mg twice daily; follow low-sugar diet."
    }

    websearch_results = [
        "Patients with type 2 diabetes must monitor their blood sugar daily. Symptoms of worsening diabetes include blurred vision, numbness, and persistent infections.",
        "Guidelines recommend that patients should report any major changes in weight, severe fatigue, or signs of foot ulcers immediately.",
        "Regular physical activity is crucial for blood sugar control. Missing medication doses can lead to serious complications like ketoacidosis."
    ]

    prompt = FollowupPromptBuilder.build(extracted_data, websearch_results)
    generator = FollowupQuestionGenerator()
    questions = generator.generate(prompt)

    if questions:
        print("\nQuestions generated:\n")
        for question in questions:
            print(question)
        FollowupQuestionSaver.save(questions)
    else:
        print("No questions generated.")


if __name__ == "__main__":
    main()