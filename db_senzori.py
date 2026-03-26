import sqlite3


create_table_query = """CREATE TABLE IF NOT EXISTS Sensors(
    id INTEGER PRIMARY KEY,
    dubina_svjetlosti INTEGER,
    pH FLOAT,
    salinitet FLOAT,
    vlaznost INTEGER,
    temperatura INTEGER,
    vrijeme TEXT  
        
);"""

insert_query = """INSERT INTO Sensors (dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme)
  VALUES (?, ?, ?, ?, ?, ?)"""



def get_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)

        cursor = conn.cursor()

        # ako tablica Sensors ne postoji, kreiraj ju
        cursor.execute(create_table_query)
        conn.commit()

        cursor.close()

        return conn
    except sqlite3.Error as err:
        print(f"ERROR1: {err}")

def add_sensors(conn, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme):

    try:
        cursor = conn.cursor()
        cursor.execute(insert_query, (dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme))

        conn.commit()

        return True
    
    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()