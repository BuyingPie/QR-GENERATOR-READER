import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import os
import pygame

# Inizializza la libreria per i suoni
pygame.mixer.init()

# Percorso per i file audio
current_dir = os.path.dirname(os.path.abspath(__file__))
sound_ok_path = os.path.join(current_dir, "ok.wav")
sound_error_path = os.path.join(current_dir, "error.wav")

try:
    soundOK = pygame.mixer.Sound(sound_ok_path)
    soundERROR = pygame.mixer.Sound(sound_error_path)
except pygame.error as e:
    messagebox.showerror("Errore Audio", f"Errore nel caricamento dei file audio: {e}")
    soundOK = None
    soundERROR = None

# Variabili globali
stop_mode = False
cap = None  # Variabile per il flusso video


# Funzione per elaborare i dati del QR code
def parse_barcode(barcode):
    try:
        name, surname, cls, role = barcode.split("--")
        role_dict = {
            "1": "Studente",
            "2": "Rappresentante di Classe",
            "3": "Rappresentante di Istituto",
            "4": "Admin"
        }
        role_text = role_dict.get(role.strip(), "Ruolo sconosciuto")
        return name.strip(), surname.strip(), cls.strip(), role_text
    except ValueError:
        return None, None, None, None


# Funzione per aggiornare il file con le nuove informazioni
def check_and_update_file(name, surname, cls):
    file_path = "student_data.txt"
    new_entry = f"{name},{surname},{cls}\n"

    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write(new_entry)
        return False

    with open(file_path, "r") as file:
        entries = file.readlines()

    for entry in entries:
        if entry.strip() == new_entry.strip():
            return True

    with open(file_path, "a") as file:
        file.write(new_entry)
    return False


# Funzione per processare i QR code
def process_barcode(barcode):
    name, surname, cls, role_text = parse_barcode(barcode)

    if name:
        # Controlla se l'utente è già nel file
        duplicate = check_and_update_file(name, surname, cls)

        if duplicate:
            if soundERROR:
                soundERROR.play()
            print("Duplicato trovato:", name)
        else:
            # Aggiorna il pannello di ispezione
            inspection_name_label["text"] = f"Nome: {name}"
            inspection_surname_label["text"] = f"Cognome: {surname}"
            inspection_class_label["text"] = f"Classe: {cls}"
            inspection_role_label["text"] = f"Ruolo: {role_text}"

            # Aggiorna il pannello pubblico
            public_greeting_label["text"] = f"Benvenuto {name}!"
            if soundOK:
                soundOK.play()

            display_photo(name)

            # Mostra "AVANTI" dopo 2 secondi
            public_window.after(2000, lambda: public_greeting_label.config(text="AVANTI"))


# Funzione per visualizzare le foto
def display_photo(name):
    image_path = f"images/{name.lower()}.jpg"
    try:
        img = Image.open(image_path).resize((150, 150))
        img = ImageTk.PhotoImage(img)

        inspection_photo_label.config(image=img)
        inspection_photo_label.image = img

        public_photo_label.config(image=img)
        public_photo_label.image = img
    except FileNotFoundError:
        print(f"Immagine non trovata per {name}")


# Funzione per avviare il flusso video
def start_video_stream():
    global cap
    selected_index = int(camera_index.get())
    cap = cv2.VideoCapture(selected_index)

    def update_frame():
        if not cap:
            return

        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Errore", "Impossibile accedere alla videocamera.")
            return

        # Ridimensiona il frame
        frame = cv2.resize(frame, (320, 240))

        # Decodifica i QR code
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            barcode_data = obj.data.decode("utf-8")
            process_barcode(barcode_data)

        # Converte il frame in formato Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(img)

        camera_label.config(image=img_tk)
        camera_label.image = img_tk

        camera_label.after(30, update_frame)

    update_frame()


# Funzione per fermare il flusso video
def stop_video_stream():
    global cap
    if cap:
        cap.release()
        cap = None


# Creazione dell'interfaccia grafica principale
root = tk.Tk()
root.title("Sistema di Ispezione e Accoglienza")

# Frame principale
inspection_frame = ttk.LabelFrame(root, text="Portale di Ispezione")
inspection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Menu a tendina per selezionare la telecamera
camera_index = tk.StringVar(value="0")
ttk.Label(inspection_frame, text="Seleziona Telecamera:").grid(row=0, column=0, padx=5, pady=5)
camera_menu = ttk.Combobox(inspection_frame, textvariable=camera_index, values=["0", "1", "2", "3"])
camera_menu.grid(row=0, column=1, padx=5, pady=5)
camera_menu.current(0)

# Pulsanti per avviare/fermare il flusso video
ttk.Button(inspection_frame, text="Avvia Camera", command=start_video_stream).grid(row=1, column=0, padx=5, pady=5)
ttk.Button(inspection_frame, text="Ferma Camera", command=stop_video_stream).grid(row=1, column=1, padx=5, pady=5)

# Label per visualizzare il video
camera_label = ttk.Label(inspection_frame)
camera_label.grid(row=2, column=0, columnspan=2, pady=10)

# Etichette di ispezione
inspection_name_label = ttk.Label(inspection_frame, text="Nome: ")
inspection_name_label.grid(row=3, column=0, columnspan=2, sticky="w")
inspection_surname_label = ttk.Label(inspection_frame, text="Cognome: ")
inspection_surname_label.grid(row=4, column=0, columnspan=2, sticky="w")
inspection_class_label = ttk.Label(inspection_frame, text="Classe: ")
inspection_class_label.grid(row=5, column=0, columnspan=2, sticky="w")
inspection_role_label = ttk.Label(inspection_frame, text="Ruolo: ")
inspection_role_label.grid(row=6, column=0, columnspan=2, sticky="w")

inspection_photo_label = ttk.Label(inspection_frame)
inspection_photo_label.grid(row=7, column=0, columnspan=2)

# Pannello pubblico
public_window = tk.Toplevel(root)
public_window.title("Schermo Pubblico")
public_greeting_label = ttk.Label(public_window, text="", font=("Helvetica", 60))
public_greeting_label.pack(expand=True, fill="both")
public_photo_label = ttk.Label(public_window)
public_photo_label.pack()

root.mainloop()
