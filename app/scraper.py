import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_nba_stats():
    url = "https://www.basketball-reference.com/leagues/NBA_2025_per_game.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    table = soup.find('table', id='per_game_stats')
    df = pd.read_html(str(table))[0]
    df = df[df['Player'] != 'Player']  # Remove header repeats
    return df.to_dict(orient='records')