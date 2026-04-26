import requests
from config import Config

def get_verse_of_day():
    try:
        response = requests.get(Config.BIBLE_API_URL)
        if response.status_code == 200:
            data = response.json()
            verse = data['verse']['details']
            return {
                'text': verse['text'],
                'reference': verse['reference']
            }
        return None
    except Exception as e:
        print(f"Bible API error: {e}")
        return None