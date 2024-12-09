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

def shutdown_raspberry():
    subprocess.call(['sudo', 'shutdown', 'now'])

def exit_app():
    app.quit()

def show_info():
    ip_address = get_ip_address()
    info_text.set(f"URL: http://{ip_address}:5000\nWiFi: transcript\nMot de passe: transcript")

app = tk.Tk()
app.title("Interface Raspberry Pi")

# Configurer la fenêtre pour qu'elle s'affiche en plein écran
app.attributes('-fullscreen', True)

info_text = tk.StringVar()

# Bouton pour afficher l'URL et les informations Wi-Fi
info_button = tk.Button(app, text="Afficher les infos Wi-Fi", command=show_info, font=("Helvetica", 16), width=25, height=2)
info_button.pack(pady=10)

# Label pour afficher l'URL et les informations Wi-Fi
info_label = tk.Label(app, textvariable=info_text, font=("Helvetica", 16))
info_label.pack(pady=20)

# Bouton pour éteindre le Raspberry Pi
shutdown_button = tk.Button(app, text="Éteindre le Raspberry Pi", command=shutdown_raspberry, font=("Helvetica", 16), width=25, height=2)
shutdown_button.pack(pady=10)

# Bouton pour sortir de l'application
exit_button = tk.Button(app, text="Sortir", command=exit_app, font=("Helvetica", 16), width=25, height=2)
exit_button.pack(pady=10)

app.mainloop()
