from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from datetime import date, datetime
import os
from jobs.pipelines.sleep_etl import DailySleep
from jobs.pipelines.readiness_etl import DailyReadiness

load_dotenv()

engine = create_engine(os.getenv("DOCKER_DATABASE_URI"))
Session = sessionmaker(bind=engine)

def query_from_db(type_of_data: str, params: dict = None, retries: int = 3) -> dict:
    table = {
        "sleep": DailySleep,
        "readiness": DailyReadiness
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