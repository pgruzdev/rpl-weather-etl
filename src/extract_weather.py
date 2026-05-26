import os
import time
import pandas as pd
import requests
from datetime import date

input_path = "data/processed/rpl_matches_clean.csv"
output_path = "data/raw/rpl_weather_raw.csv"

def get_weather_description(code):
    """
    Переводит коды WMO в соответствующие погодные условия
    """
    if code == 0:
        return "Ясно"
    elif code in [1, 2, 3]:
        return "Облачно"
    elif code in [45, 48]:
        return "Туман"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "Дождь"
    elif code in [71, 73, 75, 77, 85, 86]:
        return "Снег"
    elif code in [95, 96, 99]:
        return "Гроза"
    return "Облачно"

def fetch_weather():
    """
    Берет каждый матч из rpl_matches_clean.csv, подставляет
    город и координаты и запрашивает погоду в указанной геоточке
    во время начала матча
    """
    coordinates = {
        "Moscow": {"lat": 55.7558, "lon": 37.6173},
        "Saint Petersburg": {"lat": 59.9343, "lon": 30.3351},
        "Krasnodar": {"lat": 45.0355, "lon": 38.9753},
        "Rostov-na-Donu": {"lat": 47.2221, "lon": 39.7188},
        "Samara": {"lat": 53.2001, "lon": 50.15},
        "Kazan": {"lat": 55.7887, "lon": 49.1221},
        "Nizhny Novgorod": {"lat": 56.3269, "lon": 44.0059},
        "Ekaterinburg": {"lat": 56.8389, "lon": 60.6057},
        "Voronezh": {"lat": 51.672, "lon": 39.1843},
        "Grozny": {"lat": 43.3171, "lon": 45.6967},
        "Makhachkala": {"lat": 42.9764, "lon": 47.5024},
        "Tula": {"lat": 54.1961, "lon": 37.6182},
        "Khimki": {"lat": 55.8887, "lon": 37.4412},
        "Orenburg": {"lat": 51.7681, "lon": 55.097}
    }

    df_matches = pd.read_csv(input_path)
    weather_records = []
    print(f"Матчей для обработки: {len(df_matches)}")

    session = requests.Session()
    url = "https://archive-api.open-meteo.com/v1/archive"
    for index, row in df_matches.iterrows():
        try:
            dt = pd.to_datetime(row["date_time"])
            date_str = dt.strftime("%Y-%m-%d")
            match_hour = dt.hour
            city = row["city"]
            geo = coordinates.get(city)
            params = {
                "latitude": geo["lat"],
                "longitude": geo["lon"],
                "start_date": date_str,
                "end_date": date_str,
                "hourly": ["temperature_2m", "weather_code"],
                "timezone": "Europe/Moscow"
            }

            MAX_RETRIES = 3
            data = None
            for attempt in range(MAX_RETRIES):
                try:
                    response = session.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    break
                
                except requests.exceptions.Timeout:
                    print(f"Timeout match_id={row['match_id']}, attempt={attempt + 1}")
                    time.sleep(2)

                except requests.exceptions.RequestException as e:
                    print(f"API error match_id={row['match_id']}: {e}")
                    break

            if not data:
                continue

            temperatures = data["hourly"]["temperature_2m"]
            weather_codes = data["hourly"]["weather_code"]
            temperature = temperatures[match_hour]
            weather_code = weather_codes[match_hour]
            weather_condition = get_weather_description(weather_code)

            weather_records.append({
                "match_id": row["match_id"],
                "city": city,
                "match_datetime": dt,
                "temperature": temperature,
                "weather_code": weather_code,
                "weather_condition": weather_condition
            })
            time.sleep(0.3)
        
        except Exception as e:
            print(f"Ошибка обработки match_id={row['match_id']}: {e}")
       
        if (index + 1) % 25 == 0:
            print(f"Обработано:{index + 1}/{len(df_matches)}")

    df_weather = pd.DataFrame(weather_records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_weather.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Строк записано: {len(df_weather)}")

if __name__ == "__main__":
    fetch_weather()