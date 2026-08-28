import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

# Справочник стадионов, городов и координат клубов РПЛ под ваш JSON
CLUBS_INFO = {
    "Zenit": {"city": "Санкт-Петербург", "stadium": "Газпром Арена", "lat": 59.9727, "lon": 30.2214},
    "Spartak Moscow": {"city": "Москва", "stadium": "Лукойл Арена", "lat": 55.8180, "lon": 37.4404},
    "CSKA Moscow": {"city": "Москва", "stadium": "ВЭБ Арена", "lat": 55.7915, "lon": 37.5165},
    "FC Krasnodar": {"city": "Краснодар", "stadium": "Стадион ФК Краснодар", "lat": 45.0442, "lon": 39.0287},
    "Dynamo": {"city": "Москва", "stadium": "ВТБ Арена", "lat": 55.7915, "lon": 37.5598},
    "Lokomotiv": {"city": "Москва", "stadium": "РЖД Арена", "lat": 55.8036, "lon": 37.7410},
    "FC Rostov": {"city": "Ростов-на-Дону", "stadium": "Ростов Арена", "lat": 47.2096, "lon": 39.7378},
    "Rubin": {"city": "Казань", "stadium": "Ак Барс Арена", "lat": 55.8179, "lon": 49.1578},
    "Krylia Sovetov": {"city": "Самара", "stadium": "Солидарность Самара Арена", "lat": 53.2780, "lon": 50.2374},
    "Akhmat": {"city": "Грозный", "stadium": "Ахмат Арена", "lat": 43.3236, "lon": 45.7447},
    "Nizhny Novgorod": {"city": "Нижний Новгород", "stadium": "Стадион Нижний Новгород", "lat": 56.3328, "lon": 43.9639},
    "Fakel": {"city": "Воронеж", "stadium": "Факел", "lat": 51.6669, "lon": 39.2063},
    "FC Orenburg": {"city": "Оренбург", "stadium": "Газовик", "lat": 51.7950, "lon": 55.2010},
    "Khimki": {"city": "Химки", "stadium": "Арена Химки", "lat": 55.8864, "lon": 37.4542},
    "Dinamo Makhachkala": {"city": "Каспийск", "stadium": "Анжи Арена", "lat": 42.9009, "lon": 47.5818},
    "Akron": {"city": "Самара", "stadium": "Солидарность Самара Арена", "lat": 53.2780, "lon": 50.2374},
}


def get_season_name(date_time_obj: datetime) -> str:
    """Определяет время года по номеру месяца."""
    month = date_time_obj.month
    if month in [12, 1, 2]:
        return "Зима"
    elif month in [3, 4, 5]:
        return "Весна"
    elif month in [6, 7, 8]:
        return "Лето"
    else:
        return "Осень"


def get_weather_description(code: int) -> str:
    """Определяет погоду по коду через условия."""
    if code is None:
        return "Неизвестно"
    code = int(code)
    if code in [0, 1]:
        return "Ясно"
    elif code in [2, 3]:
        return "Пасмурно"
    elif code in [45, 48]:
        return "Туман"
    elif (51 <= code <= 67) or (80 <= code <= 82):
        return "Дождь"
    elif (71 <= code <= 77) or (85 <= code <= 86):
        return "Снег"
    elif code in [95, 96, 99]:
        return "Гроза"
    else:
        return "Облачно"


def find_hourly_weather(weather_json: dict, match_dt: datetime) -> tuple:
    """Находит температуру и код погоды на час матча."""
    if not weather_json or "hourly" not in weather_json:
        return None, None

    hourly = weather_json["hourly"]
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    codes = hourly.get("weather_code", [])

    match_hour_str = match_dt.strftime("%Y-%m-%dT%H:00")
    if match_hour_str in times:
        idx = times.index(match_hour_str)
        return temps[idx], codes[idx]

    if temps and codes:
        return temps[12], codes[12]
    return None, None


def transform_matches_and_weather(matches_raw: list, weather_fetcher_func) -> pd.DataFrame:
    """Соединяет матчи с погодой и формирует чистый DataFrame."""
    transformed_records = []

    for item in matches_raw:
        fixture_data = item.get("fixture", {})
        match_id = fixture_data.get("id")
        date_str = fixture_data.get("date")

        if not match_id or not date_str:
            continue

        match_dt = datetime.fromisoformat(date_str)
        season = get_season_name(match_dt)

        teams_data = item.get("teams", {})
        home_team_name = teams_data.get("home", {}).get("name", "Неизвестно")
        away_team_name = teams_data.get("away", {}).get("name", "Неизвестно")

        club_info = CLUBS_INFO.get(home_team_name, {
            "city": "Не указан",
            "stadium": "Не указан",
            "lat": 55.5555,
            "lon": 37.7777
        })

        city = club_info["city"]
        stadium = club_info["stadium"]

        date_only_str = match_dt.strftime("%Y-%m-%d")
        weather_raw = weather_fetcher_func(club_info["lat"], club_info["lon"], date_only_str)

        temperature, weather_code = find_hourly_weather(weather_raw, match_dt)
        weather_condition = get_weather_description(weather_code)

        transformed_records.append({
            "match_id": match_id,
            "season": season,
            "date_time": match_dt,
            "city": city,
            "stadium": stadium,
            "home_team": home_team_name,
            "away_team": away_team_name,
            "temperature": temperature,
            "weather_code": weather_code,
            "weather_condition": weather_condition
        })

    df = pd.DataFrame(transformed_records)
    logger.info(f"Трансформация завершена. Подготовлено записей: {len(df)}")
    return df