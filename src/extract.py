import logging
import os
from dotenv import load_dotenv
import requests

load_dotenv()

logger = logging.getLogger(__name__)

FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
FOOTBALL_API_URL = "https://v3.football.api-sports.io/fixtures"


def fetch_matches() -> list:
    """Скачивает матчи РПЛ напрямую через API-Sports."""
    if not FOOTBALL_API_KEY:
        logger.error("FOOTBALL_API_KEY не найден в переменных окружения (.env)!")
        return []

    headers = {
        "x-apisports-key": FOOTBALL_API_KEY,
    }
    params = {
        "league": "235",  # ID РПЛ в API-Sports
        "season": "2024",
        "timezone": "Europe/Moscow",
    }

    try:
        response = requests.get(
            FOOTBALL_API_URL, headers=headers, params=params, timeout=25
        )
        response.raise_for_status()

        data = response.json()

        # Проверка на внутренние ошибки API
        errors = data.get("errors")
        if errors and len(errors) > 0:
            logger.error(f"Ошибка API-Sports: {errors}")
            return []

        fixtures = data.get("response", [])
        logger.info(f"Успешно скачано {len(fixtures)} матчей через API.")
        return fixtures

    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка при скачивании матчей: {e}")
        return []


def fetch_weather(lat: float, lon: float, date_str: str) -> dict:
    """Получает почасовую погоду из Open-Meteo на указанные координаты и дату."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date_str,
        "end_date": date_str,
        "hourly": ["temperature_2m", "weather_code"],
        "timezone": "Europe/Moscow",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Ошибка запроса погоды (lat={lat}, lon={lon}, date={date_str}): {e}"
        )
        return {}