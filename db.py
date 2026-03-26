import sqlite3

create_table_query = """CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
    
);"""

select_query = """SELECT username FROM Users
"""

select_user_query = """SELECT name, surname, username, password FROM Users
   WHERE username = ?"""

insert_user_query = """INSERT INTO Users (name, surname, username, password)
  VALUES (?, ?, ?, ?)"""


delete_user_query = """DELETE FROM Users WHERE username = ?"""

select_all_users_query = """SELECT username FROM Users
"""

def get_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)

        cursor = conn.cursor()

        # ako tablica Users ne postoji, kreiraj ju
        cursor.execute(create_table_query)
        conn.commit()

        # ako korisnik "admin" ne postoji u bazi, dodaj ga
        if select_all_users(conn) == []:
            add_user(conn, "Sandi", "Camilov", "admin", "admin")
        # add_user(conn, "Pero","Peric", 'pero', 'peric')
        # add_user(conn, "Mare","Maric", 'mare', 'maric')
        cursor.close()

        return conn
    except sqlite3.Error as err:
        print(f"ERROR1: {err}")

def get_user(conn, username):
    try:
        cursor = conn.cursor()
        
        cursor.execute(select_user_query, (username,))

        record = cursor.fetchone()
        

        if record != None:
            return (record[0], record[1], record[2], record[3])
        else:
            return None
    except sqlite3.Error as err:
        print(f"ERROR2: {err}")
    finally:
        cursor.close()

def add_user(conn, ime, prezime, username, password):
    try:
        cursor = conn.cursor()

        # ako username vec postoji u bazi, ne dodajemo ponovno
        if get_user(conn, username) != None:
            return False

        cursor.execute(insert_user_query, (ime, prezime, username, password))

        conn.commit()

        return True
    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()

def delete_user(conn, username):
    try:
        cursor = conn.cursor()

        cursor.execute(delete_user_query, (username,))
        conn.commit()
        print('commited!')
    except sqlite3.Error as err:
        print(f"ERROR3: {err}")
        return False
    finally:
        cursor.close()

def select_username(conn):
    try:
        cursor = conn.cursor()
        
        cursor.execute(select_query)

        record = cursor.fetchone()
        

        if record != None:
            return record
        else:
            return None
    except sqlite3.Error as err:
        print(f"ERROR2: {err}")
    finally:
        cursor.close()


def select_all_users(conn):
    try:
        cursor = conn.cursor()
        
        cursor.execute(select_all_users_query)

        record = cursor.fetchall()
        

        if record != None:
            return record
        else:
            return None
    except sqlite3.Error as err:
        print(f"ERROR2: {err}")
    finally:
        cursor.close()