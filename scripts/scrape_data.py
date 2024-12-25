import os
import re
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

# Cargar variables de entorno
load_dotenv()
URL_DE_LA_PAGINA = os.getenv("URL_DE_LA_PAGINA")

# Inicializar el driver
def inicializar_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    return driver

# Manejar el panel de cookies
def manejar_panel_cookies(driver):
    try:
        boton_cookies = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.fc-button.fc-cta-consent.fc-primary-button"))
        )
        boton_cookies.click()
        print("Panel de cookies aceptado.")
    except TimeoutException:
        print("El panel de cookies no apareció o ya fue aceptado.")

# Extraer equipo y jugador
def separar_equipo_y_jugador(texto):
    """Extrae el equipo y el jugador del formato 'Equipo (Jugador)'."""
    match = re.match(r"(.+?)\s+\((.+?)\)", texto)
    if match:
        equipo = match.group(1).strip()
        jugador = match.group(2).strip()
        return equipo, jugador
    return texto, None

# Extraer datos de la tabla
def extraer_datos_tabla(driver):
    """Extrae datos de la tabla y separa equipo y jugador en la primera fila."""
    try:
        tabla = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-sm > tbody"))
        )
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        print("\nDatos de la tabla:")

        for i, fila in enumerate(filas):
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if len(columnas) == 3:
                if i == 0:  # Primera fila: extraer equipo y jugador
                    local_equipo, local_jugador = separar_equipo_y_jugador(columnas[0].text.strip())
                    visitante_equipo, visitante_jugador = separar_equipo_y_jugador(columnas[2].text.strip())
                    print(f"Local: Equipo = {local_equipo}, Jugador = {local_jugador}")
                    print(f"Visitante: Equipo = {visitante_equipo}, Jugador = {visitante_jugador}")
                else:  # Filas de estadísticas
                    valor_local = limpiar_valor(columnas[0].text.strip())
                    estadistica = columnas[1].text.strip()
                    valor_visitante = limpiar_valor(columnas[2].text.strip())
                    print(f"{estadistica}: Local = {valor_local}, Visitante = {valor_visitante}")
    except TimeoutException:
        print("No se pudo encontrar la tabla.")
    except Exception as e:
        print(f"Error al procesar la tabla: {e}")

# Función para limpiar valores repetidos
def limpiar_valor(valor):
    """Limpia valores repetidos y organiza los datos."""
    valores_unicos = list(set(valor.split("\n")))
    return " / ".join(valores_unicos)

# Recolectar enlaces de partidos
def obtener_enlaces_partidos(driver):
    """Obtiene los enlaces de los partidos desde la tabla principal."""
    enlaces = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-pane.active > div > table > tbody"))
        )
        filas = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane.active > div > table > tbody > tr")
        for fila in filas:
            try:
                enlace_elemento = fila.find_element(By.CSS_SELECTOR, "td:nth-child(4) > a")
                enlaces.append(enlace_elemento.get_attribute("href"))
            except NoSuchElementException:
                print("No se pudo extraer el enlace de una fila.")
    except TimeoutException:
        print("No se pudo encontrar la tabla de partidos.")
    return enlaces

# Scraping principal
def scrape_data():
    """Realiza el scraping de la página principal y de cada partido."""
    driver = inicializar_driver()
    try:
        driver.get(URL_DE_LA_PAGINA)
        manejar_panel_cookies(driver)

        enlaces_partidos = obtener_enlaces_partidos(driver)
        print(f"\nEnlaces encontrados: {enlaces_partidos}")

        for url_partido in enlaces_partidos:
            try:
                print(f"\nAccediendo al partido: {url_partido}")
                driver.get(url_partido)
                extraer_datos_tabla(driver)
            except StaleElementReferenceException as e:
                print(f"Error de referencia obsoleta al acceder al partido: {e}")
            except Exception as e:
                print(f"Error general al procesar el partido {url_partido}: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_data()
