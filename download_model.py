import whisper
import os

def download_and_save_model(model_name="small", save_dir="models"):
    """
    Télécharge le modèle Whisper spécifié et le sauvegarde dans le répertoire local.
    """
    # Créer le répertoire de sauvegarde s'il n'existe pas
    os.makedirs(save_dir, exist_ok=True)
    
    # Charger le modèle
    model = whisper.load_model(model_name)
    
    # Sauvegarder le modèle dans le répertoire spécifié
    model.save_pretrained(save_dir)

if __name__ == "__main__":
    download_and_save_model()
