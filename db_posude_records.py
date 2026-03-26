import sqlite3


create_table_query = """CREATE TABLE IF NOT EXISTS PyRecords(
    id INTEGER PRIMARY KEY,
    naziv TEXT NOT NULL,
    biljka TEXT NOT NULL,
    dubina_svjetlosti INTEGER,
    pH FLOAT,
    salinitet FLOAT,
    vlaznost INTEGER,
    temperatura INTEGER,
    vrijeme TEXT
              
);"""

select_query = """SELECT naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme FROM PyRecords
   WHERE naziv = ?"""

insert_query = """INSERT INTO PyRecords (naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura)
  VALUES (?, ?, ?, ?, ?, ?, ?)"""

insert_sync_query = """INSERT INTO PyRecords (naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""




update_name_pot_query = """UPDATE PyRecords SET naziv = ?
 WHERE naziv = ?"""

delete_query = """DELETE FROM PyRecords WHERE naziv = ?"""

select_all_pots_query = """SELECT naziv FROM PyRecords"""


update_plant_name_query = """UPDATE PyRecords SET biljka = ?
 WHERE naziv = ?"""

select_not_empty_pots_query = """SELECT naziv FROM PyRecords WHERE NOT biljka = ?
"""
select_last_sensor_query = """SELECT * FROM PyRecords WHERE biljka = ?
ORDER BY id DESC
LIMIT 1
"""
select_all_query = """SELECT * FROM PyRecords WHERE naziv = ?"""

def get_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)

        cursor = conn.cursor()

        # ako tablica PyRecords ne postoji, kreiraj ju
        cursor.execute(create_table_query)
        conn.commit()
        # Inicijalni zapis se ne dodaje ovdje —
        # db_posude.get_connection() to već radi za PyPots tablicu

        cursor.close()

        return conn
    except sqlite3.Error as err:
        print(f"ERROR1: {err}")
    

def add_sync_pot(conn, naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme):
    try:
        cursor = conn.cursor()

        cursor.execute(insert_sync_query, (naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme))

        conn.commit()

        return True
    
    except sqlite3.Error as err:
        print(f'ERROR5: {err}')
        return False
    finally:
        cursor.close()




def delete_pot(conn, naziv):

    try:
        cursor = conn.cursor()

        cursor.execute(delete_query, (naziv,))
        conn.commit()
    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()



def update_name_pot(conn, naziv, _naziv):
    try:
        cursor = conn.cursor()

        cursor.execute(update_name_pot_query, (naziv, _naziv))
        conn.commit()
    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()

def update_plant_name(conn, posuda, biljka):
    try:
        cursor = conn.cursor()

        cursor.execute(update_plant_name_query, (biljka, posuda))
        conn.commit()
    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()



def select_last_sensor(conn, biljka):
    try:
        cursor = conn.cursor()

        cursor.execute(select_last_sensor_query, (biljka,))

        record = cursor.fetchone()
        
        if record != None:
      
            return record
        else:
            return None
    except sqlite3.Error as err:
        print(f"ERROR2: {err}")
    finally:
        cursor.close()

def select_all(conn, posuda):
    try:
        cursor = conn.cursor()

        cursor.execute(select_all_query, (posuda,))

        record = cursor.fetchmany(50)
        
        if record != None:
            
            return record
        else:
            return []
    except sqlite3.Error as err:
        print(f"ERROR2: {err}")
    finally:
        cursor.close()