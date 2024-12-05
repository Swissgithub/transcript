from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import requests
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from transcribe import transcribe_audio, extract_audio_from_video
from recorder import AudioRecorder
from summarize_transcription import summarize_transcription

app = Flask(__name__)

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

@app.route('/')
def index():
    """
    Route principale affichant le formulaire d'upload et les contrôles d'enregistrement.
    """
    return render_template('index.html', transcription_content=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Gère le téléchargement de fichiers audio et vidéo, les transcrit, et renvoie le résultat.
    """
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier dans la requête"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_extension = os.path.splitext(filename)[1].lower()
        try:
            if file_extension in ['.mp4', '.mov', '.avi']:
                # Extraire l'audio
                audio_file = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')
                extract_audio_from_video(file_path, audio_file)
                transcription = transcribe_audio(audio_file)
                os.remove(audio_file)
                os.remove(file_path)
            else:
                transcription = transcribe_audio(file_path)
                os.remove(file_path)

            # Sauvegarder la transcription dans un fichier
            transcription_file = save_transcription(transcription)

            # Générer le résumé
            summary = summarize_transcription(transcription_file)

            return jsonify({"transcription": transcription, "summary": summary}), 200
        except Exception as e:
            error_message = f"Erreur lors de la transcription : {e}"
            return jsonify({"error": error_message}), 500
    else:
        return jsonify({"error": "Fichier non autorisé ou problème de format"}), 400

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
    Arrête l'enregistrement audio en direct et renvoie la transcription.
    """
    if recorder.is_recording:
        recorder.stop_recording()
        try:
            # Transcrire l'enregistrement
            transcription = transcribe_audio(recorder.output_path)
            os.remove(recorder.output_path)

            # Sauvegarder la transcription dans un fichier
            transcription_file = save_transcription(transcription)

            # Générer le résumé
            summary = summarize_transcription(transcription_file)

            return jsonify({"transcription": transcription, "summary": summary}), 200
        except Exception as e:
            error_message = f"Erreur lors de la transcription : {e}"
            return jsonify({"error": error_message}), 500
    else:
        return jsonify({"status": "no_recording"}), 400

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
        return jsonify({"message": "Adresse email requise"}), 400
    
    try:
        # Configurez votre serveur SMTP ici
        smtp_server = "smtp.example.com"
        smtp_port = 587
        smtp_user = "your_email@example.com"
        smtp_password = "your_password"
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email
        msg['Subject'] = "Résultats de la Transcription"
        
        body = f"Transcription:\n{transcription}\n\nRésumé:\n{summary}"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email, msg.as_string())
        server.quit()
        
        return jsonify({"message": "Email envoyé avec succès"})
    except Exception as e:
        return jsonify({"message": f"Échec de l'envoi de l'email : {e}"}), 500

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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Permet de télécharger les fichiers enregistrés ou transcrits.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
