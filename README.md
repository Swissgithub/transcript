# transcript

## Description

Cette application web Flask permet de télécharger des fichiers audio et vidéo, de les transcrire en texte, et de gérer des enregistrements audio en direct.

## Installation

1. Clonez le dépôt :

```bash
$ git clone <URL_DU_DEPOT>
$ cd transcript
```

2. Créez un environnement virtuel et activez-le :

```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

3. Installez les dépendances :

```bash
$ pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application Flask :

```bash
$ flask run
```

2. Ouvrez votre navigateur et allez à l'adresse [http://127.0.0.1:5000](http://127.0.0.1:5000).

3. Connectez-vous avec les identifiants suivants :
   - **Nom d'utilisateur** : `admin`
   - **Mot de passe** : `password123`

4. Téléchargez un fichier audio ou vidéo, ou démarrez un enregistrement audio en direct.

5. Visualisez la transcription générée.

## Exemples d'utilisation

- **Téléchargement de fichiers** : Téléchargez un fichier audio ou vidéo et obtenez la transcription en texte.
- **Enregistrement en direct** : Démarrez et arrêtez l'enregistrement audio en direct, puis visualisez la transcription.

## Dépendances

- Flask
- Gunicorn
- OpenAI Whisper
- ffmpeg-python
- PyAudio
- MoviePy
- Flask-HTTPAuth
- Torch

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements que vous souhaitez apporter.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.