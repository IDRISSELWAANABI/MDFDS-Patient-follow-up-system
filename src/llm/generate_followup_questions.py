from src.llm.ollama_client import OllamaLLM, InputData
import os
from typing import List, Dict


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
- Générer entre 5 et 7 questions claires et personnalisées à poser au patient.

Directives spécifiques:
- Les questions doivent être en français naturel et adapté à un patient non expert.
- Utiliser des formulations variées : "Avez-vous constaté...", "Ressentez-vous...", "Avez-vous eu des difficultés avec...", etc.
- Adopter un ton bienveillant et engageant.
- Éviter tout jargon médical technique.
- NE PAS fournir de résumé, ni expliquer les questions : donner directement la liste des questions.

Générez la liste maintenant :
"""
    return prompt


def generate_questions(prompt: str, model_name: str = "gemma:3b", temperature: float = 0.7) -> str:
    input_data = InputData(
        model=model_name,
        content=prompt,
        temperature=temperature
    )
    llm = OllamaLLM(input_data=input_data)
    prediction = llm.predict()
    return prediction.get("content", "")


def save_output(text: str, filename: str = "patient_questions.txt") -> None:
    os.makedirs("outputs", exist_ok=True)
    filepath = os.path.join("outputs", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n✅ Questions saved at: {filepath}")


def main():
    # TODO: Replace with real data input in production
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
    generated_questions = generate_questions(prompt)

    print("\n✅ Questions prêtes à envoyer au patient:\n")
    print(generated_questions)

    save_output(generated_questions)


if __name__ == "__main__":
    main()