import sqlite3

DB_PATH = 'database/fifa_esports.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def insert_match(league, local_team, visitor_team, local_score, visitor_score, match_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Matches (league, local_team, visitor_team, local_score, visitor_score, match_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (league, local_team, visitor_team, local_score, visitor_score, match_date))
    conn.commit()
    conn.close()

def insert_event(match_id, event_type, minute, team):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Events (match_id, event_type, minute, team)
        VALUES (?, ?, ?, ?)
    ''', (match_id, event_type, minute, team))
    conn.commit()
    conn.close()

def query_matches():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Matches')
    rows = cursor.fetchall()
    conn.close()
    return rows
