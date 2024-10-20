# Guide d'Installation pour l'Application Transcript

## Prérequis

- Python 3.x doit être installé sur votre système.
- Assurez-vous que `pip` est installé et à jour.
- Installez `ffmpeg` sur votre système pour le traitement audio/vidéo.

## Étapes d'Installation

### 1. Cloner le Dépôt

Clonez le dépôt Git sur votre machine locale et naviguez dans le répertoire du projet :

```bash
git clone <URL_DU_DEPOT>
cd transcript
```

### 2. Créer et Activer un Environnement Virtuel

Créez un environnement virtuel pour isoler les dépendances du projet :

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows, utilisez `venv\\Scripts\\activate`
```

### 3. Installer les Dépendances

Installez les dépendances nécessaires à partir du fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

### 4. Configurer le Service systemd (Optionnel)

Si vous souhaitez exécuter l'application en tant que service systemd, suivez ces étapes :

- Copiez le fichier `systemd_service/transcription_app.service` dans le répertoire `/etc/systemd/system/`.
- Rechargez le démon systemd pour prendre en compte le nouveau service :

```bash
sudo systemctl daemon-reload
```

- Démarrez le service :

```bash
sudo systemctl start transcription_app
```

- Activez le service pour qu'il démarre automatiquement au démarrage :

```bash
sudo systemctl enable transcription_app
```

### 5. Exécuter l'Application

Pour exécuter l'application Flask localement, utilisez la commande suivante :

```bash
flask run
```

### 6. Accéder à l'Application

Ouvrez votre navigateur web et accédez à l'application à l'adresse suivante : [http://127.0.0.1:5000](http://127.0.0.1:5000).

Connectez-vous avec les identifiants suivants :
- **Nom d'utilisateur** : `admin`
- **Mot de passe** : `password123`

Vous pouvez maintenant télécharger des fichiers audio/vidéo ou démarrer un enregistrement audio en direct pour obtenir des transcriptions.

## Remarques

- Assurez-vous que le dossier `uploads` est accessible en écriture pour que l'application puisse y stocker les fichiers téléchargés et transcrits.
- Modifiez les identifiants par défaut dans `app.py` pour plus de sécurité avant de déployer l'application en production.
