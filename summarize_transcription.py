import os
from transformers import pipeline

def summarize_transcription(file_path):
    """
    Lit un fichier de transcription, génère un résumé, et l'ajoute à la fin du fichier.
    """
    try:
        with open(file_path, 'r') as file:
            transcription_text = file.read()
        
        # Utiliser Hugging Face Transformers pour générer le résumé
        summary = summarize_with_transformers(transcription_text)
        
        # Append the summary to the transcription file
        with open(file_path, 'a') as file:
            file.write("\n\n---\nRésumé :\n")
            file.write(summary)
        
        print("Résumé ajouté au fichier de transcription.")
    except Exception as e:
        print(f"Erreur lors de la lecture ou de l'écriture du fichier de transcription : {e}")

def summarize_with_transformers(transcription_text):
    """
    Utilise un modèle de Hugging Face Transformers pour générer un résumé du texte transcrit.
    """
    summarizer = pipeline("summarization")
    # Ajuster les paramètres pour un résumé plus détaillé
    summary = summarizer(transcription_text, max_length=200, min_length=50, do_sample=False)
    return summary[0]['summary_text']

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
