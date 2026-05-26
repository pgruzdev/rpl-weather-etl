import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
input_path = "data/processed/rpl_ready_for_postgres.csv"

def load_csv_to_postgres():
    """
    Автоматически считывает очищенный датасет и записывает его 
    в реляционную базу данных PostgreSQL, заменяя старые данные.
    """
    df = pd.read_csv(input_path)
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    engine = create_engine(db_url)
    df.to_sql(
        name="rpl_matches_weather", 
        con=engine, 
        if_exists="replace", 
        index=False
    )
    
    print("Готово")
if __name__ == "__main__":
    load_csv_to_postgres()