from flask import Flask, render_template, jsonify
from scripts.monitor_matches import inicializar_driver, procesar_partidos
import threading

app = Flask(__name__)

# Variable global para almacenar los datos
partidos_data = []

def scraper_thread():
    """Hilo para ejecutar el scraper en segundo plano."""
    global partidos_data
    driver = inicializar_driver()
    try:
        while True:
            partidos_data = procesar_partidos(driver)
    finally:
        driver.quit()

@app.route("/")
def index():
    """Ruta principal para mostrar la página HTML."""
    return render_template("monitor.html")

@app.route("/api/partidos")
def api_partidos():
    """Ruta API para devolver los datos en formato JSON."""
    return jsonify(partidos_data)

if __name__ == "__main__":
    # Iniciar el hilo del scraper
    thread = threading.Thread(target=scraper_thread, daemon=True)
    thread.start()

    # Iniciar Flask sin reloader
    app.run(debug=True, port=5000, use_reloader=False)

