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

## Installation de Whisper

Whisper est un modèle de transcription audio développé par OpenAI. Pour l'installer, suivez les étapes ci-dessous :

1. Installez les dépendances requises :
   ```bash
   pip install torch torchaudio
   ```

2. Installez Whisper :
   ```bash
   pip install git+https://github.com/openai/whisper.git
   ```

3. Vérifiez l'installation en exécutant une commande de test :
   ```bash
   whisper --help
   ```

## Installation de LLaMA

LLaMA est un modèle de langage développé par Meta AI. Pour l'installer, suivez les étapes ci-dessous :

1. Clonez le dépôt LLaMA :
   ```bash
   git clone https://github.com/facebookresearch/llama.git
   cd llama
   ```

2. Installez les dépendances requises :
   ```bash
   pip install -r requirements.txt
   ```

3. Téléchargez le modèle LLaMA (assurez-vous d'avoir les droits d'accès nécessaires) :
   ```bash
   # Remplacez par l'URL de téléchargement du modèle
   wget <URL_DU_MODELE>
   ```

4. Configurez LLaMA dans votre application en suivant les instructions du dépôt.

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
