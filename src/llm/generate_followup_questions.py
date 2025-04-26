import os, sys
from typing import List, Dict, Any
import json


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.llm.ollama_client import OllamaLLM, InputData

def build_followup_prompt(extracted_data: Dict, websearch_results: List[str]) -> str:
    patient_summary = f"""
Nom: {extracted_data.get('patient_name', 'Non spécifié')}
Diagnostic principal: {extracted_data.get('diagnosis', 'Non spécifié')}
Symptômes actuels: {', '.join(extracted_data.get('symptoms', []))}
Traitement actuel: {extracted_data.get('treatment_plan', 'Non spécifié')}
"""
    medical_updates = "\n".join([f"- {article}" for article in websearch_results])

    prompt = f"""
Vous êtes une intelligence artificielle d'assistance médicale spécialisée dans la création de questions de suivi pour les patients.

Voici les données du patient:
{patient_summary}

Voici les dernières informations médicales pertinentes:
{medical_updates}

Tâche:
- Analyser et comprendre les priorités de suivi pour ce patient.
- Générer 5 à 7 questions de suivi sous forme JSON.
- Diversifier les types de questions : short_text, yes_no, number, multiple_choice.
- Respecter ce format JSON strict sans aucune explication :

[
    {{"type": "short_text", "title": "..."}},
    {{"type": "yes_no", "title": "..."}},
    {{"type": "number", "title": "..."}},
    {{"type": "multiple_choice", "title": "...", "properties": {{"choices": [{{"label": "..."}}, {{"label": "..."}}], "allow_multiple_selection": true}}}}
]

Directives spécifiques:
- Les questions doivent être en français naturel et adapté à un patient non expert.
- Utiliser des formulations variées : "Avez-vous constaté...", "Ressentez-vous...", "Avez-vous eu des difficultés avec...", etc.
- Adopter un ton bienveillant et engageant.
- Éviter tout jargon médical technique.
- NE PAS fournir de résumé, ni expliquer les questions : donner directement la liste JSON valide.

Générez maintenant :
"""
    return prompt


def generate_questions(prompt: str, model_name: str = "gemma3:12b", temperature: float = 0.7) -> List[Dict[str, Any]]:
    input_data = InputData(
        model=model_name,
        content=prompt,
        temperature=temperature
    )
    llm = OllamaLLM(input_data=input_data)
    prediction = llm.predict()

    try:
        questions = json.loads(prediction.get("content", ""))
        if not isinstance(questions, list):
            raise ValueError("Invalid output structure: Expected a list.")
        return questions
    except Exception as e:
        print(f"\n❌ Error parsing LLM output: {e}\nRaw output:\n{prediction.get('content', '')}")
        return []
    


def save_questions(questions: List[Dict[str, Any]], filename: str = "patient_questions.json") -> None:
    os.makedirs("outputs", exist_ok=True)
    filepath = os.path.join("outputs", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Questions saved at: {filepath}")



def main():
    # TODO: Replace with real extracted inputs
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

    prompt = build_followup_prompt(extracted_data, websearch_results)
    questions = generate_questions(prompt)

    if questions:
        print("\n✅ Questions prêtes au format Typeform:\n")
        for q in questions:
            print(q)
        save_questions(questions)
    else:
        print("\n⚠️ Aucune question générée.")


if __name__ == "__main__":
    main()