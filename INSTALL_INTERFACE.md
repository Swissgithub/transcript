# Guide d'Installation pour l'Interface Graphique sur Raspberry Pi

## Prérequis

- Assurez-vous que Python 3.x est installé sur votre Raspberry Pi.
- Installez Tkinter si ce n'est pas déjà fait. Vous pouvez l'installer avec la commande suivante :

```bash
sudo apt-get install python3-tk
```

## Étapes d'Installation

### 1. Copier le Script sur le Raspberry Pi

Assurez-vous que le fichier `start_interface.py` est présent sur votre Raspberry Pi. Vous pouvez le transférer via SCP, FTP, ou tout autre moyen de transfert de fichiers.

### 2. Configurer l'Exécution Automatique au Démarrage

Pour exécuter le script automatiquement au démarrage, ajoutez la commande suivante à la fin du fichier `~/.bashrc` :

```bash
python3 /chemin/vers/start_interface.py
```

Remplacez `/chemin/vers/start_interface.py` par le chemin absolu vers le fichier `start_interface.py` sur votre Raspberry Pi.

### 3. Redémarrer le Raspberry Pi

Redémarrez votre Raspberry Pi pour appliquer les changements :

```bash
sudo reboot
```

## Utilisation

Une fois le Raspberry Pi redémarré, l'interface graphique devrait s'afficher automatiquement. Vous pouvez utiliser les boutons pour démarrer et arrêter l'enregistrement, et voir l'URL et les informations de connexion Wi-Fi.

## Remarques

- Assurez-vous que le Raspberry Pi est connecté à un écran pour voir l'interface graphique.
- Vérifiez que le réseau Wi-Fi "transcript" est configuré et actif sur votre Raspberry Pi.
