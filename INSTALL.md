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
