import whisper
from moviepy.editor import VideoFileClip
import os
import subprocess
from transformers import pipeline

def download_model_if_not_exists(model_name="small"):
    """
    Télécharge le modèle Whisper spécifié s'il n'existe pas déjà dans le cache local.
    """
    try:
        # Tente de charger le modèle pour vérifier s'il est déjà téléchargé
        whisper.load_model(model_name)
        print(f"Modèle {model_name} déjà présent.")
    except RuntimeError:
        print(f"Téléchargement du modèle {model_name}...")
        whisper.load_model(model_name)

def load_whisper_model():
    """
    Charge le modèle Whisper.
    """
    return whisper.load_model("small")

def convert_audio(file_path, target_path, samp_rate=16000):
    """
    Convertit un fichier audio en mono avec une fréquence d'échantillonnage spécifiée.
    Utilise ffmpeg pour la conversion.
    """
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', file_path,
            '-ac', '1',                # Mono
            '-ar', str(samp_rate),     # Fréquence d'échantillonnage
            target_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la conversion de l'audio : {e.stderr.decode()}")
        raise e

def transcribe_audio(file_path):
    """
    Transcrit un fichier audio en texte après l'avoir converti au format requis.
    """
    model = load_whisper_model()
    try:
        # Chemin vers l'audio converti
        converted_audio = "converted_audio.wav"
        
        # Convertir l'audio
        convert_audio(file_path, converted_audio)
        
        # Transcrire l'audio converti
        result = model.transcribe(converted_audio)
        
        # Supprimer le fichier audio converti
        os.remove(converted_audio)
        
        return result["text"]
    except Exception as e:
        print(f"Erreur lors de la transcription de {file_path} : {e}")
        return ""

def extract_audio_from_video(video_path, audio_path):
    """
    Extrait l'audio d'un fichier vidéo et le sauvegarde en tant que fichier WAV.
    Ensuite, convertit l'audio extrait en format compatible.
    """
    try:
        # Extraire l'audio avec moviepy
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        
        # Convertir l'audio extrait
        convert_audio(audio_path, audio_path, samp_rate=16000)
    except Exception as e:
        print(f"Erreur lors de l'extraction de l'audio de {video_path} : {e}")

def summarize_transcription(transcription_text):
    """
    Utilise un modèle LLM pour résumer la transcription et générer une liste d'actions.
    """
    # Charger le modèle de résumé
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Calculer la longueur maximale du résumé
    input_length = len(transcription_text.split())
    max_length = min(100, input_length // 2)  # Ajuster pour une meilleure synthèse
    
    # Générer le résumé
    summary = summarizer(transcription_text, max_length=max_length, min_length=25, do_sample=False)
    
    # Générer une liste d'actions (exemple simplifié)
    actions = ["Action 1", "Action 2", "Action 3"]  # Remplacer par une logique réelle
    
    return summary[0]['summary_text'], actions
