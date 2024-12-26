import qrcode
from PIL import Image
import os

while True:
    def generate_qr_code(name, surname, cls, number):
        # Crea il testo per il QR code
        qr_data = f"{name}--{surname}--{cls}--{number}"
        
        # Crea il QR code
        qr = qrcode.QRCode(
            version=1,  # La versione determina la dimensione del QR code
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,  # Dimensione della singola "scatola" del QR code
            border=4,  # Spessore del bordo del QR code
        )
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Crea l'immagine del QR code
        img = qr.make_image(fill='black', back_color='white')
        
        # Salva l'immagine come PNG
        file_name = f"{name}_{surname}_{cls}.png"
        img.save(f"qr_codes/{file_name}")
        
        print(f"QR code salvato come {file_name}")

    # Funzione per chiedere all'utente i dati
    def get_user_input():
        name = input("Inserisci il nome: ")
        surname = input("Inserisci il cognome: ")
        cls = input("Inserisci la classe: ")
        number = input("Inserisci un numero identificativo: ")
        
        # Genera il QR code con i dati inseriti
        generate_qr_code(name, surname, cls, number)

    # Crea la cartella per salvare i QR code se non esiste
    if not os.path.exists("qr_codes"):
        os.mkdir("qr_codes")

    # Avvio del programma
    get_user_input()
