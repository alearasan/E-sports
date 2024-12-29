import pandas as pd
import os

def preprocess_football_data(matches_path, statistics_path, events_path, output_path):
    # Cargar los datos
    matches = pd.read_csv(matches_path)
    statistics = pd.read_csv(statistics_path)
    events = pd.read_csv(events_path)

    # Limpieza de datos
    matches_cleaned = matches.drop_duplicates().dropna()
    statistics_cleaned = statistics.drop_duplicates().dropna()
    events_cleaned = events.drop_duplicates().dropna()

    # Asegurar que las columnas relevantes sean integer
    matches_cleaned['id'] = matches_cleaned['id'].astype(int)
    statistics_cleaned['match_id'] = statistics_cleaned['match_id'].astype(int)
    events_cleaned['match_id'] = events_cleaned['match_id'].astype(int)
    events_cleaned['minute'] = events_cleaned['minute'].astype(int)

    # Identificar estadísticas con pocos datos
    stat_type_counts = statistics_cleaned['stat_type'].value_counts()
    threshold = 0.5 * len(matches_cleaned)  # Considerar 50% como el umbral
    valid_stat_types = stat_type_counts[stat_type_counts >= threshold].index

    # Filtrar estadísticas poco frecuentes
    statistics_cleaned = statistics_cleaned[statistics_cleaned['stat_type'].isin(valid_stat_types)]

    # Convertir los valores de estadísticas a integer
    statistics_cleaned['local_value'] = statistics_cleaned['local_value'].astype(int)
    statistics_cleaned['visitor_value'] = statistics_cleaned['visitor_value'].astype(int)

    # Preprocesar eventos para crear listas de minutos de goles por equipo
    events_goals = events_cleaned[events_cleaned['event_type'].str.contains('Goal', na=False)]
    local_goals = events_goals[events_goals['team'] == 'Local'].groupby('match_id')['minute'].apply(list).rename('local_minute_goals')
    visitor_goals = events_goals[events_goals['team'] == 'Visitante'].groupby('match_id')['minute'].apply(list).rename('visitor_minute_goals')

    # Unir las listas de goles al dataset de partidos
    matches_cleaned = matches_cleaned.merge(local_goals, left_on='id', right_index=True, how='left')
    matches_cleaned = matches_cleaned.merge(visitor_goals, left_on='id', right_index=True, how='left')

    # Eliminar las comillas de las listas de minutos
    def clean_minute_list(value):
        if isinstance(value, list):
            return ','.join(map(str, value))
        return value

    matches_cleaned['local_minute_goals'] = matches_cleaned['local_minute_goals'].apply(clean_minute_list)
    matches_cleaned['visitor_minute_goals'] = matches_cleaned['visitor_minute_goals'].apply(clean_minute_list)

    # Transformar estadísticas para tener columnas por stat_type
    stats_pivot = statistics_cleaned.pivot(index='match_id', columns='stat_type', values=['local_value', 'visitor_value'])
    stats_pivot.columns = ['_'.join(col).strip() for col in stats_pivot.columns.values]  # Aplanar columnas jerárquicas
    stats_pivot.reset_index(inplace=True)

    # Unificar estadísticas con partidos
    matches_cleaned = matches_cleaned.merge(stats_pivot, left_on='id', right_on='match_id', how='left')

    # Eliminar columnas redundantes
    matches_cleaned.drop(columns=['match_id'], inplace=True, errors='ignore')

    # Eliminar columnas duplicadas para goles
    if 'local_score' in matches_cleaned.columns and 'visitor_score' in matches_cleaned.columns:
        matches_cleaned = matches_cleaned.drop(columns=['local_score', 'visitor_score'], errors='ignore')

    # Crear carpeta de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Guardar dataset procesado
    matches_cleaned.to_csv(output_path, index=False)


# Ejemplo de uso
matches_path = "data/raw/matches.csv"
statistics_path = "data/raw/statistics.csv"
events_path = "data/raw/events.csv"
output_path = "data/processed/processed_data.csv"

preprocess_football_data(matches_path, statistics_path, events_path, output_path)
