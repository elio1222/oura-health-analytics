from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from datetime import date, datetime
import os
from app.models.models import DailySleep, DailyReadiness, DailyStress, SleepRoute

load_dotenv()

import os

def get_database_uri():
    # If running inside Docker, override automatically
    if os.path.exists("/.dockerenv"):
        return os.getenv(
            "DOCKER_DATABASE_URI",
            os.getenv("DATABASE_URI")
        )
    return os.getenv("DATABASE_URI")


engine = create_engine(get_database_uri())

Session = sessionmaker(bind=engine)

def query_from_db(type_of_data: str, params: dict = None, retries: int = 3) -> dict:
    table = {
        "sleep": DailySleep,
        "readiness": DailyReadiness,
        "stress": DailyStress,
        "sleep_route": SleepRoute 
    }
    for _ in range(retries):
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        
        with Session() as session:
            try:
                DataObj = table.get(type_of_data)
                data = session.query(DataObj).filter(DataObj.day >= start_date, DataObj.day <= end_date).all()
                return data
            except Exception as e:
                print(e)