import os
import logging
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from faster_whisper import WhisperModel
import subprocess

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4', 'm4a'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # Limite de taille de fichier à 100 Mo

# Initialisation de l'application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialisation du modèle Whisper
model = WhisperModel("large-v2")

# Configuration du logging
logging.basicConfig(level=logging.INFO)

# Vérifier si l'extension est autorisée
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Convertir en WAV
def convert_to_wav(filepath):
    try:
        new_filepath = os.path.splitext(filepath)[0] + '.wav'
        subprocess.run(['ffmpeg', '-i', filepath, new_filepath], check=True)
        return new_filepath
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de la conversion en WAV : {e}")
        return None

# Route principale
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Vérification du fichier téléchargé
        if 'file' not in request.files:
            logging.warning("Aucun fichier dans la requête")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            logging.warning("Aucun fichier sélectionné")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logging.info(f"Fichier téléchargé et sauvegardé à {filepath}")

            # Conversion en WAV si nécessaire
            if not filename.lower().endswith('.wav'):
                filepath = convert_to_wav(filepath)
                if not filepath:
                    return "Erreur lors de la conversion du fichier."

            # Transcription
            try:
                segments, info = model.transcribe(filepath)
                transcription = "\n".join([segment.text for segment in segments])
                logging.info("Transcription réussie")
            except Exception as e:
                logging.error(f"Erreur lors de la transcription : {e}")
                return "Erreur lors de la transcription."

            # Suppression du fichier après traitement
            try:
                os.remove(filepath)
                logging.info(f"Fichier temporaire supprimé : {filepath}")
            except Exception as e:
                logging.warning(f"Impossible de supprimer le fichier temporaire : {e}")

            return render_template('result.html', transcription=transcription)
    return render_template('upload.html')

# Route pour accéder aux fichiers téléchargés
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Exécution de l'application
if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, host='0.0.0.0', port=5000)
