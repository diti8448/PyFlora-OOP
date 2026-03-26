# PyFloraPosuda - Pametni sustav za upravljanje biljkama

PyFloraPosuda je desktop aplikacija koja simulira sustav pametnih posuda za biljke. Projekt integrira rad s lokalnom bazom podataka, obradu slika i dohvat vanjskih meteoroloških podataka u stvarnom vremenu.

## Glavne značajke:
- **Sustav Sinkronizacije**: Dohvaćanje realnih vremenskih podataka (temperatura) putem **Open-Meteo API-ja** za lokaciju Zagreb (Algebra).
- **Upravljanje Podacima**: SQLite baza s tablicama za korisnike, biljke, posude i povijest senzorskih zapisa (Records).
- **Vizualizacija**: Prikaz statistike i stanja biljaka pomoću `matplotlib` i `pandas` grafova unutar aplikacije.
- **Grafičko sučelje**: Potpuna Tkinter GUI implementacija za login, uredi mod i praćenje senzora.

## Tehnički detalji:
- **Jezik**: Python 3.x
- **Baza**: SQLite3
- **Arhitektura**: Modularni pristup (odvojeni moduli za bazu, sinkronizaciju i GUI).

## Kako pokrenuti?
1. Instalirajte potrebne biblioteke: `pip install -r requirements.txt`
2. Pokrenite glavnu skriptu: `python main.py`