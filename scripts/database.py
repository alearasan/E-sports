import sqlite3

# Ruta a la base de datos
DB_PATH = 'database/fifa_esports.db'

# Crear una conexión con la base de datos
def get_connection():
    return sqlite3.connect(DB_PATH)

# Insertar un partido en la tabla Matches
def insert_match(league, local_player, visitor_player, local_team, visitor_team, local_score, visitor_score, match_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Matches (league, local_player, visitor_player, local_team, visitor_team, local_score, visitor_score, match_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (league, local_player, visitor_player, local_team, visitor_team, local_score, visitor_score, match_date))
    match_id = cursor.lastrowid  # Obtener el ID del partido recién insertado
    conn.commit()
    conn.close()
    return match_id

# Insertar un evento en la tabla Events
def insert_event(match_id, event_type, minute, team):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Events (match_id, event_type, minute, team)
        VALUES (?, ?, ?, ?)
    ''', (match_id, event_type, minute, team))
    conn.commit()
    conn.close()

# Insertar una estadística en la tabla Statistics
def insert_statistic(match_id, stat_type, local_value, visitor_value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Statistics (match_id, stat_type, local_value, visitor_value)
        VALUES (?, ?, ?, ?)
    ''', (match_id, stat_type, local_value, visitor_value))
    conn.commit()
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
