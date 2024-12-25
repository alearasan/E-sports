import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Inicializar el driver de Selenium
def inicializar_driver():
    driver = webdriver.Chrome()  # Asegúrate de tener el chromedriver configurado correctamente
    return driver

# Conectar a la base de datos SQLite
def conectar_base_datos():
    conn = sqlite3.connect('partidos.db')
    cursor = conn.cursor()
    return conn, cursor

# Crear la tabla en la base de datos
def crear_tabla(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT,
            away_team TEXT,
            fecha TEXT,
            probabilidad_1 TEXT,
            probabilidad_2 TEXT,
            probabilidad_3 TEXT,
            marcador TEXT,
            media_goles TEXT,
            resultado_final TEXT,
            UNIQUE(home_team, away_team, fecha, marcador, resultado_final)  -- Añadimos la restricción de unicidad
        )
    ''')

# Extraer equipos (local y visitante)
def extraer_equipos(partido):
    equipos = partido.find_element(By.CLASS_NAME, 'tnmscn')
    home_team = equipos.find_element(By.CLASS_NAME, 'homeTeam').text
    away_team = equipos.find_element(By.CLASS_NAME, 'awayTeam').text
    return home_team, away_team

# Extraer fecha del partido
def extraer_fecha(partido):
    equipos = partido.find_element(By.CLASS_NAME, 'tnmscn')
    fecha = equipos.find_element(By.CLASS_NAME, 'date_bah').text
    return fecha

# Extraer probabilidades
def extraer_probabilidades(partido):
    probabilidades = partido.find_elements(By.CLASS_NAME, 'fprc')
    if probabilidades:
        fprc_spans = probabilidades[0].find_elements(By.TAG_NAME, 'span')
        if len(fprc_spans) >= 3:
            probabilidad_1 = fprc_spans[0].text
            probabilidad_2 = fprc_spans[1].text
            probabilidad_3 = fprc_spans[2].text
        else:
            probabilidad_1 = probabilidad_2 = probabilidad_3 = 'No disponible'
    else:
        probabilidad_1 = probabilidad_2 = probabilidad_3 = 'No disponible'
    return probabilidad_1, probabilidad_2, probabilidad_3

# Extraer marcador
def extraer_marcador(partido):
    try:
        marcador = WebDriverWait(partido, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ex_sc'))
        ).text
    except:
        marcador = 'No disponible'
    return marcador

# Extraer media de goles
def extraer_media_goles(partido):
    try:
        media_goles = partido.find_element(By.CLASS_NAME, 'avg_sc').text
    except:
        media_goles = 'No disponible'
    return media_goles

# Extraer resultado final
def extraer_resultado_final(partido):
    try:
        resultado_final = partido.find_element(By.CLASS_NAME, 'lscr_td').text
    except:
        resultado_final = 'Resultado no disponible'
    return resultado_final

# Verificar si el partido ya existe en la base de datos
def verificar_partido_existente(cursor, home_team, away_team, fecha, marcador, resultado_final):
    cursor.execute('''
        SELECT 1 FROM partidos
        WHERE home_team = ? AND away_team = ? AND fecha = ? AND marcador = ? AND resultado_final = ?
    ''', (home_team, away_team, fecha, marcador, resultado_final))
    return cursor.fetchone() is not None

# Insertar datos en la base de datos si no existen duplicados
def insertar_datos(cursor, conn, home_team, away_team, fecha, probabilidad_1, probabilidad_2, probabilidad_3, marcador, media_goles, resultado_final):
    if not verificar_partido_existente(cursor, home_team, away_team, fecha, marcador, resultado_final):
        if all([home_team, away_team, fecha, probabilidad_1, probabilidad_2, probabilidad_3, marcador, media_goles, resultado_final]):
            cursor.execute('''
                INSERT INTO partidos (home_team, away_team, fecha, probabilidad_1, probabilidad_2, probabilidad_3, marcador, media_goles, resultado_final)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (home_team, away_team, fecha, probabilidad_1, probabilidad_2, probabilidad_3, marcador, media_goles, resultado_final))
            conn.commit()
            print("Partido insertado:", home_team, "vs", away_team)
        else:
            print("Faltan campos para el partido:", home_team, "vs", away_team)
    else:
        print("El partido ya existe en la base de datos:", home_team, "vs", away_team)

# Procesar la página web y extraer los datos
def procesar_pagina(driver, cursor, conn):
    driver.get('https://www.forebet.com/es/esoccer/predictions-from-yesterday')  # URL de la página de predicciones
    #driver.get('https://www.forebet.com/es/esoccer/predictions-for-today/finished')  # URL de la página de predicciones
    time.sleep(3)  # Espera para asegurarse de que la página cargue completamente

    # Espera a que el elemento 'ex_sc' esté presente
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'ex_sc'))
    )
    
    # Encuentra todos los contenedores de partidos
    partidos = driver.find_elements(By.CLASS_NAME, 'rcnt')

    # Extrae la información de cada partido
    for partido in partidos:
        home_team, away_team = extraer_equipos(partido)
        fecha = extraer_fecha(partido)
        probabilidad_1, probabilidad_2, probabilidad_3 = extraer_probabilidades(partido)
        marcador = extraer_marcador(partido)
        media_goles = extraer_media_goles(partido)
        resultado_final = extraer_resultado_final(partido)

        # Insertar los datos en la base de datos si no existen duplicados
        insertar_datos(cursor, conn, home_team, away_team, fecha, probabilidad_1, probabilidad_2, probabilidad_3, marcador, media_goles, resultado_final)

        # Mostrar la información extraída
        print(f"Partido: {home_team} vs {away_team}")
        print(f"Fecha: {fecha}")
        print(f"Probabilidad de victoria (1x2): {probabilidad_1}, {probabilidad_2}, {probabilidad_3}")
        print(f"Marcador final: {marcador}")
        print(f"Media goles: {media_goles}")
        print(f"Resultado final: {resultado_final}")
        print('-' * 50)

# Función principal
def main():
    # Inicialización
    driver = inicializar_driver()
    conn, cursor = conectar_base_datos()

    # Crear tabla en la base de datos
    crear_tabla(cursor)

    # Procesar la página y extraer datos
    procesar_pagina(driver, cursor, conn)

    # Cerrar conexiones
    conn.close()
    driver.quit()

if __name__ == '__main__':
    main()
