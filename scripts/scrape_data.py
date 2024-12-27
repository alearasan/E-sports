import os
import re
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from scripts.database import setup_database, insert_match, insert_statistic, insert_event

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

def convertir_fecha(fecha_texto):
    """Convierte la fecha y hora extraídas en formatos estándar."""
    from datetime import datetime
    try:
        # Manejar el formato 'YYYY/MM/DD HH:MM'
        fecha_obj = datetime.strptime(fecha_texto, "%Y/%m/%d %H:%M")
        fecha_formato = fecha_obj.strftime("%Y-%m-%d")  # Formato de fecha
        hora_formato = fecha_obj.strftime("%H:%M:%S")  # Formato de hora
        return fecha_formato, hora_formato
    except ValueError:
        print(f"Formato de fecha desconocido: {fecha_texto}")
        return fecha_texto, None  # Devuelve la fecha original si no se puede convertir

def extraer_fecha_partido(driver):
    """Extrae la fecha y hora del partido desde el selector especificado."""
    try:
        fecha_elemento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.page > div.page-main > div.my-3.my-md-5 > div > div.row.justify-content-md-center.pt-3 > div.col-md-6.text-center > h1 > span > span:nth-child(4)"))
        )
        fecha_texto = fecha_elemento.text.strip()
        fecha, hora = convertir_fecha(fecha_texto)
        print(f"Fecha extraída: {fecha}, Hora extraída: {hora}")
        return fecha, hora
    except TimeoutException:
        print("No se pudo encontrar la fecha del partido.")
        return None, None
    except Exception as e:
        print(f"Error al extraer la fecha del partido: {e}")
        return None, None

    
def extraer_liga(driver):
    """Extrae el nombre de la liga desde el selector especificado."""
    try:
        liga_elemento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.page > div.page-main > div.my-3.my-md-5 > div > nav > ol > li:nth-child(2) > a"))
        )
        liga_texto = liga_elemento.text.strip()
        print(f"Liga extraída: {liga_texto}")
        return liga_texto
    except TimeoutException:
        print("No se pudo encontrar la liga.")
        return None
    except Exception as e:
        print(f"Error al extraer la liga: {e}")
        return None

def extraer_eventos(driver, match_id):
    """Extrae los eventos del partido y los guarda en la base de datos."""
    try:
        # Localizar la lista de eventos
        eventos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.list-group > li"))
        )

        for evento in eventos:
            try:
                # Extraer el texto del evento
                texto_evento = evento.text.strip()

                # Determinar el equipo (local o visitante) basándose en las clases
                equipo = "Local" if "bl-home" in evento.get_attribute("class") else "Visitante" if "bl-away" in evento.get_attribute("class") else "N/A"

                # Extraer el minuto, tipo de evento y detalles adicionales
                match_evento = re.match(r"(\d+(\+\d+)?)'\s+-\s+(.+?)\s+-\s+\((.+?)\)", texto_evento)
                if match_evento:
                    minuto_completo = match_evento.group(1)  # Ejemplo: "12+1"
                    minuto_base = int(minuto_completo.split("+")[0])  # Extraer solo "12"
                    tipo_evento = match_evento.group(3).strip()
                    detalle_evento = match_evento.group(4).strip()
                else:
                    # Si no se ajusta al formato, continuar con el siguiente
                    print(f"Evento ignorado: {texto_evento}")
                    continue

                # Imprimir el evento extraído
                print(f"Match id: {match_id} Evento: Minuto = {minuto_base}, Tipo = {tipo_evento}, Equipo = {equipo}, Detalle = {detalle_evento}")

                # Insertar el evento en la base de datos
                insert_event(match_id, tipo_evento, minuto_base, equipo)
            except Exception as e:
                print(f"Error al procesar un evento: {e}")
    except TimeoutException:
        print("No se pudo encontrar la lista de eventos.")
    except Exception as e:
        print(f"Error al extraer los eventos: {e}")


# Extraer equipo y jugador
def separar_equipo_y_jugador(texto):
    """Extrae el equipo y el jugador del formato 'Equipo (Jugador)'."""
    match = re.match(r"(.+?)\s+\((.+?)\)", texto)
    if match:
        equipo = match.group(1).strip()
        jugador = match.group(2).strip()
        return equipo, jugador
    return texto, None

def extraer_datos_tabla(driver, league, match_date, match_time):
    """Extrae datos de la tabla, imprime los valores y guarda en la base de datos."""
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
                    local_team, local_player = separar_equipo_y_jugador(columnas[0].text.strip())
                    visitor_team, visitor_player = separar_equipo_y_jugador(columnas[2].text.strip())
                    print(f"Equipo: Local = {local_team}, Visitante = {visitor_team}")
                    print(f"Jugador: Local = {local_player}, Visitante = {visitor_player}")
                else:  # Otras filas: estadísticas
                    local_value = limpiar_valor(columnas[0].text.strip())
                    stat_type = columnas[1].text.strip()
                    visitor_value = limpiar_valor(columnas[2].text.strip())
                    stats.append((stat_type, local_value, visitor_value))
                    print(f"{stat_type}: Local = {local_value}, Visitante = {visitor_value}")

        # Insertar el partido en la base de datos
        local_score = stats[0][1]  # Supongamos que los goles son la primera estadística
        visitor_score = stats[0][2]
        match_id = insert_match(
            league=league,
            local_player=local_player,
            visitor_player=visitor_player,
            local_team=local_team,
            visitor_team=visitor_team,
            local_score=int(local_score),
            visitor_score=int(visitor_score),
            match_date=f"{match_date} {match_time}"
        )
        print(f"Partido insertado en la base de datos con ID: {match_id}")

        # Insertar estadísticas en la base de datos
        for stat_type, local_value, visitor_value in stats:
            insert_statistic(match_id, stat_type, int(local_value), int(visitor_value))

        return match_id
    
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
    """Realiza el scraping de la página principal y de cada partido con soporte para paginación."""
    setup_database()  # Asegúrate de que la base de datos está configurada

    driver = inicializar_driver()
    try:
        page = 1
        while True:
            # Construir la URL para la página actual
            pagina_url = f"{URL_DE_LA_PAGINA}/p.{page}"
            print(f"\nAccediendo a la página: {pagina_url}")
            driver.get(pagina_url)
            
            # Manejar el panel de cookies en la primera carga
            if page == 1:
                manejar_panel_cookies(driver)

            # Obtener los enlaces de los partidos en la página
            enlaces_partidos = obtener_enlaces_partidos(driver)
            if not enlaces_partidos:
                print("No se encontraron más enlaces. Finalizando paginación.")
                break  # Salir del bucle si no hay más enlaces
            
            print(f"\nEnlaces encontrados en la página {page}: {enlaces_partidos}")

            # Procesar cada enlace de partido
            for url_partido in enlaces_partidos:
                try:
                    print(f"\nAccediendo al partido: {url_partido}")
                    driver.get(url_partido)

                    # Extraer la liga
                    league = extraer_liga(driver)
                    if not league:
                        print("Liga no encontrada. Saltando partido.")
                        continue

                    # Extraer la fecha y hora del partido
                    match_date, match_time = extraer_fecha_partido(driver)
                    if not match_date or not match_time:
                        print("Fecha u hora no encontradas. Saltando partido.")
                        continue

                    # Extraer y guardar los datos del partido
                    match_id = extraer_datos_tabla(driver, league, match_date, match_time)

                    # Extraer y guardar los eventos del partido
                    extraer_eventos(driver, match_id)
                except StaleElementReferenceException as e:
                    print(f"Error de referencia obsoleta al acceder al partido: {e}")
                except Exception as e:
                    print(f"Error general al procesar el partido {url_partido}: {e}")

            # Incrementar el número de página
            page += 1
    finally:
        driver.quit()



if __name__ == "__main__":
    scrape_data()
