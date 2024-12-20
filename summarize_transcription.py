import os
import requests

def summarize_transcription(file_path):
    """
    Lit un fichier de transcription, génère un résumé en utilisant l'API locale LLaMA, et l'ajoute à la fin du fichier.
    """
    try:
        with open(file_path, 'r') as file:
            transcription_text = file.read()
        
        # Imprimer le texte de la transcription pour le diagnostic
        print("Texte de la transcription avant summarization :")
        print(transcription_text)
        
        # Utiliser l'API locale LLaMA pour générer le résumé
        summary = summarize_with_llama(transcription_text)
        
        # Append the summary to the transcription file
        with open(file_path, 'a') as file:
            file.write("\n\n-----------------\nSummary :\n")
            file.write(summary)
        
        print("Résumé ajouté au fichier de transcription.")
    except Exception as e:
        print(f"Erreur lors de la lecture ou de l'écriture du fichier de transcription : {e}")

def summarize_with_llama(transcription_text):
    """
    Utilise l'API locale LLaMA pour générer un résumé du texte transcrit.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "tinyllama",
        "prompt": f"Tell me in one sentence what is the purpose of this text: {transcription_text}",
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

def get_latest_transcription_file(directory):
    """
    Récupère le fichier de transcription le plus récent dans le répertoire spécifié.
    """
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith('transcription_')]
    if not files:
        raise FileNotFoundError("Aucun fichier de transcription trouvé.")
    latest_file = max(files, key=os.path.getctime)
    return latest_file

if __name__ == "__main__":
    try:
        # Remplacez 'uploads' par le chemin de votre répertoire de transcriptions
        latest_file = get_latest_transcription_file('uploads')
        summarize_transcription(latest_file)
    except Exception as e:
        print(f"Erreur lors de la récupération du fichier de transcription : {e}")
