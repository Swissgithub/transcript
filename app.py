import logging
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import requests
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from transcribe import transcribe_audio, extract_audio_from_video, load_whisper_model
from recorder import AudioRecorder
from summarize_transcription import summarize_transcription
from todo_tasks import generate_todo_tasks

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='flask_app.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Configuration des dossiers
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Limite à 100MB

# Paramètres d'upload
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    """
    Vérifie si le fichier a une extension autorisée.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_transcription(text, filename="current_transcription.txt"):
    """
    Sauvegarde la transcription dans un fichier texte nommé 'current_transcription.txt'.
    """
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("Transcription:\n")
        f.write(text + "\n")
    return file_path

def get_latest_transcription():
    """
    Récupère le contenu du dernier fichier de transcription créé.
    """
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "current_transcription.txt")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Instance de l'enregistreur audio
recorder = AudioRecorder(output_path=os.path.join(UPLOAD_FOLDER, 'live_record.wav'))

# Charger le modèle Whisper au démarrage
whisper_model = load_whisper_model()

@app.route('/')
def index():
    """
    Route principale affichant le formulaire d'upload et les contrôles d'enregistrement.
    """
    return render_template('index.html', transcription_content=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Gère le téléchargement de fichiers audio et vidéo, les transcrit, et affiche le résultat.
    """
    app.logger.debug("Requête d'upload reçue")
    if 'file' not in request.files:
        app.logger.error("Aucun fichier dans la requête")
        return jsonify({"error": "Aucun fichier dans la requête"}), 400
    file = request.files['file']
    if file.filename == '':
        app.logger.error("Nom de fichier vide")
        return jsonify({"error": "Nom de fichier vide"}), 400
    if file and allowed_file(file.filename):
        app.logger.debug(f"Fichier accepté : {file.filename}")
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension in ['.mp4', '.mov', '.avi']:
            try:
                # Extraire l'audio
                app.logger.debug(f"Extraction de l'audio du fichier vidéo : {file_path}")
                audio_file = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')
                extract_audio_from_video(file_path, audio_file)
                app.logger.debug(f"Audio extrait avec succès : {audio_file}")
                transcription = transcribe_audio(audio_file)
                app.logger.debug(f"Transcription réussie : {transcription}")
                # Supprimer l'audio extrait après transcription
                os.remove(audio_file)
                # Supprimer le fichier vidéo original après transcription (optionnel)
                os.remove(file_path)
            except Exception as e:
                transcription = f"Erreur lors de la transcription : {e}"
                app.logger.error(transcription)
        else:
            try:
                transcription = transcribe_audio(file_path)
                app.logger.debug(f"Transcription réussie : {transcription}")
                # Supprimer le fichier audio original après transcription (optionnel)
                os.remove(file_path)
            except Exception as e:
                transcription = f"Erreur lors de la transcription : {e}"
                app.logger.error(transcription)
        
        # Sauvegarder la transcription dans un fichier
        transcription_file = save_transcription(transcription)
        
        # Ensure summarization is called for MP4 files
        summary = summarize_transcription(transcription_file)
        
        # Generate todo tasks
        generate_todo_tasks(transcription_file)
        
        # Log transcription and summary
        app.logger.debug(f"Transcription: {transcription}")
        app.logger.debug(f"Summary: {summary}")
        
        latest_transcription = get_latest_transcription()
        return jsonify({"transcription": latest_transcription, "summary": summary})
    else:
        app.logger.error(f"Fichier non autorisé ou problème de format : {file.filename}")
        return jsonify({"error": "Fichier non autorisé ou problème de format"}), 400

@app.route('/send_email', methods=['POST'])
def send_email():
    """
    Envoie le résultat de la transcription par email.
    """
    data = request.json
    email = data.get('email')
    transcription = data.get('transcription')
    summary = data.get('summary')
    
    if not email:
        return jsonify({"message": "Email address is required"}), 400
    
    try:
        # Configurez votre serveur SMTP ici
        smtp_server = "smtp.example.com"
        smtp_port = 587
        smtp_user = "your_email@example.com"
        smtp_password = "your_password"
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email
        msg['Subject'] = "Transcription Results"
        
        body = f"Transcription:\n{transcription}\n\nSummary:\n{summary}"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email, msg.as_string())
        server.quit()
        
        return jsonify({"message": "Email sent successfully"})
    except Exception as e:
        return jsonify({"message": f"Failed to send email: {e}"}), 500

@app.route('/start_recording', methods=['POST'])
def start_recording():
    """
    Démarre l'enregistrement audio en direct.
    """
    if not recorder.is_recording:
        recorder.start_recording()
        return jsonify({"status": "recording_started"})
    else:
        return jsonify({"status": "already_recording"})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    """
    Arrête l'enregistrement audio en direct et affiche la transcription.
    """
    if recorder.is_recording:
        recorder.stop_recording()
        try:
            # Transcrire l'enregistrement
            transcription = transcribe_audio(recorder.output_path)
            # Supprimer le fichier enregistré après transcription (optionnel)
            os.remove(recorder.output_path)
            
            # Sauvegarder la transcription dans un fichier
            transcription_file = save_transcription(transcription)
            
            # Générer le résumé
            summary = summarize_transcription(transcription_file)
            
            # Generate todo tasks
            generate_todo_tasks(transcription_file)
            
            # Log transcription and summary
            app.logger.debug(f"Transcription: {transcription}")
            app.logger.debug(f"Summary: {summary}")
            
            latest_transcription = get_latest_transcription()
            return jsonify({"transcription": latest_transcription, "summary": summary})
        except Exception as e:
            app.logger.error(f"Erreur lors de la transcription : {e}")
            return jsonify({"error": f"Erreur lors de la transcription : {e}"})
    else:
        app.logger.debug("Aucun enregistrement en cours lors de l'appel à stop_recording.")
        return jsonify({"status": "no_recording"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Permet de télécharger les fichiers enregistrés ou transcrits.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health')
def health():
    """
    Route de vérification de santé de l'application.
    """
    return "L'application fonctionne correctement."

@app.route('/check_internet')
def check_internet():
    """
    Vérifie si le serveur a accès à Internet avec un délai d'attente de 5 secondes.
    """
    try:
        requests.get('https://www.google.com', timeout=5)
        return jsonify({"internet_access": True})
    except requests.ConnectionError:
        return jsonify({"internet_access": False})

@app.route('/summarize', methods=['POST'])
def summarize():
    """
    Exécute le script de résumé de transcription et retourne le résultat.
    """
    try:
        result = subprocess.run(['python', 'summarize_transcription.py'], capture_output=True, text=True)
        summary = result.stdout.strip()
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": f"Erreur lors du résumé : {e}"}), 500

@app.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    """
    Supprime tous les fichiers dans le dossier des uploads.
    """
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return jsonify({"message": "Uploads cleared successfully"})
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression des fichiers : {e}"}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return "Fichier trop volumineux. La taille maximale autorisée est de 100MB.", 413

if __name__ == "__main__":
    try:
        # Exécuter l'application Flask avec le mode debug activé
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # S'assurer que PyAudio est correctement terminé lors de l'arrêt
        recorder.terminate()
