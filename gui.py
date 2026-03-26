import tkinter as tk
from PIL import ImageTk, Image
import db, db_biljke, db_posude, db_senzori, db_posude_records
import sqlite3
from tkinter import messagebox
import sync
import random
from random import randint
import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class App(tk.Tk):
    def __init__(self, conn):
        super().__init__()

        self.conn = conn
        self.title("PyFloraPosuda")
        self.geometry('800x600')
        self.config(bg="#2d5a27")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Naslov
        login_lbl = tk.Label(self, text="PyFloraPosude", bg="#2176C1", fg='white', relief='raised')
        login_lbl.pack(ipady=5, fill='x')
        login_lbl.config(font=("Arial", 20, 'bold'))

        # Pozadinska slika
        try:
            image_path = os.path.join(BASE_DIR, "soil.jpg")
            raw_image = Image.open(image_path)
            raw_image = raw_image.resize((800, 200))
            self.background_image = ImageTk.PhotoImage(raw_image)
            self.background_label = tk.Label(self, image=self.background_image)
            self.background_label.pack()
        except Exception as e:
            print(f"Greška pri učitavanju slike: {e}")
            tk.Label(self, text="", bg="#2d5a27", height=5).pack()

        # Login naslov
        tk.Label(self, text="Prijava", bg="#2d5a27", fg="white",
                 font=("Arial", 24, "bold")).pack(pady=(10, 5))

        # Username
        username_frame = tk.Frame(self, bg="#2d5a27")
        username_frame.pack(pady=3)
        tk.Label(username_frame, text="Korisničko ime:", bg="#2d5a27",
                 fg="white", width=18, anchor='e').pack(side='left', padx=5)
        username_entry = tk.Entry(username_frame, bd=3, width=25)
        username_entry.pack(side='right')

        # Password
        password_frame = tk.Frame(self, bg="#2d5a27")
        password_frame.pack(pady=3)
        tk.Label(password_frame, text="Lozinka:", bg="#2d5a27",
                 fg="white", width=18, anchor='e').pack(side='left', padx=5)
        password_entry = tk.Entry(password_frame, bd=3, show='*', width=25)
        password_entry.pack(side='right')

        # Poruka o grešci
        error_lbl = tk.Label(self, text="", bg="#2d5a27", fg="#ff6b6b",
                             font=("Arial", 10))
        error_lbl.pack()

        def checkInput():
            entered_usernm = username_entry.get()
            entered_pswrd = password_entry.get()

            if not entered_usernm or not entered_pswrd:
                error_lbl.config(text="Molim unesite korisničko ime i lozinku!")
                return

            result = db.get_user(self.conn, entered_usernm)
            if result is not None and entered_pswrd == result[3]:
                print(f'Dobrodošli {result[0]} {result[1]}!')
                username_entry.config(state='disabled')
                password_entry.config(state='disabled')
                prijava_button.config(state='disabled')
                error_lbl.config(text="")
                top = Window(self)
                top.focus()
            else:
                error_lbl.config(text="Pogrešno korisničko ime ili lozinka!")
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)

        # Bind Enter na prijavu
        self.bind('<Return>', lambda e: checkInput())

        prijava_button = tk.Button(self, text="Prijavi se!", command=checkInput,
                                   bg="#1a6b14", fg="white", width=17,
                                   font=("Arial", 11, "bold"), bd=3)
        prijava_button.pack(pady=15)

    def on_closing(self):
        if messagebox.askokcancel("Izlaz", "Želite li zatvoriti program?"):
            self.conn.close()
            self.destroy()


class Window(tk.Toplevel):
    def __init__(self, container):
        super().__init__(container)
        self.geometry('1400x900')
        self.title('PyFloraPosuda')
        self.config(bg="#f0f0f0")

        self.conn = sqlite3.connect("./data/PyFloraPosuda.db")

        # --- Gornji toolbar ---
        toolbar = tk.Frame(self, bg="#2176C1", pady=5)
        toolbar.grid(row=0, column=0, columnspan=10, sticky='EW')

        tk.Label(toolbar, text="PyFloraPosude", bg="#2176C1", fg="white",
                 font=("Arial", 14, "bold")).pack(side='left', padx=15)

        global sync_btn
        sync_btn = tk.Button(toolbar, text='🔄 Sync', command=self._sync,
                             height=1, width=10, font=('Arial', 11, 'bold'),
                             bg="#4CAF50", fg="white", bd=2)
        sync_btn.pack(side='right', padx=10, pady=2)

        global moj_profil_btn
        moj_profil_btn = tk.Button(toolbar, text='👤 Moj Profil',
                                   command=self.profil, height=1, width=12,
                                   font=('Arial', 11, 'bold'),
                                   bg="#1a6b14", fg="white", bd=2)
        moj_profil_btn.pack(side='right', padx=5, pady=2)

        # --- Dohvati korisnika ---
        username_tuple = db.select_username(self.conn)
        username = ''
        print(f'username_tuple = {username_tuple}')
        if username_tuple:
            for user in username_tuple:
                username += user

        record = db.get_user(self.conn, username)
        self.ime = record[0]
        self.prezime = record[1]
        self.username = record[2]
        self.password = record[3]

        # --- Profil widgeti (skriveni u početku) ---
        self.profil_frame = tk.Frame(self, bg="#f0f0f0", padx=10, pady=10)

        tk.Label(self.profil_frame, text="Moj Profil", bg="#f0f0f0",
                 font=("Arial", 16, "bold")).grid(row=0, column=0,
                                                   columnspan=4, pady=(0, 10))

        tk.Label(self.profil_frame, text="Ime:", bg="#f0f0f0").grid(
            row=1, column=0, sticky='E', padx=5)
        self.var_ime = tk.StringVar(value=self.ime)
        self.ime_entry = tk.Entry(self.profil_frame, textvariable=self.var_ime,
                                  state='disabled', width=20)
        self.ime_entry.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(self.profil_frame, text="Prezime:", bg="#f0f0f0").grid(
            row=2, column=0, sticky='E', padx=5)
        self.var_prezime = tk.StringVar(value=self.prezime)
        self.prezime_entry = tk.Entry(self.profil_frame,
                                      textvariable=self.var_prezime,
                                      state='disabled', width=20)
        self.prezime_entry.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(self.profil_frame, text="Korisničko ime:", bg="#f0f0f0").grid(
            row=3, column=0, sticky='E', padx=5)
        self.var_username = tk.StringVar(value=self.username)
        self.username_entry = tk.Entry(self.profil_frame,
                                       textvariable=self.var_username,
                                       state='disabled', width=20)
        self.username_entry.grid(row=3, column=1, padx=5, pady=3)

        tk.Label(self.profil_frame, text="Lozinka:", bg="#f0f0f0").grid(
            row=4, column=0, sticky='E', padx=5)
        self.var_password = tk.StringVar(value=self.password)
        self.password_entry = tk.Entry(self.profil_frame,
                                       textvariable=self.var_password,
                                       show='*', state='disabled', width=20)
        self.password_entry.grid(row=4, column=1, padx=5, pady=3)

        self.check = tk.Checkbutton(self.profil_frame, text='Prikaži lozinku',
                                    command=self.show, bg="#f0f0f0")
        self.check.grid(row=4, column=2, padx=5)

        # Gumbi profila
        btn_frame_profil = tk.Frame(self.profil_frame, bg="#f0f0f0")
        btn_frame_profil.grid(row=5, column=0, columnspan=4, pady=10)

        self.natrag_btn = tk.Button(btn_frame_profil, text='◀ Natrag',
                                    command=self.natrag_button, width=12, bd=2)
        self.natrag_btn.pack(side='left', padx=5)

        self.uredi_btn = tk.Button(btn_frame_profil, text='✏ Uredi',
                                   command=self.uredi, width=12, bd=2,
                                   bg="#2176C1", fg="white")
        self.uredi_btn.pack(side='left', padx=5)

        self.spremi_btn = tk.Button(btn_frame_profil, text='💾 Spremi',
                                    command=self.spremi, width=12, bd=2,
                                    bg="#4CAF50", fg="white")

        self.izbrisi_btn = tk.Button(btn_frame_profil,
                                     text='🗑 Izbriši račun',
                                     command=self.izbrisi, width=15, bd=2,
                                     bg="#c0392b", fg="white")

        # --- Posude frame ---
        self.posude_frame = PosudeFrame(self)
        self.posude_frame.grid(row=1, column=0, sticky='NW', padx=5, pady=5)

    def _sync(self):
        sync.syncronize()
        messagebox.showinfo("Sync", "Sinkronizacija podataka uspješna!")
        # Osvježi prikaz ako je neka posuda odabrana
        self.posude_frame.osvjezi_prikaz()

    def profil(self):
        self.posude_frame.grid_remove()
        self.profil_frame.grid(row=1, column=0, sticky='NW', padx=10, pady=10)
        self.natrag_btn.pack(side='left', padx=5)
        self.uredi_btn.pack(side='left', padx=5)
        self.spremi_btn.pack_forget()
        self.izbrisi_btn.pack_forget()
        self.check.grid_remove()

    def uredi(self):
        self.ime_entry.config(state='normal')
        self.prezime_entry.config(state='normal')
        self.username_entry.config(state='normal')
        self.password_entry.config(state='normal')
        self.uredi_btn.pack_forget()
        self.natrag_btn.pack_forget()
        self.spremi_btn.pack(side='left', padx=5)
        self.izbrisi_btn.pack(side='left', padx=5)
        self.check.grid(row=4, column=2, padx=5)

    def show(self):
        self.password_entry.configure(show='')
        self.check.configure(command=self.hide, text='Sakrij lozinku')

    def hide(self):
        self.password_entry.configure(show='*')
        self.check.configure(command=self.show, text='Prikaži lozinku')

    def natrag_button(self):
        self.profil_frame.grid_remove()
        self.posude_frame.grid()
        self.check.grid_remove()
        self.ime_entry.config(state='disabled')
        self.prezime_entry.config(state='disabled')
        self.username_entry.config(state='disabled')
        self.password_entry.config(state='disabled')

    def izbrisi(self):
        if messagebox.askyesno(message='Jeste li sigurni da želite izbrisati korisnički račun?'):
            db.delete_user(self.conn, self.username)
            self.destroy()

    def spremi(self):
        novo_ime = self.ime_entry.get().strip()
        novo_prezime = self.prezime_entry.get().strip()
        novi_username = self.username_entry.get().strip()
        nova_lozinka = self.password_entry.get().strip()

        if not novo_ime or not novo_prezime or not novi_username or not nova_lozinka:
            messagebox.showerror(title="Greška", message="Sva polja moraju biti popunjena!")
            return

        self.ime_entry.config(state='disabled')
        self.prezime_entry.config(state='disabled')
        self.username_entry.config(state='disabled')
        self.password_entry.config(state='disabled')
        self.spremi_btn.pack_forget()
        self.izbrisi_btn.pack_forget()
        self.natrag_btn.pack(side='left', padx=5)
        self.uredi_btn.pack(side='left', padx=5)
        self.check.grid_remove()

        # Ažuriraj u bazi (delete + add jer update_user postoji ali nije uvijek pouzdan)
        db.delete_user(self.conn, self.username)
        db.add_user(self.conn, novo_ime, novo_prezime, novi_username, nova_lozinka)

        # Ažuriraj lokalne varijable
        self.ime = novo_ime
        self.prezime = novo_prezime
        self.username = novi_username
        self.password = nova_lozinka

        messagebox.showinfo("Uspjeh", "Podaci uspješno spremljeni!")


class PosudeFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container, bg="#f0f0f0")

        self.conn = sqlite3.connect("./data/PyFloraPosuda.db")
        self.record = ()
        self.biljka = ''

        # --- Placeholderi za grafove ---
        self.canvas = tk.Label(self)
        self.canvas_1 = tk.Label(self)
        self.canvas_2 = tk.Label(self)
        self.canvas_3 = tk.Label(self)
        self.canvas_4 = tk.Label(self)

        # --- Lista posuda ---
        self.free_plants = db_biljke.select_free_plants(self.conn)
        self.listaposuda = set()
        listaposude_ = db_posude.select_all_pots(self.conn)
        if listaposude_:
            for posuda_ in listaposude_:
                for posuda in posuda_:
                    self.listaposuda.add(posuda)

        # ========================
        # LIJEVA KOLUMNA – lista posuda (normalni prikaz)
        # ========================
        self.posude_lbl = tk.Label(self, font=('Arial', 11, 'bold'),
                                   text='Moje PyPosude', bg="#f0f0f0")
        self.posude_lbl.grid(row=0, column=0, sticky='W', pady=(5, 0))

        self.lstbx_posuda = tk.Listbox(self, borderwidth=3, height=14,
                                       width=20, selectbackground="#2176C1",
                                       font=('Arial', 10))
        self.lstbx_posuda.grid(row=1, rowspan=3, column=0, padx=5)

        # Popuni samo zauzetim posudama
        for element in self.listaposuda:
            pot = db_posude.get_pot(self.conn, element)
            if pot and pot[1] != 'PRAZNA posuda':
                self.lstbx_posuda.insert("end", element)


        self.crud_posuda_btn = tk.Button(self, text='Uredi posude i biljke',
                                         command=self.uredi_posude,
                                         font=('Arial', 10, 'bold'),
                                         bg="#2176C1", fg="white", bd=2)
        self.crud_posuda_btn.grid(row=5, column=0, pady=3)

        # ========================
        # DESNA KOLUMNA – detalji odabrane posude
        # ========================

        # Naziv biljke iznad slike
        self.var_plant_img = tk.StringVar(value='')
        self.img_photo_lbl = tk.Label(self, textvariable=self.var_plant_img,
                                      font=('Arial', 12, 'bold'), bg="#f0f0f0",
                                      pady=5)

        # Slika biljke
        self.background_label = tk.Label(self, image='', borderwidth=3,
                                         relief='groove')
        self.background_label_2 = tk.Label(self, image='', borderwidth=3,
                                            relief='groove')

        # Senzori labeli
        self.senzor_svjetlost = tk.Label(self,
                                         text='Svjetlost (FC)',
                                         font=('Arial', 9, 'bold'), bg="#f0f0f0")
        self.senzor_svjetlost_vrijednost = tk.Label(self, font=('Arial', 11),
                                                    bg="#e8f5e9", width=10,
                                                    relief='groove')
        self.senzor_ph = tk.Label(self, text='pH vrijednost',
                                  font=('Arial', 9, 'bold'), bg="#f0f0f0")
        self.senzor_ph_vrijednost = tk.Label(self, font=('Arial', 11),
                                             bg="#e8f5e9", width=10,
                                             relief='groove')
        self.senzor_salinitet = tk.Label(self, text='Salinitet (mS/cm)',
                                         font=('Arial', 9, 'bold'), bg="#f0f0f0")
        self.senzor_salinitet_vrijednost = tk.Label(self, font=('Arial', 11),
                                                    bg="#e8f5e9", width=10,
                                                    relief='groove')
        self.senzor_vlaga = tk.Label(self, text='Vlažnost (%)',
                                     font=('Arial', 9, 'bold'), bg="#f0f0f0")
        self.senzor_vlaga_vrijednost = tk.Label(self, font=('Arial', 11),
                                                bg="#e8f5e9", width=10,
                                                relief='groove')
        self.senzor_temp = tk.Label(self, text='Temperatura (°C)',
                                    font=('Arial', 9, 'bold'), bg="#f0f0f0")
        self.senzor_temp_vrijednost = tk.Label(self, font=('Arial', 11),
                                               bg="#e8f5e9", width=10,
                                               relief='groove')

        # Aktivnosti
        self.svjetlost_aktivnost = tk.Label(self, text='Aktivnost:',
                                            font=('Arial', 9), bg="#f0f0f0",
                                            wraplength=150, justify='left')
        self.ph_aktivnost = tk.Label(self, text='Aktivnost:',
                                     font=('Arial', 9), bg="#f0f0f0",
                                     wraplength=150, justify='left')
        self.salinitet_aktivnost = tk.Label(self, text='Aktivnost:',
                                            font=('Arial', 9), bg="#f0f0f0",
                                            wraplength=150, justify='left')
        self.vlaga_aktivnost = tk.Label(self, text='Aktivnost:',
                                        font=('Arial', 9), bg="#f0f0f0",
                                        wraplength=150, justify='left')
        self.temp_aktivnost = tk.Label(self, text='Aktivnost:',
                                       font=('Arial', 9), bg="#f0f0f0",
                                       wraplength=150, justify='left')

        self.akcija_btn = tk.Button(self, command=self.akcija,
                                    text='Pokreni aktivnost!', height=2,
                                    width=20, font=('Arial', 10, 'bold'),
                                    bg="#e67e22", fg="white", bd=3)

        self.plot_button = tk.Button(self, command=self.plot, text='📊 Grafovi',
                                     width=20, borderwidth=3,
                                     font=('Arial', 10, 'bold'),
                                     bg="#9b59b6", fg="white")

        # ========================
        # UREDI POSUDE widgeti
        # ========================
        self.lstbx_posuda_uredi = tk.Listbox(self, borderwidth=3, height=14,
                                             width=20, selectbackground="#2176C1",
                                             font=('Arial', 10))

        self.dodaj_posudu_btn = tk.Button(self, command=self.dodaj_posudu,
                                          borderwidth=2, width=18,
                                          text='➕ Dodaj posudu',
                                          bg="#4CAF50", fg="white",
                                          font=('Arial', 9, 'bold'))
        self.uredi_natrag_btn = tk.Button(self, text='◀ Natrag',
                                          command=self.natrag_uredi,
                                          borderwidth=2, width=18,
                                          font=('Arial', 9))

        self.dodaj_biljku_btn = tk.Button(self, text='➕ Dodaj biljku',
                                          width=18, borderwidth=2,
                                          bg="#4CAF50", fg="white",
                                          font=('Arial', 9, 'bold'))
        self.isprazni_posudu_btn = tk.Button(self, text='↩ Isprazni posudu',
                                             borderwidth=2, width=18,
                                             bg="#e67e22", fg="white",
                                             font=('Arial', 9, 'bold'))
        self.azuriraj_biljku_btn = tk.Button(self, text='✏ Ažuriraj biljku',
                                             borderwidth=2, width=18,
                                             bg="#2176C1", fg="white",
                                             font=('Arial', 9, 'bold'))
        self.izbrisi_posudu_btn = tk.Button(self, text='🗑 Izbriši posudu',
                                            borderwidth=2, width=18,
                                            bg="#c0392b", fg="white",
                                            font=('Arial', 9, 'bold'))
        self.azuriraj_posudu_btn = tk.Button(self, text='✏ Ažuriraj posudu',
                                             borderwidth=2, width=18,
                                             bg="#2176C1", fg="white",
                                             font=('Arial', 9, 'bold'))

        # Baza biljaka
        self.baza_biljaka_btn = tk.Button(self, width=18,
                                          font=('Arial', 9, 'bold'),
                                          borderwidth=2,
                                          text='🌿 Baza biljaka',
                                          bg="#1a6b14", fg="white")
        self.baza_biljaka_lstbx = tk.Listbox(self, borderwidth=3, height=14,
                                             width=20, selectbackground="#2176C1",
                                             font=('Arial', 10))

        self.var_baza_posuda = tk.StringVar()
        self.baza_ime_posude = tk.Label(self, font=('Arial', 10),
                                        textvariable=self.var_baza_posuda,
                                        bg="#f0f0f0")

        # Dodaj biljku u posudu
        self.dodaj_biljku_lstbox = tk.Listbox(self, borderwidth=3, height=14,
                                              width=20, selectbackground="#2176C1",
                                              font=('Arial', 10))
        self.dodaj_biljku_lstbox_ = tk.Listbox(self, borderwidth=3, height=14,
                                               width=20, selectbackground="#2176C1",
                                               font=('Arial', 10))
        self.stavi_biljku_btn = tk.Button(self, text='✔ Stavi', width=18,
                                          bg="#4CAF50", fg="white",
                                          font=('Arial', 9, 'bold'))
        self.odustani_stavi_biljku_btn = tk.Button(self, text='✖ Odustani',
                                                   width=18, font=('Arial', 9))

        # Entry polja
        self.var_posuda_entry = tk.StringVar(value='')
        self.var_biljka_entry = tk.StringVar(value='')
        self.dodaj_biljku_entry = tk.Entry(self, bd=3, width=25,
                                           textvariable=self.var_biljka_entry)
        self.dodaj_posudu_entry = tk.Entry(self, bd=3, width=25,
                                           textvariable=self.var_posuda_entry)

        self.odustani_btn = tk.Button(self, text='✖ Odustani',
                                      command=self.odustani, width=18,
                                      font=('Arial', 9))
        self.odustani_btn_ = tk.Button(self, text='✖ Odustani',
                                       command=self.odustani_, width=18,
                                       font=('Arial', 9))
        self.ok_btn = tk.Button(self, text='✔ OK', width=10,
                                bg="#4CAF50", fg="white",
                                font=('Arial', 9, 'bold'))
        self.upisi_ime_posude_lbl = tk.Label(self, text='Upiši naziv posude',
                                             font=('Arial', 10), bg="#f0f0f0")
        self.stavi_btn = tk.Button(self, text='✔ Stavi', width=18,
                                   bg="#4CAF50", fg="white",
                                   font=('Arial', 9, 'bold'))
        self.ostavi_prazno_btn = tk.Button(self, text='Ostavi praznu',
                                           width=18, font=('Arial', 9))

        self.lokacija_lbl = tk.Label(self, text='Lokacija: ', width=30,
                                     borderwidth=2, relief='groove',
                                     font=('Arial', 10, 'bold'), bg="#e8f5e9")

        # Bind lista posuda (normalni prikaz)
        self.lstbx_posuda.bind("<<ListboxSelect>>", self._onselect_posuda)

    # ====================================================================
    # POMOĆNA METODA: osvježi trenutni prikaz nakon synca
    # ====================================================================
    def osvjezi_prikaz(self):
        if not self.record:
            return
        try:
            posuda_naziv = self.record[0]
            self.record = db_posude.get_pot(self.conn, posuda_naziv)
            if self.record and self.record[1] != 'PRAZNA posuda':
                self._prikazi_senzore(self.record)
        except Exception as e:
            print(f"Osvježi greška: {e}")

    # ====================================================================
    # PRIVATNE POMOĆNE METODE ZA PRIKAZ SENZORA
    # ====================================================================
    def _prikazi_senzore(self, record):
        """Dohvati zadnje senzorske podatke i prikaži aktivnosti."""
        try:
            data = db_posude_records.select_last_sensor(self.conn, record[1])
            if data is None:
                data = db_posude.select_last_sensor(self.conn, record[1])
            if data is None:
                return

            _, _, _, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, _ = data

            self.senzor_svjetlost_vrijednost.config(text=str(dubina_svjetlosti))
            self.senzor_ph_vrijednost.config(text=str(pH))
            self.senzor_salinitet_vrijednost.config(text=str(salinitet))
            self.senzor_vlaga_vrijednost.config(text=str(vlaznost))
            self.senzor_temp_vrijednost.config(text=str(temperatura))

            # Aktivnosti
            if dubina_svjetlosti < 200:
                self.svjetlost_aktivnost.config(text='⚠ Staviti na sunce',
                                                fg='#e67e22')
            elif dubina_svjetlosti > 1200:
                self.svjetlost_aktivnost.config(text='⚠ Staviti u hlad',
                                                fg='#e67e22')
            else:
                self.svjetlost_aktivnost.config(text='✔ Ok', fg='#27ae60')

            if pH < 6.50:
                self.ph_aktivnost.config(text='⚠ Dodati sodu bikarbonu',
                                         fg='#e67e22')
            elif pH > 7.50:
                self.ph_aktivnost.config(text='⚠ Dodati sumpornu kiselinu',
                                          fg='#e67e22')
            else:
                self.ph_aktivnost.config(text='✔ Ok', fg='#27ae60')

            if salinitet < 0.50:
                self.salinitet_aktivnost.config(text='⚠ Dodati nutricije',
                                                fg='#e67e22')
            elif salinitet > 2.50:
                self.salinitet_aktivnost.config(text='⚠ Navodniti čistom vodom',
                                                fg='#e67e22')
            else:
                self.salinitet_aktivnost.config(text='✔ Ok', fg='#27ae60')

            if vlaznost < 60:
                self.vlaga_aktivnost.config(text='⚠ Zamagliti biljku',
                                            fg='#e67e22')
            elif vlaznost > 80:
                self.vlaga_aktivnost.config(text='⚠ Staviti na toplije mjesto',
                                            fg='#e67e22')
            else:
                self.vlaga_aktivnost.config(text='✔ Ok', fg='#27ae60')

            if temperatura < 20:
                self.temp_aktivnost.config(
                    text='⚠ Premjestiti u manju prostoriju', fg='#e67e22')
            elif temperatura > 25:
                self.temp_aktivnost.config(
                    text='⚠ Premjestiti u veću prostoriju', fg='#e67e22')
            else:
                self.temp_aktivnost.config(text='✔ Ok', fg='#27ae60')

            # Provjeri treba li aktivnost gumb
            sve_ok = all(
                lbl["text"] == '✔ Ok'
                for lbl in [self.svjetlost_aktivnost, self.ph_aktivnost,
                             self.salinitet_aktivnost, self.vlaga_aktivnost,
                             self.temp_aktivnost]
            )
            if sve_ok:
                self.akcija_btn.grid_remove()
            else:
                self.akcija_btn.grid(row=0, column=2, rowspan=2, sticky='S',
                                     padx=5)

            # Ažuriraj status biljke u bazi
            aktivnosti = [lbl["text"] for lbl in
                          [self.svjetlost_aktivnost, self.ph_aktivnost,
                           self.salinitet_aktivnost, self.vlaga_aktivnost,
                           self.temp_aktivnost]
                          if '⚠' in lbl["text"]]
            if aktivnosti:
                status = '\n'.join(aktivnosti)
                db_biljke.update_status_biljke(self.conn, record[1], status)
            else:
                db_biljke.update_status_biljke(self.conn, record[1], 'OK')

        except Exception as e:
            print(f"Greška pri prikazu senzora: {e}")

    def _ucitaj_sliku_biljke(self, naziv_biljke, label_widget):
        """Učitaj i prikaži sliku biljke na zadani Label widget."""
        try:
            (_, photoPath, _) = db_biljke.get_plant(self.conn, naziv_biljke)
            raw_image = Image.open(photoPath)
            raw_image = raw_image.resize((250, 175))
            _image = ImageTk.PhotoImage(raw_image)
            label_widget.config(image=_image)
            label_widget.image = _image
            return True
        except Exception as e:
            print(f"Greška pri učitavanju slike: {e}")
            return False

    def _ucitaj_praznu_sliku(self, label_widget):
        """Prikaži placeholder sliku za praznu posudu."""
        try:
            image_path = os.path.join(BASE_DIR, "empty_pot.jpg")
            raw_image = Image.open(image_path)
            raw_image = raw_image.resize((250, 175))
            _image = ImageTk.PhotoImage(raw_image)
            label_widget.config(image=_image)
            label_widget.image = _image
        except Exception:
            label_widget.config(image='', text='🪴 PRAZNA', width=20,
                                height=10, font=('Arial', 14))

    # ====================================================================
    # EVENT HANDLER – odabir posude u normalnom prikazu
    # ====================================================================
    def _onselect_posuda(self, event):
        selection = event.widget.curselection()
        sync_btn.config(state='normal')
        self.akcija_btn.grid_remove()

        if not selection:
            return

        index = int(selection[0])
        posuda = event.widget.get(index)
        self.record = db_posude.get_pot(self.conn, posuda)

        if not self.record:
            return

        # Prikaži plot gumb
        self.plot_button.grid(row=8, column=2, pady=5)
        self.unplot()
        self.crud_posuda_btn.grid(row=8, column=0, sticky='S')

        # Slika
        self.background_label.grid(row=1, rowspan=3, column=1, padx=10)
        self.img_photo_lbl.grid(row=0, column=1)
        self.var_plant_img.set(self.record[1])

        if self.record[1] != 'PRAZNA posuda':
            self._ucitaj_sliku_biljke(self.record[1], self.background_label)

            # Prikaži senzore
            self.senzor_svjetlost.grid(row=4, column=1)
            self.senzor_svjetlost_vrijednost.grid(row=5, column=1)
            self.senzor_ph.grid(row=4, column=2)
            self.senzor_ph_vrijednost.grid(row=5, column=2)
            self.senzor_salinitet.grid(row=4, column=3)
            self.senzor_salinitet_vrijednost.grid(row=5, column=3)
            self.senzor_vlaga.grid(row=4, column=4)
            self.senzor_vlaga_vrijednost.grid(row=5, column=4)
            self.senzor_temp.grid(row=4, column=5)
            self.senzor_temp_vrijednost.grid(row=5, column=5)

            self.svjetlost_aktivnost.grid(row=6, column=1, sticky='N')
            self.ph_aktivnost.grid(row=6, column=2, sticky='N')
            self.salinitet_aktivnost.grid(row=6, column=3, sticky='N')
            self.vlaga_aktivnost.grid(row=6, column=4, sticky='N')
            self.temp_aktivnost.grid(row=6, column=5, sticky='N')

            self._prikazi_senzore(self.record)
        else:
            self._ucitaj_praznu_sliku(self.background_label)
            self.akcija_btn.grid_remove()

            # Postavi senzore na '-'
            for lbl in [self.senzor_svjetlost_vrijednost,
                        self.senzor_ph_vrijednost,
                        self.senzor_salinitet_vrijednost,
                        self.senzor_vlaga_vrijednost,
                        self.senzor_temp_vrijednost]:
                lbl.config(text='-')
            for lbl in [self.svjetlost_aktivnost, self.ph_aktivnost,
                        self.salinitet_aktivnost, self.vlaga_aktivnost,
                        self.temp_aktivnost]:
                lbl.config(text='Aktivnost: -', fg='gray')

            self.senzor_svjetlost.grid(row=4, column=1)
            self.senzor_svjetlost_vrijednost.grid(row=5, column=1)
            self.senzor_ph.grid(row=4, column=2)
            self.senzor_ph_vrijednost.grid(row=5, column=2)
            self.senzor_salinitet.grid(row=4, column=3)
            self.senzor_salinitet_vrijednost.grid(row=5, column=3)
            self.senzor_vlaga.grid(row=4, column=4)
            self.senzor_vlaga_vrijednost.grid(row=5, column=4)
            self.senzor_temp.grid(row=4, column=5)
            self.senzor_temp_vrijednost.grid(row=5, column=5)
            self.svjetlost_aktivnost.grid(row=6, column=1, sticky='N')
            self.ph_aktivnost.grid(row=6, column=2, sticky='N')
            self.salinitet_aktivnost.grid(row=6, column=3, sticky='N')
            self.vlaga_aktivnost.grid(row=6, column=4, sticky='N')
            self.temp_aktivnost.grid(row=6, column=5, sticky='N')

    # ====================================================================
    # GRAFOVI
    # ====================================================================
    def plot(self):
        self.plot_button.config(command=self.unplot, text='❌ Zatvori grafove')

        if not self.record:
            return

        records = db_posude_records.select_all(self.conn, self.record[0])
        if not records:
            messagebox.showinfo("Info", "Nema dovoljno podataka za grafove. Pokrenite Sync.")
            return

        # --- PANDAS: učitaj records u DataFrame ---
        # Svaki record je tuple:
        # (id, naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme)
        df = pd.DataFrame(records, columns=[
            'id', 'naziv', 'biljka', 'dubina_svjetlosti',
            'pH', 'salinitet', 'vlaznost', 'temperatura', 'vrijeme'
        ])
        df['pH'] = df['pH'].round(0)

        # --- NUMPY: pretvori stupce u array za grafove i statistike ---
        ids               = np.arange(len(df))
        xlimit            = len(ids) + 2
        vlaga             = df['vlaznost'].to_numpy()
        salinitet         = df['salinitet'].to_numpy()
        dubina_svjetlosti = df['dubina_svjetlosti'].to_numpy()
        temp              = df['temperatura'].to_numpy()
        ph                = df['pH'].to_numpy()

        # NumPy bins za histogram — 8 jednakih intervala između min i max
        sal_bins = np.linspace(salinitet.min(), salinitet.max(), 8)

        # Graf 1 – Line: vlaga
        fig1 = Figure(figsize=(3, 2), dpi=100)
        plot1 = fig1.add_subplot(111)
        plot1.plot(ids, vlaga, color='#2980b9')
        plot1.set_ylabel('Vlažnost (%)')
        plot1.set_xlim([0, xlimit])
        # NumPy: prosječna vlažnost kao crvena isprekidana linija
        plot1.axhline(y=np.mean(vlaga), color='red', linestyle='--',
                      linewidth=0.8, label=f'Avg: {np.mean(vlaga):.1f}%')
        plot1.legend(fontsize=6)
        plot1.set_title('Vlažnost kroz vrijeme', fontsize=9)
        canvas = FigureCanvasTkAgg(fig1, self)
        canvas.draw()
        self.canvas = canvas.get_tk_widget()
        self.canvas.grid(row=9, column=1, columnspan=2, sticky='W', pady=3)
        plt.close('all')

        # Graf 2 – Histogram: salinitet (NumPy bins)
        fig2 = Figure(figsize=(3, 2), dpi=100)
        plot2 = fig2.add_subplot(111)
        plot2.hist(salinitet, bins=sal_bins, color='#27ae60', edgecolor='white')
        plot2.set_title('Salinitet histogram', fontsize=9)
        # NumPy: statistike u xlabel
        plot2.set_xlabel(f'Avg: {np.mean(salinitet):.2f} | ' 
                         f'Min: {np.min(salinitet):.2f} | '
                         f'Max: {np.max(salinitet):.2f}', fontsize=6)
        canvas_1 = FigureCanvasTkAgg(fig2, self)
        canvas_1.draw()
        self.canvas_1 = canvas_1.get_tk_widget()
        self.canvas_1.grid(row=10, column=1, pady=3)
        plt.close('all')

        # Graf 3 – Line: dubina svjetlosti
        fig3 = Figure(figsize=(3, 2), dpi=100)
        plot3 = fig3.add_subplot(111)
        plot3.plot(ids, dubina_svjetlosti, color='#f39c12')
        plot3.set_ylabel('Svjetlost (FC)')
        plot3.set_xlim([0, xlimit])
        # NumPy: prosječna svjetlost kao crvena isprekidana linija
        plot3.axhline(y=np.mean(dubina_svjetlosti), color='red', linestyle='--',
                      linewidth=0.8, label=f'Avg: {np.mean(dubina_svjetlosti):.0f}')
        plot3.legend(fontsize=6)
        plot3.set_title('Svjetlost kroz vrijeme', fontsize=9)
        canvas_2 = FigureCanvasTkAgg(fig3, self)
        canvas_2.draw()
        self.canvas_2 = canvas_2.get_tk_widget()
        self.canvas_2.grid(row=9, column=4, pady=3)
        plt.close('all')

        # Graf 4 – Line: temperatura
        fig4 = Figure(figsize=(3, 2), dpi=100)
        plot4 = fig4.add_subplot(111)
        plot4.plot(ids, temp, color='#e74c3c')
        plot4.set_ylabel('Temperatura (°C)')
        plot4.set_xlim([0, xlimit])
        # NumPy: prosječna temperatura kao plava isprekidana linija
        plot4.axhline(y=np.mean(temp), color='blue', linestyle='--',
                      linewidth=0.8, label=f'Avg: {np.mean(temp):.1f}°C')
        plot4.legend(fontsize=6)
        plot4.set_title('Temperatura kroz vrijeme', fontsize=9)
        canvas_3 = FigureCanvasTkAgg(fig4, self)
        canvas_3.draw()
        self.canvas_3 = canvas_3.get_tk_widget()
        self.canvas_3.grid(row=9, column=2, columnspan=2, pady=3)
        plt.close('all')

        # Graf 5 – Pie: pH raspodjela
        # Pandas: grupiraj pH vrijednosti i prebroji pojavljivanja
        ph_counts = df['pH'].value_counts().sort_index()
        ph_labels = [str(int(v)) for v in ph_counts.index]
        fig5 = Figure(figsize=(3, 2), dpi=100)
        plot5 = fig5.add_subplot(111)
        plot5.pie(ph_counts.values, labels=ph_labels, autopct='%1.0f%%',
                  textprops={'fontsize': 7})
        plot5.set_title('pH raspodjela', fontsize=9)
        canvas_4 = FigureCanvasTkAgg(fig5, self)
        canvas_4.draw()
        self.canvas_4 = canvas_4.get_tk_widget()
        self.canvas_4.grid(row=10, column=2, columnspan=2, pady=3)
        plt.close('all')

    def unplot(self):
        self.plot_button.config(command=self.plot, text='📊 Grafovi')
        for c in [self.canvas, self.canvas_1, self.canvas_2,
                  self.canvas_3, self.canvas_4]:
            try:
                c.grid_remove()
            except Exception:
                pass

    # ====================================================================
    # AKCIJA (ručno generiranje ispravnih vrijednosti)
    # ====================================================================
    def akcija(self):
        self.unplot()
        self.plot_button.grid_remove()
        self.akcija_btn.grid_remove()

        dubina_svjetlosti = randint(200, 1200)
        pH = round(random.uniform(6.50, 7.50), 2)
        salinitet = round(random.uniform(0.50, 2.50), 2)
        vlaznost = randint(60, 80)
        temperatura = randint(20, 25)
        now = datetime.datetime.now().strftime('%H:%M:%S')

        db_senzori.add_sensors(self.conn, dubina_svjetlosti, pH, salinitet,
                               vlaznost, temperatura, now)
        db_posude.update_pot_sync(self.conn, self.record[0],
                                  dubina_svjetlosti, pH, salinitet,
                                  vlaznost, temperatura, now)
        db_posude_records.add_sync_pot(self.conn, self.record[0], self.record[1],
                                       dubina_svjetlosti, pH, salinitet,
                                       vlaznost, temperatura, now)
        db_biljke.update_status_biljke(self.conn, self.record[1], 'OK')

        self.senzor_svjetlost_vrijednost.config(text=str(dubina_svjetlosti))
        self.senzor_ph_vrijednost.config(text=str(pH))
        self.senzor_salinitet_vrijednost.config(text=str(salinitet))
        self.senzor_vlaga_vrijednost.config(text=str(vlaznost))
        self.senzor_temp_vrijednost.config(text=str(temperatura))

        for lbl in [self.svjetlost_aktivnost, self.ph_aktivnost,
                    self.salinitet_aktivnost, self.vlaga_aktivnost,
                    self.temp_aktivnost]:
            lbl.config(text='✔ Ok', fg='#27ae60')

        self.plot_button.grid(row=8, column=2, pady=5)
        messagebox.showinfo("Aktivnost", "Aktivnost pokrenuta – vrijednosti normalizirane!")

    # ====================================================================
    # BAZA BILJAKA
    # ====================================================================
    def baza_biljaka(self):
        self.posude_lbl.grid_remove()
        self.lstbx_posuda_uredi.grid_remove()
        self.background_label.grid_remove()
        self.background_label_2.grid_remove()
        self.img_photo_lbl.grid_remove()
        self.dodaj_biljku_btn.grid_remove()
        self.izbrisi_posudu_btn.grid_remove()
        self.azuriraj_biljku_btn.grid_remove()
        self.azuriraj_posudu_btn.grid_remove()
        self.uredi_natrag_btn.grid_remove()
        self.dodaj_posudu_btn.grid_remove()
        self.isprazni_posudu_btn.grid_remove()
        moj_profil_btn.config(state='disabled')
        self.baza_biljaka_btn.config(text='◀ Vrati se', command=self.vrati_se)

        self.baza_biljaka_lstbx = tk.Listbox(self, borderwidth=3, height=14,
                                             width=20, selectbackground="#2176C1",
                                             font=('Arial', 10))
        self.baza_biljaka_lstbx.grid(row=1, rowspan=3, column=0, padx=5)

        self.my_plants_lbl = tk.Label(self, font=('Arial', 11, 'bold'),
                                      text='Baza biljaka', bg="#f0f0f0")
        self.my_plants_lbl.grid(row=0, column=0, sticky='W', pady=(5, 0))

        sve_biljke = db_biljke.select_all_plants(self.conn)
        self.baza_biljaka_lstbx.delete(0, tk.END)
        for _biljka in sve_biljke:
            for biljka in _biljka:
                self.baza_biljaka_lstbx.insert("end", biljka)

        # Labeli za prikaz aktivnosti biljke
        self.lokacija_lbl.grid_remove()
        self.svjetlost_aktivnost.grid_remove()
        self.ph_aktivnost.grid_remove()
        self.salinitet_aktivnost.grid_remove()
        self.vlaga_aktivnost.grid_remove()
        self.temp_aktivnost.grid_remove()

        def onSelect(event):
            selection = event.widget.curselection()
            if not selection:
                return
            index = int(selection[0])
            biljka = event.widget.get(index)

            slobodna = (biljka,) in self.free_plants or biljka in self.free_plants

            if slobodna:
                self.lokacija_lbl.grid(row=4, column=0)
                self.lokacija_lbl.config(text='Lokacija: SLOBODNA')
                for lbl in [self.svjetlost_aktivnost, self.ph_aktivnost,
                             self.salinitet_aktivnost, self.vlaga_aktivnost,
                             self.temp_aktivnost]:
                    lbl.config(text='Aktivnost: -', fg='gray')
                    lbl.grid_remove()
            else:
                data = db_posude_records.select_last_sensor(self.conn, biljka)
                if data is None:
                    data = db_posude.select_last_sensor(self.conn, biljka)
                if data is None:
                    return

                _, posuda, _, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, _ = data
                self.lokacija_lbl.grid(row=4, column=0)
                self.lokacija_lbl.config(text=f'Lokacija: {posuda}')

                self.svjetlost_aktivnost.grid(row=5, column=0, sticky='W')
                self.ph_aktivnost.grid(row=6, column=0, sticky='W')
                self.salinitet_aktivnost.grid(row=7, column=0, sticky='W')
                self.vlaga_aktivnost.grid(row=8, column=0, sticky='W')
                self.temp_aktivnost.grid(row=9, column=0, sticky='W')

                self.senzor_svjetlost_vrijednost.config(text=str(dubina_svjetlosti))
                self.senzor_ph_vrijednost.config(text=str(pH))
                self.senzor_salinitet_vrijednost.config(text=str(salinitet))
                self.senzor_vlaga_vrijednost.config(text=str(vlaznost))
                self.senzor_temp_vrijednost.config(text=str(temperatura))

                # Aktivnosti direktno ovdje (bez _prikazi_senzore jer imamo drukčiji tuple)
                if dubina_svjetlosti < 200:
                    self.svjetlost_aktivnost.config(text='⚠ Staviti na sunce', fg='#e67e22')
                elif dubina_svjetlosti > 1200:
                    self.svjetlost_aktivnost.config(text='⚠ Staviti u hlad', fg='#e67e22')
                else:
                    self.svjetlost_aktivnost.config(text='✔ Ok', fg='#27ae60')

                if pH < 6.50:
                    self.ph_aktivnost.config(text='⚠ Dodati sodu bikarbonu', fg='#e67e22')
                elif pH > 7.50:
                    self.ph_aktivnost.config(text='⚠ Dodati sumpornu kiselinu', fg='#e67e22')
                else:
                    self.ph_aktivnost.config(text='✔ Ok', fg='#27ae60')

                if salinitet < 0.50:
                    self.salinitet_aktivnost.config(text='⚠ Dodati nutricije', fg='#e67e22')
                elif salinitet > 2.50:
                    self.salinitet_aktivnost.config(text='⚠ Navodniti čistom vodom', fg='#e67e22')
                else:
                    self.salinitet_aktivnost.config(text='✔ Ok', fg='#27ae60')

                if vlaznost < 60:
                    self.vlaga_aktivnost.config(text='⚠ Zamagliti biljku', fg='#e67e22')
                elif vlaznost > 80:
                    self.vlaga_aktivnost.config(text='⚠ Staviti na toplije mjesto', fg='#e67e22')
                else:
                    self.vlaga_aktivnost.config(text='✔ Ok', fg='#27ae60')

                if temperatura < 20:
                    self.temp_aktivnost.config(text='⚠ Premjestiti u manju prostoriju', fg='#e67e22')
                elif temperatura > 25:
                    self.temp_aktivnost.config(text='⚠ Premjestiti u veću prostoriju', fg='#e67e22')
                else:
                    self.temp_aktivnost.config(text='✔ Ok', fg='#27ae60')

        self.baza_biljaka_lstbx.bind("<<ListboxSelect>>", onSelect)

    def vrati_se(self):
        self.baza_biljaka_btn.config(text='🌿 Baza biljaka', command=self.baza_biljaka)
        try:
            self.baza_biljaka_lstbx.grid_remove()
            self.my_plants_lbl.grid_remove()
        except Exception:
            pass

        self.posude_lbl.grid()
        self.lstbx_posuda_uredi.grid()
        self.background_label.grid()
        self.img_photo_lbl.grid()
        self.uredi_natrag_btn.grid()
        moj_profil_btn.config(state='normal')
        self.dodaj_posudu_btn.grid()
        self.lokacija_lbl.grid_remove()
        self.svjetlost_aktivnost.grid_remove()
        self.ph_aktivnost.grid_remove()
        self.salinitet_aktivnost.grid_remove()
        self.vlaga_aktivnost.grid_remove()
        self.temp_aktivnost.grid_remove()

    def natrag(self):
        self.posude_lbl.grid()
        self.lstbx_posuda.grid()
        self.dodaj_posudu_btn.grid()
        self.background_label.grid_remove()
        self._sakrij_senzore()

    def _sakrij_senzore(self):
        for w in [self.senzor_svjetlost, self.senzor_svjetlost_vrijednost,
                  self.senzor_ph, self.senzor_ph_vrijednost,
                  self.senzor_salinitet, self.senzor_salinitet_vrijednost,
                  self.senzor_vlaga, self.senzor_vlaga_vrijednost,
                  self.senzor_temp, self.senzor_temp_vrijednost,
                  self.akcija_btn, self.svjetlost_aktivnost,
                  self.ph_aktivnost, self.salinitet_aktivnost,
                  self.vlaga_aktivnost, self.temp_aktivnost]:
            w.grid_remove()

    # ====================================================================
    # AŽURIRAJ BILJKU (promjena naziva)
    # ====================================================================
    def azuriraj_biljku(self):
        self.isprazni_posudu_btn.grid_remove()
        self.dodaj_biljku_btn.grid_remove()
        self.azuriraj_biljku_btn.config(state='disabled')
        self.baza_biljaka_btn.grid_remove()
        self.azuriraj_posudu_btn.grid_remove()
        self.izbrisi_posudu_btn.grid_remove()
        self.dodaj_posudu_btn.grid_remove()
        self.uredi_natrag_btn.grid_remove()

        self.upisi_ime_biljke_lbl = tk.Label(self, text='Novo ime biljke:',
                                             font=('Arial', 10, 'bold'),
                                             bg="#f0f0f0")
        self.upisi_ime_biljke_lbl.grid(row=2, column=2, sticky='S')
        self.var_biljka_entry.set(value=self.record[1])
        self.dodaj_biljku_entry.grid(row=3, column=2)

        self.ok_azur_btn = tk.Button(self, text='✔ OK', command=self.ok_azur,
                                     bg="#4CAF50", fg="white",
                                     font=('Arial', 9, 'bold'), width=8)
        self.ok_azur_btn.grid(row=3, column=3, sticky='W')
        self.odustani_azur_btn = tk.Button(self, text='✖ Odustani',
                                           command=self.odustani_azur,
                                           font=('Arial', 9), width=10)
        self.odustani_azur_btn.grid(row=3, column=4, sticky='W')

    def odustani_azur(self):
        self.odustani_azur_btn.grid_remove()
        self.azuriraj_biljku_btn.config(state='normal')
        self.dodaj_posudu_btn.grid()
        self.isprazni_posudu_btn.grid()
        self.isprazni_posudu_btn.grid_remove()
        self.azuriraj_biljku_btn.grid_remove()
        self.background_label.grid_remove()
        self.uredi_natrag_btn.grid()
        self.ok_azur_btn.grid_remove()
        self.dodaj_biljku_entry.grid_remove()
        try:
            self.upisi_ime_biljke_lbl.grid_remove()
        except Exception:
            pass

    def ok_azur(self):
        novo_ime = self.dodaj_biljku_entry.get().strip()
        if (novo_ime,) in db_biljke.select_all_plants(self.conn):
            messagebox.showerror(title="Greška", message='Ime biljke već postoji!')
            return
        if not novo_ime:
            messagebox.showerror(title="Greška",
                                  message='Ime biljke ne smije biti prazno!')
            return
        if 'PRAZNA' in novo_ime:
            messagebox.showerror(title="Greška",
                                  message='Ime biljke ne smije sadržavati "PRAZNA"!')
            return

        db_biljke.update_name_plant(self.conn, novo_ime, self.record[1])
        db_posude.update_plant_name(self.conn, self.record[0], novo_ime)
        db_posude_records.update_plant_name(self.conn, self.record[0], novo_ime)

        self.azuriraj_biljku_btn.config(state='normal')
        self.baza_biljaka_btn.grid_remove()
        self.dodaj_posudu_btn.grid()
        self.ok_azur_btn.grid_remove()
        self.odustani_azur_btn.grid_remove()
        self.isprazni_posudu_btn.grid_remove()
        self.azuriraj_biljku_btn.grid_remove()
        self.background_label.grid_remove()
        self.uredi_natrag_btn.grid()
        self.dodaj_biljku_entry.grid_remove()
        try:
            self.upisi_ime_biljke_lbl.grid_remove()
        except Exception:
            pass
        messagebox.showinfo("Uspjeh", f"Biljka preimenovana u '{novo_ime}'!")

    # ====================================================================
    # ISPRAZNI POSUDU
    # ====================================================================
    def isprazni_posudu(self):
        if messagebox.askquestion(
                message='Biljka će se pospremiti u bazu slobodnih biljaka.'
                        '\nJeste li sigurni?') == 'yes':
            self.background_label.grid_remove()
            self.img_photo_lbl.grid_remove()
            self.isprazni_posudu_btn.grid_remove()
            self.dodaj_biljku_btn.grid_remove()
            self.azuriraj_biljku_btn.grid_remove()
            self.baza_biljaka_btn.grid_remove()
            self.azuriraj_posudu_btn.grid_remove()
            self.izbrisi_posudu_btn.grid_remove()

            db_biljke.update_status_biljke(self.conn, self.record[1], 'SLOBODNA')
            db_posude.delete_pot(self.conn, self.record[0])
            db_posude.add_pot(self.conn, self.record[0],
                              dubina_svjetlosti=None, pH=None,
                              salinitet=None, vlaznost=None, temperatura=None)

            try:
                self.free_plants.append(self.record[1])
            except Exception:
                self.free_plants.append((self.record[1],))

    # ====================================================================
    # DODAJ BILJKU U POSUDU (iz uredi prikaza)
    # ====================================================================
    def dodaj_biljku(self):
        self.azuriraj_biljku_btn.grid_remove()
        self.izbrisi_posudu_btn.grid_remove()
        self.azuriraj_posudu_btn.grid_remove()
        self.dodaj_posudu_btn.grid_remove()
        self.baza_biljaka_btn.grid_remove()
        self.dodaj_biljku_btn.config(state='disabled')
        self.lstbx_posuda_uredi.config(state='disabled')

        self.dodaj_biljku_lstbox_.grid(row=2, column=4)
        self.odustani_stavi_biljku_btn.grid(row=3, column=5, sticky='W')
        self.odustani_stavi_biljku_btn.config(command=self.odustani_biljka)

        self.dodaj_biljku_lstbox_.delete(0, tk.END)
        for plant in self.free_plants:
            self.dodaj_biljku_lstbox_.insert("end", plant)

        def _onselect_(event):
            self.biljka = ''
            selection = event.widget.curselection()
            if not selection:
                return
            index = int(selection[0])
            _biljka = event.widget.get(index)
            for char in _biljka:
                self.biljka += char

            self.stavi_biljku_btn.grid(row=3, column=4, sticky='N')
            self.stavi_biljku_btn.config(command=self.stavi_biljku,
                                          state='normal')
            self._ucitaj_sliku_biljke(self.biljka, self.background_label_2)
            self.background_label_2.grid(row=1, rowspan=3, column=1)

        self.dodaj_biljku_lstbox_.bind("<<ListboxSelect>>", _onselect_)

    def stavi_biljku(self):
        messagebox.showinfo(message=f'Biljka {self.biljka} stavljena u posudu {self.record[0]}')
        self.background_label_2.grid_remove()
        self.odustani_stavi_biljku_btn.grid_remove()
        self.stavi_biljku_btn.grid_remove()
        self.dodaj_biljku_lstbox_.grid_remove()
        self.dodaj_biljku_btn.grid_remove()
        self.img_photo_lbl.grid_remove()
        self.dodaj_posudu_btn.grid()
        self.lstbx_posuda_uredi.config(state='normal')
        self.dodaj_biljku_btn.config(state='normal')


        try:
            self.free_plants.remove((self.biljka,))
        except Exception:
            self.free_plants.remove(self.biljka)

        db_biljke.update_status_biljke(self.conn, self.biljka)
        db_posude.delete_pot(self.conn, self.record[0])
        db_posude.add_pot(self.conn, self.record[0], self.biljka)
        self.background_label.grid_remove()
        self._osvjezi_listboxeve()

    def odustani_biljka(self):
        self.background_label_2.grid_remove()
        self.odustani_stavi_biljku_btn.grid_remove()
        self.stavi_biljku_btn.grid_remove()
        self.dodaj_biljku_lstbox_.grid_remove()
        self.dodaj_biljku_btn.grid_remove()
        self.dodaj_posudu_btn.grid()
        self.lstbx_posuda_uredi.config(state='normal')
        self.dodaj_biljku_btn.config(state='normal')

    # ====================================================================
    # AŽURIRAJ POSUDU (promjena naziva)
    # ====================================================================
    def azuriraj_posudu(self):
        self.lstbx_posuda_uredi.config(state='disabled')
        self.dodaj_posudu_btn.grid_remove()
        self.izbrisi_posudu_btn.grid_remove()
        self.isprazni_posudu_btn.grid_remove()
        self.dodaj_biljku_btn.grid_remove()
        self.azuriraj_biljku_btn.grid_remove()
        self.baza_biljaka_btn.grid_remove()
        self.uredi_natrag_btn.grid_remove()

        self.upisi_ime_posude_lbl.config(text='Novo ime posude:')
        self.upisi_ime_posude_lbl.grid(row=5, column=0, sticky='W')
        self.var_posuda_entry.set(self.record[0])
        self.dodaj_posudu_entry.grid(row=6, column=0)
        self.dodaj_posudu_entry.config(state='normal')
        self.ok_btn.grid(row=6, column=1, sticky='W')
        self.ok_btn.config(command=self.ok_)
        self.odustani_btn_.grid(row=6, column=2)
        self.azuriraj_posudu_btn.grid_remove()

    def ok_(self):
        novo_ime = self.dodaj_posudu_entry.get().strip()
        if novo_ime in self.listaposuda:
            messagebox.showerror(title="Greška", message='Ime posude već postoji!')
            return
        if not novo_ime:
            messagebox.showerror(title="Greška",
                                  message='Ime posude ne smije biti prazno!')
            return

        db_posude.update_name_pot(self.conn, novo_ime, self.record[0])
        db_posude_records.update_name_pot(self.conn, novo_ime, self.record[0])

        # Ažuriraj lokalnu listu
        staro_ime = self.record[0]
        self.listaposuda.discard(staro_ime)
        self.listaposuda.add(novo_ime)

        self.dodaj_posudu_btn.grid()
        self.lstbx_posuda_uredi.config(state='normal')
        self.ok_btn.grid_remove()
        self.upisi_ime_posude_lbl.grid_remove()
        self.dodaj_posudu_entry.grid_remove()
        self.odustani_btn_.grid_remove()
        self.uredi_natrag_btn.grid()

        self._osvjezi_listboxeve()
        messagebox.showinfo("Uspjeh", f"Posuda preimenovana u '{novo_ime}'!")

    # ====================================================================
    # IZBRIŠI POSUDU
    # ====================================================================
    def izbrisi_posudu(self):
        if not self.record:
            return

        poruka = ('Jeste li sigurni? Biljka će se pospremiti u slobodne.'
                  if self.record[1] != 'PRAZNA posuda'
                  else 'Jeste li sigurni?')

        if messagebox.askquestion(message=poruka) != 'yes':
            return

        naziv = self.record[0]
        db_posude.delete_pot(self.conn, naziv)
        db_posude_records.delete_pot(self.conn, naziv)
        self.listaposuda.discard(naziv)

        if self.record[1] != 'PRAZNA posuda':
            db_biljke.update_status_biljke(self.conn, self.record[1], 'SLOBODNA')
            try:
                self.free_plants.append(self.record[1])
            except Exception:
                self.free_plants.append((self.record[1],))

        for w in [self.azuriraj_posudu_btn, self.izbrisi_posudu_btn,
                  self.background_label, self.img_photo_lbl,
                  self.isprazni_posudu_btn, self.dodaj_biljku_btn,
                  self.azuriraj_biljku_btn, self.baza_biljaka_btn]:
            w.grid_remove()

        self.dodaj_posudu_btn.grid()
        self._osvjezi_listboxeve()


    def _osvjezi_listboxeve(self):
        self.lstbx_posuda.delete(0, tk.END)
        self.lstbx_posuda_uredi.delete(0, tk.END)
        for posuda in self.listaposuda:
            pot = db_posude.get_pot(self.conn, posuda)
            if pot and pot[1] != 'PRAZNA posuda':
                self.lstbx_posuda.insert("end", posuda)
            self.lstbx_posuda_uredi.insert("end", posuda)

    def uredi_posude(self):
        self.unplot()
        self.plot_button.grid_remove()
        sync_btn.config(state='disabled')

        self.posude_lbl.grid(row=0, column=0)
        self.lstbx_posuda_uredi.grid(row=1, rowspan=3, column=0, padx=5)
        self.dodaj_posudu_btn.grid(row=5, column=0)
        self.uredi_natrag_btn.grid(row=6, column=0)

        self.crud_posuda_btn.grid_remove()
        self.lstbx_posuda.grid_remove()
        self.izbrisi_posudu_btn.grid_remove()
        self.background_label.grid_remove()
        self.img_photo_lbl.grid_remove()
        self.azuriraj_posudu_btn.grid_remove()
        self.dodaj_biljku_btn.grid_remove()
        self.azuriraj_biljku_btn.grid_remove()
        self.baza_biljaka_btn.grid_remove()
        self._sakrij_senzore()

        self.lstbx_posuda_uredi.delete(0, tk.END)
        for posuda in self.listaposuda:
            self.lstbx_posuda_uredi.insert("end", posuda)

        def on_select(event):
            selection = event.widget.curselection()
            sync_btn.config(state='disabled')
            if not selection:
                return

            index = int(selection[0])
            posuda = event.widget.get(index)
            self.record = db_posude.get_pot(self.conn, posuda)

            if not self.record:
                return

            self.background_label.grid(row=1, rowspan=3, column=1, padx=10)
            self.baza_biljaka_btn.grid(row=0, column=2)
            self.baza_biljaka_btn.config(state='normal', command=self.baza_biljaka)

            if self.record[1] != 'PRAZNA posuda':
                self._ucitaj_sliku_biljke(self.record[1], self.background_label)
                self.var_plant_img.set(self.record[1])
                self.img_photo_lbl.grid(row=0, column=1)
                self.azuriraj_posudu_btn.grid(row=4, column=1, sticky='E')
                self.isprazni_posudu_btn.grid(row=1, rowspan=2, column=2,
                                              sticky='S')
                self.isprazni_posudu_btn.config(command=self.isprazni_posudu)
                self.dodaj_biljku_btn.grid_remove()
                self.azuriraj_biljku_btn.grid(row=1, column=2, sticky='S')
                self.azuriraj_biljku_btn.config(state='normal',
                                                 command=self.azuriraj_biljku)
            else:
                self._ucitaj_praznu_sliku(self.background_label)
                self.var_plant_img.set('PRAZNA posuda')
                self.img_photo_lbl.grid(row=0, column=1)
                self.isprazni_posudu_btn.grid_remove()
                self.dodaj_biljku_btn.grid(row=1, rowspan=2, column=2,
                                           sticky='S')
                self.dodaj_biljku_btn.config(command=self.dodaj_biljku)
                self.azuriraj_biljku_btn.config(state='disabled')
                self.azuriraj_posudu_btn.grid(row=4, column=1, sticky='E')

            self.izbrisi_posudu_btn.config(command=self.izbrisi_posudu)
            self.izbrisi_posudu_btn.grid(row=4, column=0, columnspan=2)
            self.azuriraj_posudu_btn.config(command=self.azuriraj_posudu)

        self.lstbx_posuda_uredi.bind("<<ListboxSelect>>", on_select)

    def natrag_uredi(self):
        self.posude_lbl.grid()

        self.lstbx_posuda.delete(0, tk.END)
        for posuda in self.listaposuda:
            pot = db_posude.get_pot(self.conn, posuda)
            if pot and pot[1] != 'PRAZNA posuda':
                self.lstbx_posuda.insert("end", posuda)

        self.lstbx_posuda.grid(row=1, rowspan=3, column=0)
        self.crud_posuda_btn.grid(row=5, column=0)

        self.lstbx_posuda_uredi.grid_remove()
        self.baza_biljaka_btn.grid_remove()
        self.background_label.grid_remove()
        self.baza_ime_posude.grid_remove()
        self.dodaj_biljku_btn.grid_remove()
        self.dodaj_posudu_btn.grid_remove()
        self.izbrisi_posudu_btn.grid_remove()
        self.azuriraj_biljku_btn.grid_remove()
        self.azuriraj_posudu_btn.grid_remove()
        self.isprazni_posudu_btn.grid_remove()
        self.img_photo_lbl.grid_remove()
        self.uredi_natrag_btn.grid_remove()
        sync_btn.config(state='normal')

    # ====================================================================
    # DODAJ POSUDU (nova posuda)
    # ====================================================================
    def dodaj_posudu(self):
        self.biljka = ''
        self.lstbx_posuda_uredi.config(state='disabled')
        self.dodaj_posudu_btn.grid_remove()
        self.izbrisi_posudu_btn.grid_remove()
        self.background_label.grid_remove()
        self.img_photo_lbl.grid_remove()
        self.azuriraj_posudu_btn.grid_remove()
        self.uredi_natrag_btn.grid_remove()
        self.isprazni_posudu_btn.grid_remove()
        self.dodaj_biljku_btn.grid_remove()
        self.azuriraj_biljku_btn.grid_remove()
        self.baza_biljaka_btn.grid_remove()

        self.ok_btn.config(command=self.ok)
        self.upisi_ime_posude_lbl.config(text='Ime nove posude:')
        self.upisi_ime_posude_lbl.grid(row=5, column=0)
        self.var_posuda_entry.set(value=f'PyPosuda{len(self.listaposuda) + 1}')
        self.ok_btn.grid(row=6, column=1)
        self.dodaj_posudu_entry.grid(row=6, column=0)
        self.dodaj_posudu_entry.config(state='normal')
        self.odustani_btn_.grid(row=6, column=3, sticky='W')

        def _onselect(event):
            self.biljka = ''
            selection = event.widget.curselection()
            if not selection:
                return
            index = int(selection[0])
            _biljka = event.widget.get(index)
            for char in _biljka:
                self.biljka += char

            self.stavi_btn.grid(row=6, column=1)
            self.stavi_btn.config(command=self.stavi, state='normal')
            self.ostavi_prazno_btn.grid(row=6, column=2, sticky='W')

            self._ucitaj_sliku_biljke(self.biljka, self.background_label_2)
            self.background_label_2.grid(row=1, rowspan=3, column=1)

        self.dodaj_biljku_lstbox.bind("<<ListboxSelect>>", _onselect)

    def ok(self):
        ime = self.dodaj_posudu_entry.get().strip()
        if not ime:
            messagebox.showerror(title="Greška",
                                  message='Ime posude ne smije ostati prazno!')
            return
        if db_posude.get_pot(self.conn, ime) is not None:
            messagebox.showerror(title="Greška", message='Ime posude je zauzeto!')
            return

        self.ok_btn.grid_remove()
        self.dodaj_posudu_entry.config(state='disabled')
        self.upisi_ime_posude_lbl.grid_remove()
        self.stavi_biljku_lbl = tk.Label(self, text='Odaberi slobodnu biljku:',
                                          font=('Arial', 10), bg="#f0f0f0")
        self.stavi_biljku_lbl.grid(row=4, column=1)
        self.dodaj_biljku_lstbox.grid(row=5, column=1)
        self.odustani_btn_.grid_remove()
        self.odustani_btn.grid(row=6, column=3)
        self.ostavi_prazno_btn.grid(row=6, column=2, sticky='W')
        self.ostavi_prazno_btn.config(command=self.ostavi_prazno, state='normal')

        self.dodaj_biljku_lstbox.delete(0, tk.END)
        for plant in self.free_plants:
            self.dodaj_biljku_lstbox.insert("end", plant)

    def stavi(self):
        if not self.biljka:
            return

        ime = self.dodaj_posudu_entry.get().strip()
        if db_posude.add_pot(self.conn, ime, self.biljka):
            self._zatvori_dodaj_posudu_ui()
            db_biljke.update_status_biljke(self.conn, self.biljka)
            self.listaposuda.add(ime)
            try:
                self.free_plants.remove((self.biljka,))
            except Exception:
                try:
                    self.free_plants.remove(self.biljka)
                except Exception:
                    pass
            self._osvjezi_listboxeve()

    def ostavi_prazno(self):
        ime = self.dodaj_posudu_entry.get().strip()
        db_posude.add_pot(self.conn, ime, biljka='PRAZNA posuda',
                          dubina_svjetlosti=None, pH=None,
                          salinitet=None, vlaznost=None, temperatura=None)
        self._zatvori_dodaj_posudu_ui()
        self.listaposuda.add(ime)
        self._osvjezi_listboxeve()

    def _zatvori_dodaj_posudu_ui(self):
        for w in [self.dodaj_biljku_lstbox, self.dodaj_posudu_entry,
                  self.stavi_btn, self.ostavi_prazno_btn,
                  self.odustani_btn, self.background_label_2]:
            w.grid_remove()
        try:
            self.stavi_biljku_lbl.grid_remove()
        except Exception:
            pass
        self.dodaj_posudu_btn.grid()
        self.lstbx_posuda_uredi.config(state='normal')
        self.uredi_natrag_btn.grid()

    def odustani(self):
        for w in [self.dodaj_biljku_lstbox, self.stavi_btn,
                  self.ostavi_prazno_btn, self.odustani_btn,
                  self.background_label_2]:
            w.grid_remove()
        try:
            self.stavi_biljku_lbl.grid_remove()
        except Exception:
            pass
        self.dodaj_posudu_btn.grid()
        self.lstbx_posuda_uredi.config(state='normal')
        self.uredi_natrag_btn.grid()
        self.ok_btn.grid_remove()
        self.upisi_ime_posude_lbl.grid_remove()
        self.dodaj_posudu_entry.grid_remove()

    def odustani_(self):
        self.dodaj_posudu_btn.grid()
        self.lstbx_posuda_uredi.config(state='normal')
        self.ok_btn.grid_remove()
        self.upisi_ime_posude_lbl.grid_remove()
        self.dodaj_posudu_entry.grid_remove()
        self.odustani_btn_.grid_remove()
        self.uredi_natrag_btn.grid()