import tkinter as tk
import socket
import subprocess

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def start_recording():
    # Commande pour démarrer l'enregistrement via l'application transcript
    subprocess.Popen(['python3', 'app.py'])

def stop_recording():
    # Commande pour arrêter l'enregistrement
    # Cela peut nécessiter une implémentation spécifique pour arrêter le processus
    pass

def exit_app():
    app.quit()

app = tk.Tk()
app.title("Interface d'Enregistrement")

# Configurer la fenêtre pour qu'elle s'affiche en plein écran
app.attributes('-fullscreen', True)

# Afficher l'URL et les informations Wi-Fi
ip_address = get_ip_address()
url_label = tk.Label(app, text=f"URL: http://{ip_address}:5000", font=("Helvetica", 16))
url_label.pack(pady=20)

wifi_info = tk.Label(app, text="WiFi: transcript\nMot de passe: transcript", font=("Helvetica", 16))
wifi_info.pack(pady=20)

# Boutons pour démarrer et arrêter l'enregistrement
start_button = tk.Button(app, text="Démarrer l'enregistrement", command=start_recording, font=("Helvetica", 16), width=20, height=2)
start_button.pack(pady=10)

stop_button = tk.Button(app, text="Arrêter l'enregistrement", command=stop_recording, font=("Helvetica", 16), width=20, height=2)
stop_button.pack(pady=10)

# Bouton pour sortir de l'application
exit_button = tk.Button(app, text="Sortir", command=exit_app, font=("Helvetica", 16), width=20, height=2)
exit_button.pack(pady=10)

app.mainloop()
