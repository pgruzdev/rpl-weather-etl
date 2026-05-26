import os
import pandas as pd
from datetime import datetime

def get_season(date_str):
    """
    Возвращает название месяца по его номеру
    """
    dt = datetime.fromisoformat(date_str)
    month = dt.month
    if month in [12, 1, 2]:
        return "Зима"
    elif month in [3, 4, 5]:
        return "Весна"
    elif month in [6, 7, 8]:
        return "Лето"
    elif month in [9, 10, 11]:
        return "Осень"
    return "Неизвестно"

def merge_matches_and_weather():
    """
    Объединение погоды с матчами
    """
    matches_path = "data/processed/rpl_matches_clean.csv"
    weather_path = "data/raw/rpl_weather_raw.csv"
    output_path = "data/processed/rpl_ready_for_postgres.csv"

    df_matches = pd.read_csv(matches_path)
    df_weather = pd.read_csv(weather_path)
    df_final = pd.merge(df_matches, df_weather, on="match_id", how="inner")
    df_final = df_final.rename(columns={"city_x": "city"})
    df_final = df_final.drop(columns=["city_y", "match_datetime"], errors="ignore")
    df_final["season"] = df_final["date_time"].apply(get_season)

    os.makedirs("data/processed", exist_ok=True)
    df_final.to_csv(output_path, index=False, encoding="utf-8")
    print(df_final.head(3))

if __name__ == "__main__":
    merge_matches_and_weather()
