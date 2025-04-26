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
- Respecter exactement ce format pour chaque question :
  - Pour "short_text", "yes_no" et "number" :
    {{"type":"short_text","title":"..."}} (ou autre type)
  - Pour "multiple_choice" :
    {{"type":"multiple_choice","title":"...","properties":{{"choices":[{{"label":"..."}},{{"label":"..."}}],"allow_multiple_selection":true}}}}
- Écrire toutes les questions dans une seule **liste JSON** strictement au format suivant :  
  [
    {{"type":"short_text","title":"..."}},
    {{"type":"yes_no","title":"..."}},
    ...
  ]
- Aucune explication, aucun texte supplémentaire, aucun retour à la ligne.
- La sortie doit être une **seule ligne JSON** valide commençant par [ et terminant par ].
- Pas de préfixe (ex: "json"), pas de balises ```json, ni d’introduction ou de commentaires.

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