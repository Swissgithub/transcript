# transcribe.py
import whisper
from moviepy.editor import VideoFileClip
import os
import subprocess

# Charger le modèle Whisper une seule fois au démarrage
model = whisper.load_model("tiny")  # Utilisez "tiny" pour de meilleures performances sur Raspberry Pi

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
