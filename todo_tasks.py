import os
import requests

def generate_todo_tasks(file_path):
    """
    Lit un fichier de transcription, génère une liste de tâches à faire en utilisant l'API locale LLaMA, et l'ajoute à la fin du fichier.
    """
    try:
        with open(file_path, 'r') as file:
            transcription_text = file.read()
        
        # Imprimer le texte de la transcription pour le diagnostic
        print("Texte de la transcription avant génération des tâches :")
        print(transcription_text)
        
        # Utiliser l'API locale LLaMA pour générer les tâches
        tasks = generate_tasks_with_llama(transcription_text)
        
        # Append the tasks to the transcription file
        with open(file_path, 'a') as file:
            file.write("\n\n-----------------\nTâches à faire :\n")
            file.write(tasks)
        
        print("Tâches ajoutées au fichier de transcription.")
    except Exception as e:
        print(f"Erreur lors de la lecture ou de l'écriture du fichier de transcription : {e}")

def generate_tasks_with_llama(transcription_text):
    """
    Utilise l'API locale LLaMA pour générer une liste de tâches à faire à partir du texte transcrit.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "tinyllama",
        "prompt": f"Please analyze the following text and identify only the tasks that must be performed after the transcription is complete, not actions currently taking place. A 'task' is a concrete directive telling someone what to do, such as 'You must do X' or 'Prepare Y.' Questions, factual statements, or descriptions are not tasks. Don't imagine tasks, juste take these you find in text. A task must be described very shortly and specify which problem it addresses (in few words). If no tasks are detected, respond with: 'No tasks detected.' and nothing else. I want only the conclusion : {transcription_text}",
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
        print(f"Statut de la réponse : {response.status_code}")
        print(f"Contenu de la réponse : {response.text}")
        return response.json().get("response", "Erreur : réponse vide de l'API")
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors de la requête : {e}")
        return f"Erreur lors de la requête : {e}"
    except ValueError as e:
        print(f"Erreur lors du traitement de la réponse JSON : {e}")
        return f"Erreur de traitement JSON : {e}"

if __name__ == "__main__":
    try:
        # Remplacez 'uploads' par le chemin de votre répertoire de transcriptions
        latest_file = get_latest_transcription_file('uploads')
        generate_todo_tasks(latest_file)
    except Exception as e:
        print(f"Erreur lors de la récupération du fichier de transcription : {e}")
