from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid

from transcribe import transcribe_audio, extract_audio_from_video
from recorder import AudioRecorder

app = Flask(__name__)

# Configuration des dossiers
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # Limite à 200MB

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
def index():
    """
    Route principale affichant le formulaire d'upload et les contrôles d'enregistrement.
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
@app.route('/upload', methods=['POST'])
def upload_file():
    print("Requête d'upload reçue")
    
    # Vérifie si un fichier est bien inclus dans la requête
    if 'file' not in request.files:
        print("Erreur: Aucun fichier trouvé dans la requête.")
        return redirect(url_for('index')), 400  # Retourne une erreur 400 explicite
    
    file = request.files['file']
    print(f"Fichier reçu: {file}")  # Affiche des informations sur l'objet fichier
    
    # Vérifie si le nom de fichier est vide
    if file.filename == '':
        print("Erreur: Le nom du fichier est vide.")
        return redirect(url_for('index')), 400
    
    # Vérifie si le fichier a une extension autorisée
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"Fichier accepté: {filename}")  # Affiche le nom du fichier accepté
        try:
            file.save(file_path)  # Tente de sauvegarder le fichier
            print(f"Fichier sauvegardé à {file_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du fichier: {e}")
            return f"Erreur de sauvegarde du fichier: {e}", 500  # Retourne une erreur 500 explicite

        # Traite le fichier selon son extension
        file_extension = os.path.splitext(filename)[1].lower()
        try:
            if file_extension in ['.mp4', '.mov', '.avi']:
                print("Début de l'extraction de l'audio depuis la vidéo")
                audio_file = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')
                extract_audio_from_video(file_path, audio_file)
                transcription = transcribe_audio(audio_file)
                os.remove(audio_file)
                os.remove(file_path)
            else:
                print("Début de la transcription de l'audio")
                transcription = transcribe_audio(file_path)
                os.remove(file_path)
            print("Transcription réussie")
        except Exception as e:
            transcription = f"Erreur lors de la transcription : {e}"
            print(transcription)
        
        # Sauvegarde la transcription dans un fichier texte
        try:
            transcription_file = save_transcription(transcription)
            print(f"Transcription sauvegardée dans le fichier {transcription_file}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la transcription : {e}")
            return f"Erreur de sauvegarde de la transcription: {e}", 500

        return render_template('result.html', transcription=transcription)
    else:
        print(f"Fichier non autorisé ou problème de format : {file.filename}")
        return redirect(url_for('index')), 400


@app.route('/start_recording', methods=['POST'])
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
    return "Fichier trop volumineux. La taille maximale autorisée est de 200MB.", 413

if __name__ == "__main__":
    try:
        # Exécuter l'application Flask
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # S'assurer que PyAudio est correctement terminé lors de l'arrêt
        recorder.terminate()
