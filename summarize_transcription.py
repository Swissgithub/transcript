import os
import requests

def summarize_transcription(file_path):
    """
    Lit un fichier de transcription, génère un résumé en utilisant l'API locale LLaMA, et l'ajoute à la fin du fichier.
    """
    try:
        with open(file_path, 'r') as file:
            transcription_text = file.read()
        
        # Utiliser l'API locale LLaMA pour générer le résumé
        summary = summarize_with_llama(transcription_text)
        
        # Append the summary to the transcription file
        with open(file_path, 'a') as file:
            file.write("\n\n-----------------\nRésumé :\n")
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
        "prompt": f"Tell me in one sentence what is the purpose of this text and answer the same language as the text: {transcription_text}",
        "stream": False
    }
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json().get("response", "Erreur : réponse vide de l'API")
    else:
        return f"Erreur : {response.status_code}, {response.text}"

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
