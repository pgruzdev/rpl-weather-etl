# RPL Weather ETL Pipeline

Автоматизированный ETL-пайплайн для сбора, обогащения и анализа погодных условий на матчах Российской Премьер-Лиги (РПЛ) сезона 2024/2025. Проект извлекает расписание матчей через API, запрашивает почасовую погоду на момент каждой игры, сохраняет нормализованные данные в PostgreSQL и строит аналитические визуализации.

## Содержание
- [Требования](#требования)
- [Установка](#установка)
- [Настройка базы данных](#настройка-базы-данных)
- [Запуск пайплайна](#запуск-пайплайна)
- [Jupyter Notebook](#jupyter-notebook)
- [Результаты анализа](#результаты-анализа)

## Требования
- Python 3.10+
- PostgreSQL 12+
- pip

## Установка
1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/pgruzdev/rpl-weather-etl.git
cd rpl-weather-etl
```

2. **Создайте и активируйте виртуальное окружение:**
```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

## Настройка базы данных
1. **Создайте файл конфигурации:**
```bash
cp .env.example .env
```

2. **Заполните `.env` данными вашей БД:**
```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rpl_weather_db
```

3. **Создайте базу данных в PostgreSQL:**
```sql
CREATE DATABASE rpl_weather_db;
```

## Запуск пайплайна
```bash
# 1. Выполнение ETL-пайплайна
python main.py

# 2. Запуск аналитики и генерация графиков
python src/analytics.py
```

## Jupyter Notebook
Для интерактивного анализа и пошагового выполнения запросов:
```bash
jupyter notebook src/analytics.ipynb
```

## Результаты анализа
Скрипт `analytics.py` выводит в консоль отформатированные таблицы и сохраняет графики в папку `plots/`:
- `average_season_temp.png` — график средней температуры по временам года
- `weather_conditions_share.png` — доля различных погодных условий в матчах
