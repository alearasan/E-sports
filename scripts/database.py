import sqlite3
import os

# Ruta a la base de datos
DB_PATH = 'database/fifa_esports.db'

# Crear una conexión con la base de datos
def get_connection():
    return sqlite3.connect(DB_PATH)

# Crear las tablas si no existen
def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Crear tabla Matches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league TEXT,
            local_player TEXT,
            visitor_player TEXT,
            local_team TEXT,
            visitor_team TEXT,
            local_score INTEGER,
            visitor_score INTEGER,
            match_date TEXT
        )
    ''')
    
    # Crear tabla Events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            event_type TEXT,
            minute INTEGER,
            team TEXT,
            FOREIGN KEY(match_id) REFERENCES Matches(id)
        )
    ''')
    
    # Crear tabla Statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            stat_type TEXT,
            local_value INTEGER,
            visitor_value INTEGER,
            FOREIGN KEY(match_id) REFERENCES Matches(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Base de datos configurada con éxito.")

# Insertar un partido en la tabla Matches
def insert_match(league, local_player, visitor_player, local_team, visitor_team, local_score, visitor_score, match_date):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si el partido ya existe
    cursor.execute('''
        SELECT id
        FROM Matches
        WHERE league = ? AND local_team = ? AND visitor_team = ? AND match_date = ?
    ''', (league, local_team, visitor_team, match_date))
    
    match = cursor.fetchone()
    if match:  # Si existe, devolver el ID del partido existente
        print(f"Partido duplicado detectado: {local_team} vs {visitor_team} en {match_date}.")
        conn.close()
        return match[0]
    else:  # Si no existe, insertar
        cursor.execute('''
            INSERT INTO Matches (league, local_player, visitor_player, local_team, visitor_team, local_score, visitor_score, match_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (league, local_player, visitor_player, local_team, visitor_team, local_score, visitor_score, match_date))
        match_id = cursor.lastrowid  # Obtener el ID del partido recién insertado
        conn.commit()
        print(f"Partido insertado: {local_team} vs {visitor_team} en {match_date}.")
        conn.close()
        return match_id


# Insertar un evento en la tabla Events
def insert_event(match_id, event_type, minute, team):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si el evento ya existe
    cursor.execute('''
        SELECT COUNT(*)
        FROM Events
        WHERE match_id = ? AND event_type = ? AND minute = ? AND team = ?
    ''', (match_id, event_type, minute, team))
    
    if cursor.fetchone()[0] == 0:  # Si no existe, insertar
        cursor.execute('''
            INSERT INTO Events (match_id, event_type, minute, team)
            VALUES (?, ?, ?, ?)
        ''', (match_id, event_type, minute, team))
        conn.commit()
        print(f"Evento insertado: {event_type} en el minuto {minute} para el equipo {team}.")
    else:
        print(f"Evento duplicado detectado: {event_type} en el minuto {minute} para el equipo {team}.")
    
    conn.close()


# Insertar una estadística en la tabla Statistics
def insert_statistic(match_id, stat_type, local_value, visitor_value):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si la estadística ya existe
    cursor.execute('''
        SELECT COUNT(*)
        FROM Statistics
        WHERE match_id = ? AND stat_type = ?
    ''', (match_id, stat_type))
    
    if cursor.fetchone()[0] == 0:  # Si no existe, insertar
        cursor.execute('''
            INSERT INTO Statistics (match_id, stat_type, local_value, visitor_value)
            VALUES (?, ?, ?, ?)
        ''', (match_id, stat_type, local_value, visitor_value))
        conn.commit()
        print(f"Estadística insertada: {stat_type}, Local = {local_value}, Visitante = {visitor_value}.")
    else:
        print(f"Estadística duplicada detectada: {stat_type} ya existe para el partido {match_id}.")
    
    conn.close()


# Consultar partidos desde la tabla Matches
def query_matches():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Matches')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Consultar eventos de un partido específico
def query_events(match_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Events WHERE match_id = ?', (match_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Consultar estadísticas de un partido específico
def query_statistics(match_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Statistics WHERE match_id = ?', (match_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
