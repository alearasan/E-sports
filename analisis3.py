import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Conectar a la base de datos SQLite
conn = sqlite3.connect('partidos.db')
cursor = conn.cursor()

# Consulta para obtener los datos necesarios
query = '''
    SELECT probabilidad_1, probabilidad_2, probabilidad_3, resultado_final
    FROM partidos
'''

# Ejecutar la consulta
cursor.execute(query)

# Obtener todos los resultados de la consulta
data = cursor.fetchall()

# Cerrar la conexión del cursor y la base de datos
cursor.close()
conn.close()

# Convertir los datos obtenidos a un DataFrame
df = pd.DataFrame(data, columns=['probabilidad_1', 'probabilidad_2', 'probabilidad_3', 'resultado_final'])

# Convertir las probabilidades a tipo numérico, forzando errores a NaN
df['probabilidad_1'] = pd.to_numeric(df['probabilidad_1'], errors='coerce')
df['probabilidad_2'] = pd.to_numeric(df['probabilidad_2'], errors='coerce')
df['probabilidad_3'] = pd.to_numeric(df['probabilidad_3'], errors='coerce')

# Función para extraer el resultado final y determinar el ganador
def obtener_resultado_final(resultado):
    if resultado == 'Resultado no disponible':
        return None  # No procesar este partido si el resultado no está disponible
    
    try:
        local, visitante = map(int, resultado.split('-'))
        if local > visitante:
            return 1  # Gana el local
        elif local < visitante:
            return 3  # Gana el visitante
        else:
            return 2  # Empate
    except ValueError:
        return None  # Si ocurre un error en la conversión, lo ignoramos

# Aplicar la función para convertir los resultados en categorías numéricas
df['resultado_final'] = df['resultado_final'].apply(obtener_resultado_final)

# Filtrar los partidos que no tienen un resultado válido
df = df.dropna(subset=['resultado_final'])

# Crear rangos para las probabilidades
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Dividir en intervalos de 10%
labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100']

# Categorizar las probabilidades en función de los rangos
df['rango_probabilidad_1'] = pd.cut(df['probabilidad_1'], bins=bins, labels=labels)
df['rango_probabilidad_2'] = pd.cut(df['probabilidad_2'], bins=bins, labels=labels)
df['rango_probabilidad_3'] = pd.cut(df['probabilidad_3'], bins=bins, labels=labels)

# Función para calcular la probabilidad de que ocurra el resultado esperado dentro de cada intervalo
def calcular_probabilidad(df, probabilidad_col, resultado_col):
    probabilidad_resultado = []
    
    for label in labels:
        # Filtrar el DataFrame para cada rango
        df_rango = df[df[probabilidad_col] == label]
        
        # Verificar si hay datos en el rango, evitar división por cero
        if df_rango.shape[0] > 0:
            probabilidad_local = df_rango[df_rango[resultado_col] == 1].shape[0] / df_rango.shape[0]
            probabilidad_empate = df_rango[df_rango[resultado_col] == 2].shape[0] / df_rango.shape[0]
            probabilidad_visitante = df_rango[df_rango[resultado_col] == 3].shape[0] / df_rango.shape[0]
            conteo_partidos = df_rango.shape[0]  # Contar el número de partidos en el rango
        else:
            probabilidad_local = probabilidad_empate = probabilidad_visitante = 0
            conteo_partidos = 0

        probabilidad_resultado.append({
            'rango': label,
            'probabilidad_local': probabilidad_local,
            'probabilidad_empate': probabilidad_empate,
            'probabilidad_visitante': probabilidad_visitante,
            'conteo_partidos': conteo_partidos  # Añadir el conteo de partidos
        })
    
    return pd.DataFrame(probabilidad_resultado)

# Calcular la probabilidad para cada una de las probabilidades prepartido
df_resultado_1 = calcular_probabilidad(df, 'rango_probabilidad_1', 'resultado_final')
df_resultado_2 = calcular_probabilidad(df, 'rango_probabilidad_2', 'resultado_final')
df_resultado_3 = calcular_probabilidad(df, 'rango_probabilidad_3', 'resultado_final')

# Mostrar las probabilidades y el conteo de partidos
print("Probabilidades y conteo de partidos cuando se usa probabilidad_1")
print(df_resultado_1)

print("\nProbabilidades y conteo de partidos cuando se usa probabilidad_2")
print(df_resultado_2)

print("\nProbabilidades y conteo de partidos cuando se usa probabilidad_3")
print(df_resultado_3)

# Graficar las probabilidades para cada caso
plt.figure(figsize=(10, 6))

# Graficar para probabilidad_1 y probabilidad_local
plt.plot(df_resultado_1['rango'], df_resultado_1['probabilidad_local'], label='Probabilidad Gana Local (probabilidad_1)', marker='o')

# Graficar para probabilidad_2 y probabilidad_empate
plt.plot(df_resultado_2['rango'], df_resultado_2['probabilidad_empate'], label='Probabilidad Empate (probabilidad_2)', marker='o')

# Graficar para probabilidad_3 y probabilidad_visitante
plt.plot(df_resultado_3['rango'], df_resultado_3['probabilidad_visitante'], label='Probabilidad Gana Visitante (probabilidad_3)', marker='o')

# Etiquetas y título
plt.title('Relación entre probabilidades prepartido y resultado esperado')
plt.xlabel('Rango de probabilidad prepartido (%)')
plt.ylabel('Probabilidad de que ocurra el resultado esperado')
plt.xticks(rotation=45)

# Mostrar leyenda
plt.legend()

# Mostrar la gráfica
plt.grid(True)
plt.tight_layout()
plt.show()
