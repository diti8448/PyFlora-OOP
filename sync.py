from random import randint
import sqlite3
import db_senzori, db_posude, db_posude_records
import random
import datetime
import requests

# Koordinate Algebra kampusa — Črnomerec, Zagreb
METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=45.8150"
    "&longitude=15.9819"
    "&current_weather=true"
)
 
 
def get_temperatura_meteo():
    """
    Dohvaća trenutnu temperaturu zraka s Open-Meteo API-ja
    za lokaciju Algebra kampusa (Črnomerec, Zagreb).
    Ako API nije dostupan (nema interneta, timeout, greška),
    vraća random vrijednost kao fallback.
    """
    try:
        response = requests.get(METEO_URL, timeout=5)
        response.raise_for_status()
        temperatura = response.json()["current_weather"]["temperature"]
        print(f"[Meteo API] Temperatura sa stanice: {temperatura}°C")
        return int(temperatura)
    except requests.exceptions.ConnectionError:
        print("[Meteo API] Nema internetske veze — koristi se random fallback.")
    except requests.exceptions.Timeout:
        print("[Meteo API] Timeout — koristi se random fallback.")
    except (KeyError, ValueError) as e:
        print(f"[Meteo API] Neočekivani format odgovora ({e}) — koristi se random fallback.")
    except Exception as e:
        print(f"[Meteo API] Greška ({e}) — koristi se random fallback.")
 
    return randint(10, 40)

def syncronize():
    conn = sqlite3.connect("./data/PyFloraPosuda.db")

    record = db_posude.select_not_empty_pots(conn)
    if record is None or len(record) == 0:
        print("Nema nepraznih posuda za sinkronizaciju.")
        conn.close()
        return

    # Izvuci nazive posuda iz liste tupleva
    pot = list({posuda for _posuda in record for posuda in _posuda})

    print(f'Neprazne posude ({len(pot)}): {pot}')
    now = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'Sinkronizacija u: {now}')

    # Temperatura se dohvaća JEDNOM za sve posude (ista soba/lokacija)
    temperatura = get_temperatura_meteo()

    for naziv_posude in pot:
        dubina_svjetlosti = randint(10, 1500)
        pH                = round(random.uniform(5, 8), 2)
        salinitet         = round(random.uniform(0, 3), 2)
        vlaznost          = randint(20, 90)
    

        _biljka = db_posude.get_pot(conn, naziv_posude)
        if _biljka is None:
            continue
        biljka = _biljka[1]
        print(f'  → {naziv_posude} / biljka: {biljka}')

        db_senzori.add_sensors(conn, dubina_svjetlosti, pH, salinitet,
                               vlaznost, temperatura, now)
        db_posude.update_pot_sync(conn, naziv_posude, dubina_svjetlosti,
                                  pH, salinitet, vlaznost, temperatura, now)
        db_posude_records.add_sync_pot(conn, naziv_posude, biljka,
                                       dubina_svjetlosti, pH, salinitet,
                                       vlaznost, temperatura, now)

    conn.close()
    print("Sinkronizacija završena.")
