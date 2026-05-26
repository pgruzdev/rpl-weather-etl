import json
import os
import pandas as pd

input_path = "data/raw/rpl_fixtures_2024.json"
output_path = "data/processed/rpl_matches_clean.csv"

def transform_fixtures():
    """
    Извлекает из JSON нужные данные (id, дату, команды...) 
    по ключу response
    """
    with open(input_path, "r", encoding="utf-8") as file:
        payload = json.load(file)
    fixtures_list = payload.get("response", [])
    processed_records = []
    for match in fixtures_list:
        fixture = match.get("fixture", {})
        match_id = fixture.get("id")
        date_time = fixture.get("date")
        venue = fixture.get("venue", {})

        teams = match.get("teams", {})
        home_team = teams.get("home", {}).get("name")
        away_team = teams.get("away", {}).get("name")
        
        city = venue.get("city")
        stadium = venue.get("name")
        
        if not match_id or not date_time or not city:
            continue    
        processed_records.append({
            "match_id": match_id,
            "date_time": date_time,
            "city": city,
            "stadium": stadium,
            "home_team": home_team,
            "away_team": away_team
        })
        
    df = pd.DataFrame(processed_records)
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Трансформация завершена. Количество строк: {len(df)}")

if __name__ == "__main__":
    transform_fixtures()
