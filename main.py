import logging
import time
from src.db import init_db, upsert_matches_weather
from src.extract import fetch_matches, fetch_weather
from src.transform import transform_matches_and_weather

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def run_pipeline():
    start_time = time.time()
    logger.info("Старт ETL-пайплайна сбора матчей и погоды РПЛ")

    # 1. Инициализация таблицы в БД
    logger.info("1/4. Проверка и создание таблицы public.rpl_matches_weather...")
    init_db()

    # 2. Extract: Получение списка матчей
    logger.info("2/4. Загрузка матчей из API...")
    matches_raw = fetch_matches()
    if not matches_raw:
        logger.warning("Список матчей пуст. Завершение работы пайплайна.")
        return

    # 3. Transform: Обогащение матчей погодой и формирование DataFrame
    logger.info(f"3/4. Обработка {len(matches_raw)} матчей и сбор погоды...")
    df = transform_matches_and_weather(matches_raw, fetch_weather)
    if df.empty:
        logger.warning("Датафрейм пуст после трансформации. Загрузка в БД отменена.")
        return

    # 4. Load: Загрузка/обновление данных в PostgreSQL (Upsert)
    logger.info("4/4. Сохранение данных в PostgreSQL...")
    saved_count = upsert_matches_weather(df)

    elapsed = round(time.time() - start_time, 2)
    logger.info(f"Пайплайн завершен за {elapsed} сек. Сохранено/обновлено записей: {saved_count}")


if __name__ == "__main__":
    run_pipeline()