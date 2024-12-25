import sqlite3
import numpy as np

# Conectar a la base de datos SQLite
def conectar_base_datos():
    conn = sqlite3.connect('partidos.db')  # Asegúrate de que el nombre de tu base de datos es correcto
    cursor = conn.cursor()
    return conn, cursor

# Función para obtener todos los partidos de los dos jugadores, incluyendo la fecha
def obtener_partidos(cursor, jugador1, jugador2):
    cursor.execute(''' 
        SELECT home_team, away_team, marcador, resultado_final, fecha
        FROM partidos
    ''')
    partidos = cursor.fetchall()
    partidos_filtrados = [
        (home_team, away_team, marcador, resultado_final, fecha)
        for home_team, away_team, marcador, resultado_final, fecha in partidos
        if jugador1 in home_team or jugador1 in away_team or jugador2 in home_team or jugador2 in away_team
    ]
    return partidos_filtrados

# Función para filtrar partidos entre dos jugadores específicos
def filtrar_partidos_directos(partidos, jugador1, jugador2):
    return [
        partido for partido in partidos
        if (jugador1 in partido[0] or jugador1 in partido[1]) and 
           (jugador2 in partido[0] or jugador2 in partido[1])
    ]

# Función para obtener los últimos N partidos
def obtener_ultimos_partidos(partidos, n):
    return partidos[-n:]

# Función para calcular el número de goles de un partido
def calcular_goles(resultado_final):
    try:
        goles_home, goles_away = map(int, resultado_final.split('-'))
        return goles_home + goles_away
    except ValueError:
        return None  # Si el formato no es correcto

# Función para calcular la probabilidad de que los goles sean mayores que los umbrales
def calcular_probabilidades(partidos):
    goles_totales = [
        calcular_goles(partido[3]) for partido in partidos if calcular_goles(partido[3]) is not None
    ]
    umbrales = [2, 3, 4, 5, 6, 7, 8]
    probabilidades = {
        f'>= {umbral} goles': sum(1 for goles in goles_totales if goles >= umbral) / len(goles_totales) * 100
        for umbral in umbrales
    } if goles_totales else {f'>= {umbral} goles': 0 for umbral in umbrales}
    return goles_totales, probabilidades

# Función para calcular la media de goles
def calcular_media_goles(goles_totales):
    return np.mean(goles_totales) if goles_totales else 0

# Función para mostrar los resultados de los partidos y las probabilidades
def mostrar_resultados(partidos, goles_totales, probabilidades, jugador1, jugador2):
    print(f"Partidos analizados: {len(partidos)}")
    for partido in partidos:
        home_team, away_team, marcador, resultado_final, fecha = partido
        print(f"Partido: {home_team} vs {away_team}, Fecha: {fecha}, Resultado: {resultado_final}")
    print("-" * 50)
    print("Probabilidades de goles mayores a ciertos umbrales:")
    for umbral, probabilidad in probabilidades.items():
        print(f"{umbral}: {probabilidad:.2f}%")
    media_goles = calcular_media_goles(goles_totales)
    print(f"Media de goles por partido: {media_goles:.2f}\n")

# Función para analizar partidos generales y directos por separado
def analizar_partidos(cursor, jugador1, jugador2, n=10):
    # Obtener todos los partidos
    partidos = obtener_partidos(cursor, jugador1, jugador2)
    if not partidos:
        print(f"No se encontraron partidos para los jugadores {jugador1} y {jugador2}.")
        return

    # Partidos directos
    print("\n--- Análisis de partidos directos ---")
    partidos_directos = filtrar_partidos_directos(partidos, jugador1, jugador2)
    if partidos_directos:
        goles_totales_directos, probabilidades_directos = calcular_probabilidades(partidos_directos)
        mostrar_resultados(partidos_directos, goles_totales_directos, probabilidades_directos, jugador1, jugador2)
    else:
        print(f"No se encontraron partidos directos entre {jugador1} y {jugador2}.")

    # Últimos N partidos generales
    print(f"\n--- Análisis de los últimos {n} partidos generales ---")
    ultimos_partidos = obtener_ultimos_partidos(partidos, n)
    if ultimos_partidos:
        goles_totales_ultimos, probabilidades_ultimos = calcular_probabilidades(ultimos_partidos)
        mostrar_resultados(ultimos_partidos, goles_totales_ultimos, probabilidades_ultimos, jugador1, jugador2)
    else:
        print(f"No se encontraron suficientes partidos recientes.")

# Función principal
def main():
    jugador1 = 'Spartacus'
    jugador2 = 'Banega'
    n = 20  # Número de partidos recientes a analizar
    # Conectar a la base de datos
    conn, cursor = conectar_base_datos()
    # Analizar partidos
    analizar_partidos(cursor, jugador1, jugador2, n)
    # Cerrar la conexión
    conn.close()

if __name__ == '__main__':
    main()
