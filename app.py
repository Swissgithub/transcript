# app.py
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid

from transcribe import transcribe_audio, extract_audio_from_video
from recorder import AudioRecorder

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuration des utilisateurs pour l'authentification
#auth = HTTPBasicAuth()
#users = {
#    "admin": generate_password_hash("password123")  # Remplacez par vos identifiants sécurisés
#}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

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

def generate_unique_filename(extension=".txt"):
    """
    Génère un nom de fichier unique basé sur un UUID.
    """
    return f"transcription_{uuid.uuid4().hex}{extension}"

def save_transcription(text, filename=None):
    """
    Sauvegarde la transcription dans un fichier texte.
    """
    if not filename:
        filename = generate_unique_filename()
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return file_path

# Instance de l'enregistreur audio
recorder = AudioRecorder(output_path=os.path.join(UPLOAD_FOLDER, 'live_record.wav'))

@app.route('/')
@auth.login_required
def index():
    """
    Route principale affichant le formulaire d'upload et les contrôles d'enregistrement.
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    """
    Gère le téléchargement de fichiers audio et vidéo, les transcrit, et affiche le résultat.
    """
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension in ['.mp4', '.mov', '.avi']:
            try:
                # Extraire l'audio
                audio_file = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')
                extract_audio_from_video(file_path, audio_file)
                transcription = transcribe_audio(audio_file)
                # Supprimer l'audio extrait après transcription
                os.remove(audio_file)
                # Supprimer le fichier vidéo original après transcription (optionnel)
                os.remove(file_path)
            except Exception as e:
                transcription = f"Erreur lors de la transcription : {e}"
        else:
            try:
                transcription = transcribe_audio(file_path)
                # Supprimer le fichier audio original après transcription (optionnel)
                os.remove(file_path)
            except Exception as e:
                transcription = f"Erreur lors de la transcription : {e}"
        
        # Sauvegarder la transcription dans un fichier
        transcription_file = save_transcription(transcription)
        
        return render_template('result.html', transcription=transcription)
    else:
        return redirect(url_for('index'))

@app.route('/start_recording', methods=['POST'])
@auth.login_required
def start_recording():
    """
    Démarre l'enregistrement audio en direct.
    """
    if not recorder.is_recording:
        recorder.start_recording()
        return redirect(url_for('index'))
    else:
        return "Enregistrement déjà en cours."

@app.route('/stop_recording', methods=['POST'])
@auth.login_required
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
        except Exception as e:
            transcription = f"Erreur lors de la transcription : {e}"
        
        # Sauvegarder la transcription dans un fichier
        transcription_file = save_transcription(transcription)
        
        return render_template('result.html', transcription=transcription)
    else:
        return "Aucun enregistrement en cours."

@app.route('/uploads/<filename>')
@auth.login_required
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

@app.errorhandler(413)
def request_entity_too_large(error):
    return "Fichier trop volumineux. La taille maximale autorisée est de 100MB.", 413

if __name__ == "__main__":
    try:
        # Exécuter l'application Flask
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # S'assurer que PyAudio est correctement terminé lors de l'arrêt
        recorder.terminate()

