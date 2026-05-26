import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FOOTBALL_API_KEY")
URL = "https://v3.football.api-sports.io/fixtures"
headers = {'x-apisports-key': API_KEY}
querystring = {"league": "235", "season": "2024", "timezone": "Europe/Moscow"}

def fetch_raw_matches():
    """
    Запрашивает данные у API и сохраняет сырой JSON-файл с матчами
    """
    try:
        response = requests.get(URL, headers=headers, params=querystring, timeout=10)
        response.raise_for_status() 
        data = response.json()
        results_count = data.get("results", 0)
        print(f"Успешно получено матчей от API: {results_count}")
        os.makedirs("data/raw", exist_ok=True)
        output_path = "data/raw/rpl_fixtures_2024.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)    
        print(f"Файл успешно сохранен в: {output_path}")
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ошибка (код статуса): {http_err}")
    except Exception as err:
        print(f"Произошла непредвиденная ошибка: {err}")

if __name__ == "__main__":
    fetch_raw_matches()
