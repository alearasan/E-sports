from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scrape_data import (
    inicializar_driver,
    manejar_panel_cookies,
    extraer_liga,
    extraer_fecha_partido,
    extraer_eventos,
)

# Cargar variables de entorno
load_dotenv()
URL_MONITOR = os.getenv("URL_MONITOR")

def extraer_datos_tabla(driver, league, match_date, match_time):
    """
    Extrae datos de la tabla del partido y los imprime en consola.
    """
    try:
        tabla = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-sm > tbody"))
        )
        filas = tabla.find_elements(By.TAG_NAME, "tr")

        local_team, local_player = None, None
        visitor_team, visitor_player = None, None
        stats = []

        for i, fila in enumerate(filas):
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if len(columnas) == 3:
                if i == 0:  # Primera fila: equipo y jugador
                    local_team = columnas[0].text.strip()
                    visitor_team = columnas[2].text.strip()
                    print(f"Equipo: Local = {local_team}, Visitante = {visitor_team}")
                else:  # Filas de estadísticas
                    local_value = columnas[0].text.strip()
                    stat_type = columnas[1].text.strip()
                    visitor_value = columnas[2].text.strip()
                    stats.append((stat_type, local_value, visitor_value))
                    print(f"{stat_type}: Local = {local_value}, Visitante = {visitor_value}")

    except TimeoutException:
        print("No se pudo encontrar la tabla de datos del partido.")
    except Exception as e:
        print(f"Error al extraer datos de la tabla: {e}")

def extraer_eventos(driver, match_id=None):
    """
    Extrae los eventos de la página y los imprime en consola.
    """
    try:
        eventos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.list-group > li"))
        )

        for evento in eventos:
            texto_evento = evento.text.strip()

            # Determinar el equipo (local o visitante) basándose en las clases
            equipo = "Local" if "bl-home" in evento.get_attribute("class") else "Visitante" if "bl-away" in evento.get_attribute("class") else "N/A"

            print(f"Evento: {texto_evento} | Equipo: {equipo}")

    except TimeoutException:
        print("No se pudo encontrar la lista de eventos.")
    except Exception as e:
        print(f"Error al extraer eventos: {e}")


def extraer_info_partidos(driver):
    """
    Extrae la información de todos los partidos en la página haciendo clic en el enlace correspondiente de cada fila.
    """
    try:
        while True:  # Si hay múltiples páginas, agrega un bucle aquí
            # Esperar a que la tabla esté presente
            tabla_partidos = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
            )
            filas = tabla_partidos.find_elements(By.TAG_NAME, "tr")

            print(f"Se encontraron {len(filas)} filas en la tabla.")

            # Recorrer todas las filas y hacer clic en el enlace de cada una
            for i, fila in enumerate(filas):
                try:
                    # Volver a encontrar las filas para evitar elementos "stale"
                    filas_actualizadas = driver.find_elements(By.TAG_NAME, "tr")
                    fila_actual = filas_actualizadas[i]

                    # Localizar el enlace dentro de la fila actualizada
                    enlace = fila_actual.find_element(By.CSS_SELECTOR, "td:nth-child(4) > a")
                    enlace_texto = enlace.text.strip()
                    enlace_href = enlace.get_attribute("href")
                    print(f"\n[{i+1}] Haciendo clic en el enlace: {enlace_texto} ({enlace_href})")

                    # Hacer clic en el enlace
                    enlace.click()

                    # Esperar a que la nueva página cargue
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-sm"))
                    )

                    # Extraer información de la nueva página
                    league = extraer_liga(driver)
                    print(f"Liga: {league}")
                    
                    match_date, match_time = extraer_fecha_partido(driver)
                    print(f"Fecha: {match_date}, Hora: {match_time}")
                    
                    print("Datos del partido:")
                    extraer_datos_tabla(driver, league, match_date, match_time)

                    print("Eventos del partido:")
                    extraer_eventos(driver, match_id=None)

                    # Volver a la página anterior
                    driver.get(URL_MONITOR)

                    # Esperar a que la tabla se recargue
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
                    )
                except NoSuchElementException:
                    print(f"Enlace no encontrado en la fila {i+1}.")
                except TimeoutException:
                    print(f"Tiempo de espera agotado al cargar la información del partido en la fila {i+1}.")
                except Exception as e:
                    print(f"Error procesando la fila {i+1}: {e}")
    except TimeoutException:
        print("No se pudo cargar la tabla de partidos.")
    except Exception as e:
        print(f"Error al extraer partidos: {e}")
    """
    Extrae la información de todos los partidos en la página haciendo clic en el enlace correspondiente de cada fila.
    """
    try:
        # Esperar a que la tabla esté presente
        tabla_partidos = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
        )
        filas = tabla_partidos.find_elements(By.TAG_NAME, "tr")

        print(f"Se encontraron {len(filas)} filas en la tabla.")

        # Recorrer todas las filas y hacer clic en el enlace de cada una
        for i, fila in enumerate(filas):
            try:
                # Localizar el enlace dentro de la fila (columna específica)
                enlace = fila.find_element(By.CSS_SELECTOR, "td:nth-child(4) > a")
                enlace_texto = enlace.text.strip()
                enlace_href = enlace.get_attribute("href")
                print(f"\n[{i+1}] Haciendo clic en el enlace: {enlace_texto} ({enlace_href})")

                # Hacer clic en el enlace
                enlace.click()

                # Esperar a que la nueva página cargue
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-sm"))
                )

                # Extraer información de la nueva página
                league = extraer_liga(driver)
                print(f"Liga: {league}")
                
                match_date, match_time = extraer_fecha_partido(driver)
                print(f"Fecha: {match_date}, Hora: {match_time}")
                
                print("Datos del partido:")
                extraer_datos_tabla(driver, league, match_date, match_time)

                print("Eventos del partido:")
                extraer_eventos(driver, match_id=None)

                # Volver a la página anterior
                driver.get(URL_MONITOR)

                # Esperar a que la tabla se recargue
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
                )
            except NoSuchElementException:
                print(f"Enlace no encontrado en la fila {i+1}.")
            except TimeoutException:
                print(f"Tiempo de espera agotado al cargar la información del partido en la fila {i+1}.")
            except Exception as e:
                print(f"Error procesando la fila {i+1}: {e}")

    except TimeoutException:
        print("No se pudo cargar la tabla de partidos.")
    except Exception as e:
        print(f"Error al extraer partidos: {e}")


def main():

    driver = inicializar_driver()

    try:
        # URL de la página principal
        driver.get(URL_MONITOR)

        # Manejar cookies si es necesario
        manejar_panel_cookies(driver)

        # Extraer información de todos los partidos
        extraer_info_partidos(driver)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
