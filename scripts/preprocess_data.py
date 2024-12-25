import pandas as pd
from database import query_matches

def preprocess_data():
    matches = query_matches()
    df = pd.DataFrame(matches, columns=['id', 'league', 'local_team', 'visitor_team', 'local_score', 'visitor_score', 'match_date'])
    df.to_csv('data/processed/matches.csv', index=False)

if __name__ == '__main__':
    preprocess_data()
