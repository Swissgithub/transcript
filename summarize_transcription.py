import os
from transformers import pipeline
import re

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

def preprocess_text(text):
    """
    Cleans the text by removing extra spaces and artifacts.
    """
    # Remove extra spaces and normalize text
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_text(text, max_length=500):
    """
    Splits the text into smaller chunks to handle long inputs.
    """
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def summarize_with_transformers(transcription_text):
    """
    Generates a summary of the transcribed text using Hugging Face Transformers.
    """
    # Preprocess the text
    transcription_text = preprocess_text(transcription_text)
    
    # Add contextual instruction
    transcription_text = "Summarize the following text: " + transcription_text

    # Load the summarization model
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Split the text if it exceeds the token limit
    segments = split_text(transcription_text)
    
    # Summarize each segment
    summaries = [
        summarizer(segment, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        for segment in segments
    ]
    
    # Combine all summaries into one
    combined_summary = " ".join(summaries)
    return combined_summary

# Example usage
transcription_text = """
Where do you live? I live in Pasadena. Where is Pasadena? It's in California. Is it in Northern California? 
No, it's in Southern California. Is Pasadena a big city? It's pretty big. How big is pretty big? 
It has about 140,000 people. How big is Los Angeles? It has about 3 million people.
"""

summary = summarize_with_transformers(transcription_text)
print("Summary:", summary)

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
