import os

def summarize_transcription(file_path):
    """
    Lit un fichier de transcription, génère un résumé et identifie les actions.
    """
    try:
        with open(file_path, 'r') as file:
            transcription_text = file.read()
        
        # Placeholder for openllama-7b integration
        summary = summarize_with_openllama(transcription_text)
        
        print("Résumé :")
        print(summary)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de transcription : {e}")

def summarize_with_openllama(transcription_text):
    """
    Utilise openllama-7b pour générer un résumé du texte transcrit.
    """
    # Placeholder for openllama-7b integration
    # Replace this with actual openllama-7b summarization logic
    summary = "Résumé généré par openllama-7b. Identifiez les actions ici."
    return summary

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
