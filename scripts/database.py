import sqlite3
from sqlite3 import Error

DB_PATH = 'database/fifa_esports.db'

def get_connection():
    """Establece una conexión con la base de datos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def insert_match(league, local_team, visitor_team, local_score, visitor_score, match_date):
    """Inserta un partido en la tabla Matches."""
    try:
        conn = get_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Matches (league, local_team, visitor_team, local_score, visitor_score, match_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (league, local_team, visitor_team, local_score, visitor_score, match_date))
            conn.commit()
            print(f"Partido insertado: {league} - {local_team} vs {visitor_team}")
        else:
            print("No se pudo establecer conexión con la base de datos.")
    except Error as e:
        print(f"Error al insertar el partido: {e}")
    finally:
        if conn:
            conn.close()

def insert_event(match_id, event_type, minute, team):
    """Inserta un evento en la tabla Events."""
    try:
        conn = get_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Events (match_id, event_type, minute, team)
                VALUES (?, ?, ?, ?)
            ''', (match_id, event_type, minute, team))
            conn.commit()
            print(f"Evento insertado: {event_type} - Minuto {minute} - Equipo: {team}")
        else:
            print("No se pudo establecer conexión con la base de datos.")
    except Error as e:
        print(f"Error al insertar el evento: {e}")
    finally:
        if conn:
            conn.close()

def query_matches():
    """Consulta todos los partidos en la tabla Matches."""
    try:
        conn = get_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Matches')
            rows = cursor.fetchall()
            return rows
        else:
            print("No se pudo establecer conexión con la base de datos.")
            return []
    except Error as e:
        print(f"Error al consultar los partidos: {e}")
        return []
    finally:
        if conn:
            conn.close()
