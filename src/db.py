import os
import logging
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

logger = logging.getLogger(__name__)


def get_db_engine():
    """Создает и возвращает подключение SQLAlchemy Engine к PostgreSQL."""
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(database_url)


def init_db():
    """Создает таблицу public.rpl_matches_weather с правильными типами данных."""
    engine = get_db_engine()

    ddl_query = """
    CREATE TABLE IF NOT EXISTS public.rpl_matches_weather (
        match_id BIGINT PRIMARY KEY,
        season VARCHAR(20) NOT NULL,
        date_time TIMESTAMPTZ NOT NULL,
        city VARCHAR(100) NOT NULL,
        stadium VARCHAR(150),
        home_team VARCHAR(100) NOT NULL,
        away_team VARCHAR(100) NOT NULL,
        temperature NUMERIC(4, 1),
        weather_code INT,
        weather_condition VARCHAR(100)
    );
    """

    with engine.begin() as conn:
        conn.execute(text(ddl_query))
        logger.info("Таблица public.rpl_matches_weather проверена / создана.")


def upsert_matches_weather(df: pd.DataFrame) -> int:
    """Загружает DataFrame в PostgreSQL с защитой от дубликатов (Upsert)."""
    if df.empty:
        logger.warning("DataFrame пуст, загрузка отменена.")
        return 0

    engine = get_db_engine()

    upsert_query = """
    INSERT INTO public.rpl_matches_weather (
        match_id, season, date_time, city, stadium,
        home_team, away_team, temperature, weather_code, weather_condition
    )
    VALUES (
        :match_id, :season, :date_time, :city, :stadium,
        :home_team, :away_team, :temperature, :weather_code, :weather_condition
    )
    ON CONFLICT (match_id) DO UPDATE SET
        season = EXCLUDED.season,
        date_time = EXCLUDED.date_time,
        city = EXCLUDED.city,
        stadium = EXCLUDED.stadium,
        home_team = EXCLUDED.home_team,
        away_team = EXCLUDED.away_team,
        temperature = EXCLUDED.temperature,
        weather_code = EXCLUDED.weather_code,
        weather_condition = EXCLUDED.weather_condition;
    """

    records = df.to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(text(upsert_query), records)
        logger.info(f"Успешно сохранено/обновлено {len(records)} записей в БД.")

    return len(records)