import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
from scripts.scrape_data import manejar_panel_cookies, separar_equipo_y_jugador, limpiar_valor

def inicializar_driver():
    """Inicializa y configura el driver de Selenium."""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")  # Ejecuta el navegador en modo headless para mayor velocidad
    return webdriver.Chrome(options=options)

# Cargar variables de entorno
load_dotenv()
URL_MONITOR = os.getenv("URL_MONITOR")

# Ligas de interés
LIGAS_INTERES = [
    "Esoccer Battle - 8 mins play",
    "Esoccer GT Leagues – 12 mins play"
]

def obtener_liga(driver):
    """
    Extrae y devuelve la liga desde la página actual.
    """
    try:
        liga_elemento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.page > div.page-main > div.my-3.my-md-5 > div > nav > ol > li:nth-child(2) > a"))
        )
        liga_texto = liga_elemento.text.strip()
        if not liga_texto:
            print("Liga no encontrada.")
            return None
        print(f"Liga: {liga_texto}")
        return liga_texto
    except Exception as e:
        print(f"Error al extraer la liga: {e}")
        return None

def obtener_minuto_juego(driver):
    """
    Extrae y devuelve el minuto de juego desde la página actual.
    """
    try:
        minuto_juego_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.row.justify-content-md-center.pt-3 > div.col-md-6.text-center > h1 > span > span:nth-child(4)")
            )
        )
        minuto_juego = minuto_juego_element.text.strip()
        if not minuto_juego:
            print("Minuto de juego no encontrado.")
            return None
        print(f"Minuto: {minuto_juego}")
        return minuto_juego
    except TimeoutException:
        print("Timeout al intentar extraer el minuto de juego.")
        return None
    except Exception as e:
        print(f"Error al extraer el minuto de juego: {e}")
        return None
    
def extraer_datos_tabla(driver):
    """Extrae datos de la tabla del partido."""
    try:
        tabla = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-sm > tbody"))
        )
        filas = tabla.find_elements(By.TAG_NAME, "tr")

        datos = []
        for i, fila in enumerate(filas):
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if len(columnas) == 3:
                if i == 0:  # Primera fila: equipo y jugador
                    local_team, local_player = separar_equipo_y_jugador(columnas[0].text.strip())
                    visitor_team, visitor_player = separar_equipo_y_jugador(columnas[2].text.strip())
                    datos.append({
                        "equipo_local": local_team,
                        "jugador_local": local_player,
                        "equipo_visitante": visitor_team,
                        "jugador_visitante": visitor_player
                    })
                else:  # Filas de estadísticas
                    local_value = limpiar_valor(columnas[0].text.strip())
                    stat_type = columnas[1].text.strip()
                    visitor_value = limpiar_valor(columnas[2].text.strip())
                    datos.append({
                        "tipo": stat_type,
                        "valor_local": local_value,
                        "valor_visitante": visitor_value
                    })
        return datos

    except TimeoutException:
        print("No se encontró la tabla de datos del partido.")
        return []
    except Exception as e:
        print(f"Error al extraer datos de la tabla: {e}")
        return []


def extraer_eventos(driver):
    """Extrae los eventos de la página."""
    try:
        eventos = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.list-group > li"))
        )
        datos_eventos = []
        for evento in eventos:
            texto_evento = evento.text.strip()
            equipo = (
                "Local" if "bl-home" in evento.get_attribute("class")
                else "Visitante" if "bl-away" in evento.get_attribute("class")
                else "N/A"
            )
            datos_eventos.append({"descripcion": texto_evento, "equipo": equipo})
        return datos_eventos

    except TimeoutException:
        print("No se encontraron eventos.")
        return []
    except Exception as e:
        print(f"Error al extraer eventos: {e}")
        return []


def recolectar_partidos_interes(driver):
    """Recolecta enlaces de partidos de interés desde la página y extrae cuotas asociadas."""
    partidos = []
    try:
        filas = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for fila in filas:
            try:
                liga = fila.find_element(By.CSS_SELECTOR, "td.league_n > a").text.strip()
                minuto = fila.find_element(By.CSS_SELECTOR, "span.race-time").text.strip().replace("'", "")
                if liga in LIGAS_INTERES and 0 < int(minuto) < 12:
                    enlace = fila.find_element(By.CSS_SELECTOR, "td:nth-child(4) > a").get_attribute("href")
                    cuotas = extraer_cuotas_desde_fila(fila)
                    partidos.append({"liga": liga, "minuto": minuto, "enlace": enlace, "cuotas": cuotas})
            except NoSuchElementException:
                print("No se encontró un enlace válido en esta fila.")
            except Exception as e:
                print(f"Error al procesar la fila: {e}")
    except Exception as e:
        print(f"Error al recolectar partidos: {e}")
    return partidos


def extraer_cuotas_desde_fila(fila):
    """Extrae cuotas desde una fila de la tabla de partidos."""
    cuotas = {"over": None, "linea_goles": None, "less": None}
    try:
        elementos = fila.find_elements(By.CSS_SELECTOR, "[id^='o_']")
        for elemento in elementos:
            id_elemento = elemento.get_attribute("id")
            texto_elemento = elemento.text.strip()
            if id_elemento.endswith("_0"):
                cuotas["over"] = texto_elemento
            elif id_elemento.endswith("_1"):
                cuotas["linea_goles"] = texto_elemento
            elif id_elemento.endswith("_2"):
                cuotas["less"] = texto_elemento
    except Exception as e:
        print(f"Error al extraer cuotas desde la fila: {e}")
    return cuotas

def procesar_partidos(driver):
    """Procesa los partidos de interés y devuelve una lista con todos los datos extraídos."""
    resultados = []
    try:
        driver.get(URL_MONITOR)
        manejar_panel_cookies(driver)

        partidos = recolectar_partidos_interes(driver)
        print(f"Se encontraron {len(partidos)} partidos de interés.")

        for partido in partidos:
            try:
                driver.get(partido["enlace"])
                league = obtener_liga(driver)
                minuto_juego = obtener_minuto_juego(driver)

                if not league or not minuto_juego:
                    print("Información insuficiente para procesar el partido. Saltando...")
                    continue

                partido_data = {
                    "liga": league,
                    "minuto": minuto_juego,
                    "enlace": partido["enlace"],
                    "cuotas": partido["cuotas"],
                    "estadisticas": extraer_datos_tabla(driver),
                    "eventos": extraer_eventos(driver),
                }
                resultados.append(partido_data)
            except Exception as e:
                print(f"Error al procesar el partido: {e}")
    except Exception as e:
        print(f"Error general al procesar partidos: {e}")
    return resultados


def main():
    """Punto de entrada principal del script."""
    driver = inicializar_driver()
    try:
        resultados = procesar_partidos(driver)
        print(f"Resultados obtenidos: {resultados}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
