# Installation de l'application Transcription

Cette documentation décrit comment installer et exécuter l'application Transcription en tant que service systemd sans utiliser d'environnement virtuel Python.

## Prérequis

- Python 3.11 doit être installé sur le système.
- Gunicorn doit être installé globalement. Vous pouvez l'installer avec la commande suivante :
  ```bash
  pip install gunicorn
  ```
- Toutes les autres dépendances Python doivent être installées globalement. Utilisez la commande suivante pour installer les dépendances listées dans `requirements.txt` :
  ```bash
  pip install -r requirements.txt
  ```

## Configuration du service systemd

1. Créez un fichier de service systemd pour l'application. Par exemple, `/etc/systemd/system/transcription_app.service` :

   ```ini
   [Unit]
   Description=Transcription Flask App
   After=network.target sound.target

   [Service]
   User=root
   WorkingDirectory=/opt/transcript/
   ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 120 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. Copiez le fichier de service dans le répertoire systemd :
   ```bash
   sudo cp systemd_service/transcription_app.service /etc/systemd/system/
   ```

3. Rechargez le démon systemd pour prendre en compte le nouveau fichier de service :
   ```bash
   sudo systemctl daemon-reload
   ```

4. Activez le service pour qu'il démarre au démarrage du système :
   ```bash
   sudo systemctl enable transcription_app.service
   ```

5. Démarrez le service :
   ```bash
   sudo systemctl start transcription_app.service
   ```

## Gestion du service

- Pour vérifier l'état du service :
  ```bash
  sudo systemctl status transcription_app.service
  ```

- Pour redémarrer le service :
  ```bash
  sudo systemctl restart transcription_app.service
  ```

- Pour arrêter le service :
  ```bash
  sudo systemctl stop transcription_app.service
  ```

Suivez ces instructions pour installer et exécuter l'application Transcription en tant que service systemd sans utiliser d'environnement virtuel Python.

---

# Installation and Integration Guide for `openllama-7b` on Raspberry Pi 5

1. **Install Required Tools**:
   - Update your package list and install necessary tools:
     ```bash
     sudo apt-get update
     sudo apt-get install -y git wget build-essential
     ```

2. **Download `openllama-7b` Model**:
   - Use `wget` or a similar tool to download the `openllama-7b` model. You may need to find the specific URL for the model download. For example:
     ```bash
     wget https://huggingface.co/models?search=openllama-7b -O openllama-7b.zip
     unzip openllama-7b.zip -d openllama-7b
     ```

3. **Set Up the Environment**:
   - Ensure you have Python and necessary libraries installed. You might need to install additional Python packages depending on the model's requirements.

4. **Integrate `openllama-7b` into Your Application**:
   - Implement a function in your application to use `openllama-7b` for summarization. Here's a conceptual example:

```python
import subprocess

def summarize_with_openllama(transcription_text):
    """
    Utilise openllama-7b pour générer un résumé du texte transcrit.
    """
    # Placeholder for openllama-7b integration
    # Replace this with actual openllama-7b summarization logic
    summary = "Résumé généré par openllama-7b."
    return summary

def transcribe_and_summarize(file_path):
    """
    Transcrit un fichier audio et génère un résumé.
    """
    transcription_text = transcribe_audio(file_path)
    summary = summarize_with_openllama(transcription_text)
    return transcription_text, summary
```

5. **Modify the Workflow**:
   - Update your application to call the summarization function after the transcription process.
