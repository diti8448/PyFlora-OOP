import sqlite3


create_table_query = """CREATE TABLE IF NOT EXISTS PyPots(
    id INTEGER PRIMARY KEY,
    naziv TEXT UNIQUE NOT NULL,
    biljka TEXT NOT NULL,
    dubina_svjetlosti INTEGER,
    pH FLOAT,
    salinitet FLOAT,
    vlaznost INTEGER,
    temperatura INTEGER,
    vrijeme TEXT
              
);"""

select_query = """SELECT naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura FROM PyPots
   WHERE naziv = ?"""

insert_query = """INSERT INTO PyPots (naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura)
  VALUES (?, ?, ?, ?, ?, ?, ?)"""


update_sync_query = """UPDATE PyPots SET dubina_svjetlosti = ? , pH = ?, salinitet = ?, vlaznost = ?, temperatura = ?, vrijeme = ?
 WHERE naziv = ?"""



update_name_pot_query = """UPDATE PyPots SET naziv = ?
 WHERE naziv = ?"""

delete_query = """DELETE FROM PyPots WHERE naziv = ?"""

select_all_pots_query = """SELECT naziv FROM PyPots"""


update_plant_name_query = """UPDATE PyPots SET biljka = ?
 WHERE naziv = ?"""

select_not_empty_pots_query = """SELECT naziv FROM PyPots WHERE NOT biljka = ?
"""
select_last_sensor_query = """SELECT * FROM PyPots WHERE biljka = ?
ORDER BY vrijeme DESC
LIMIT 1
"""
def get_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)

        cursor = conn.cursor()

        # ako tablica PyPlot ne postoji, kreiraj ju
        cursor.execute(create_table_query)
        conn.commit()
        # ako posuda ne postoji u bazi, dodaj ju
        if select_all_pots(conn) == []:
            add_pot(conn, "PyPosuda1", "Azaleja")

        cursor.close()

        return conn
    except sqlite3.Error as err:
        print(f"ERROR1: {err}")
    
def get_pot(conn, naziv):
    try:
        cursor = conn.cursor()

        cursor.execute(select_query, (naziv,))

        record = cursor.fetchone()
        

        if record != None:
            naziv = record[0]
            biljka = record[1]
            dubina_svjetlosti = record[2]
            pH = record[3]
            salinitet = record[4]
            vlaznost = record[5]
            temperatura = record[6]       
            return naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura
        else:
            return None
    except sqlite3.Error as err:
        print(f"ERROR2: {err}")
    finally:
        cursor.close()


def add_pot(conn, naziv, biljka='PRAZNA posuda', dubina_svjetlosti=200, pH=7, salinitet=1, vlaznost=60, temperatura=25):
    try:
        cursor = conn.cursor()

        # ako pyplant vec postoji u bazi, ne dodajemo ponovno
        if get_pot(conn, naziv) != None:
            return False

        cursor.execute(insert_query, (naziv, biljka, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura))

        conn.commit()

        return True
    
    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()

def update_pot_sync(conn, naziv, dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme):
    try:
        cursor = conn.cursor()

        cursor.execute(update_sync_query, (dubina_svjetlosti, pH, salinitet, vlaznost, temperatura, vrijeme, naziv))
        conn.commit()
    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
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

def select_all_pots(conn):
    try:
        cursor = conn.cursor()

        cursor.execute(select_all_pots_query)

        record = cursor.fetchall()
        if record != None:
      
            return record
        else:
            return record
    except sqlite3.Error as err:
        print(f"ERROR2: {err}")
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


def select_not_empty_pots(conn, biljka='PRAZNA posuda'):
    try:
        cursor = conn.cursor()

        cursor.execute(select_not_empty_pots_query, (biljka,))

        record = cursor.fetchall()
        
        if record != None:
      
            return record
        else:
            return None
    except sqlite3.Error as err:
        print(f"ERROR2: {err}")
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