import gui
import db, db_biljke, db_posude, db_senzori, db_posude_records
import os

def main():
    # Osiguraj da data folder postoji
    if not os.path.exists("./data"):
        os.makedirs("./data")
        
    db_path = "./data/PyFloraPosuda.db"
    
    # Inicijalizacija svih tablica koristeći istu bazu
    conn = db.get_connection(db_path)
    db_biljke.get_connection(db_path)
    db_posude.get_connection(db_path)
    db_posude_records.get_connection(db_path)
    db_senzori.get_connection(db_path)

    # Pokretanje aplikacije
    app = gui.App(conn)
    app.mainloop()

if __name__ == "__main__":
    main()