import requests
from bs4 import BeautifulSoup
from database import insert_match, insert_event

def scrape_data():
    # Aquí va la lógica para scrapear los datos de la web
    # Suponiendo datos de ejemplo:
    match_data = {
        "league": "Esoccer Battle - 8 mins play",
        "local_team": "Lyon (cl1vlind)",
        "visitor_team": "Lille (Senior)",
        "local_score": 1,
        "visitor_score": 4,
        "match_date": "2024-12-25 15:16"
    }
    insert_match(**match_data)
    
    events = [
        {"match_id": 1, "event_type": "Corner", "minute": 2, "team": "visitor"},
        {"match_id": 1, "event_type": "Goal", "minute": 2, "team": "visitor"}
    ]
    for event in events:
        insert_event(**event)

if __name__ == '__main__':
    scrape_data()
