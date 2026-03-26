import sqlite3
import os

# Dinamičko određivanje putanje mape sa slikama
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Putanja do mape PyPlants
IMAGE_DIR = os.path.join(BASE_DIR, "PyPlants")
# Privremena mapa za raspakiranje slika iz baze
TEMP_DIR = os.path.join(BASE_DIR, "temp_plants")

create_table_query = """CREATE TABLE IF NOT EXISTS PyPlants(
    id INTEGER PRIMARY KEY,
    naziv TEXT UNIQUE NOT NULL,
    fotografija BLOB NOT NULL,
    status TEXT NOT NULL
        
);"""

select_plant_query = """SELECT naziv, fotografija, status FROM PyPlants
   WHERE naziv = ?"""

insert_plant_query = """INSERT INTO PyPlants (naziv, fotografija, status)
  VALUES (?, ?, ?)"""

select_free_plants_query = """SELECT naziv FROM PyPlants
   WHERE status = ?"""

update_status_query = """UPDATE PyPlants SET status = ?
   WHERE naziv = ?"""

update_plant_query = """UPDATE PyPlants SET naziv = ?"""

delete_plant_query = """DELETE FROM PyPlants WHERE naziv = ?"""

update_name_plant_query = """UPDATE PyPlants SET naziv = ? 
WHERE naziv = ?"""

select_all_plants_query = """SELECT naziv FROM PyPlants"""


def get_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # ako tablica PyPlants ne postoji, kreiraj ju
        cursor.execute(create_table_query)
        conn.commit()

        # Inicijalne biljke — dodaju se samo ako već ne postoje u bazi
        # (add_plant interno provjerava duplikate)
        inicijalne_biljke = [
            ("Azaleja",       "Azaleja.jpg",           "OK"),
            ("Banana",        "Banana.jpg",             "SLOBODNA"),
            ("Sweet Potato Vine", "Sweet Potato Vine.jpg", "SLOBODNA"),
            ("Bugenvilija",   "Bugenvilija.jpg",        "SLOBODNA"),
            ("Cvijet truba",  "Cvijet truba.jpg",       "SLOBODNA"),
            ("Eucalyptus",    "Eucalyptus.jpg",         "SLOBODNA"),
            ("Japanska palma","Japanska palma.jpg",     "SLOBODNA"),
            ("Lantana",       "Lantana.jpg",            "SLOBODNA"),
            ("Limun",         "Limun.jpg",              "SLOBODNA"),
            ("Oleander",      "Oleander.jpg",           "SLOBODNA"),
            ("Kaktus",        "Kaktus.jpg",             "SLOBODNA"),
            ("Orhideja",      "Orhideja.jpg",           "SLOBODNA"),
        ]

        for naziv, slika, status in inicijalne_biljke:
            putanja_slike = os.path.join(IMAGE_DIR, slika)
            if os.path.exists(putanja_slike):
                add_plant(conn, naziv, putanja_slike, status)
            else:
                print(f"[UPOZORENJE] Slika nije pronađena: {putanja_slike}")

        cursor.close()
        return conn

    except sqlite3.Error as err:
        print(f"ERROR1: {err}")


def writeTofile(data, filename):
    """Sprema binarne podatke (BLOB) na disk."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as file:
        file.write(data)
    print(f"Slika spremljena na disk: {filename}")


def get_plant(conn, naziv):
    try:
        cursor = conn.cursor()
        cursor.execute(select_plant_query, (naziv,))
        record = cursor.fetchone()

        if record is not None:
            naziv_biljke = record[0]
            fotografija   = record[1]
            status        = record[2]

            # Raspakiranje BLOB slike u temp mapu — cross-platform putanja
            photo_filename = naziv_biljke + ".jpg"
            photoPath = os.path.join(TEMP_DIR, photo_filename)
            writeTofile(fotografija, photoPath)
            print(f"photopath = {photoPath}")

            return (naziv_biljke, photoPath, status)
        else:
            return None

    except sqlite3.Error as err:
        print(f"ERROR: {err}")
    finally:
        cursor.close()


def convertToBinaryData(filename):
    """Čita sliku s diska i vraća je kao binarni blob."""
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def add_plant(conn, naziv, fotografija, status):
    try:
        cursor = conn.cursor()

        # ako biljka već postoji u bazi, ne dodajemo ponovno
        if get_plant(conn, naziv) is not None:
            return False

        photo = convertToBinaryData(fotografija)
        cursor.execute(insert_plant_query, (naziv, photo, status))
        conn.commit()
        return True

    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()


def select_free_plants(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(select_free_plants_query, ('SLOBODNA',))
        record = cursor.fetchall()
        if record is None:
            return []
        return record

    except sqlite3.Error as err:
        print(f"ERROR7: {err}")
        return []
    finally:
        cursor.close()


def update_status_biljke(conn, naziv, status='OK'):
    try:
        cursor = conn.cursor()
        cursor.execute(update_status_query, (status, naziv))
        conn.commit()

    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()


def update_name_plant(conn, naziv, _naziv):
    try:
        cursor = conn.cursor()
        cursor.execute(update_name_plant_query, (naziv, _naziv))
        conn.commit()

    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()


def select_all_plants(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(select_all_plants_query)
        record = cursor.fetchall()
        if record is None:
            return []
        return record

    except sqlite3.Error as err:
        print(f"ERROR8: {err}")
        return []
    finally:
        cursor.close()
