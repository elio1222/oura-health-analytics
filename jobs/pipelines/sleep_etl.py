from sqlalchemy import create_engine, DateTime, Date, Integer, String
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, sessionmaker, Session
from dotenv import load_dotenv
from typing import List, Dict
from datetime import date, datetime
import os
from services.oura_service import fetch_oura_data 
from dateutil.relativedelta import relativedelta
import json
import logging

load_dotenv()

logger = logging.getLogger(__name__)


# sqlalchemy magic

engine = create_engine(os.getenv("DATABASE_URI"))

class Base(DeclarativeBase):
    pass

class DailySleep(Base):
    __tablename__ = "daily_sleep"

    # root fields
    id: Mapped[str] = mapped_column(primary_key=True)
    day: Mapped[date] = mapped_column(Date)
    score: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # contributors (flattened)
    deep_sleep: Mapped[int] = mapped_column(Integer)
    efficiency: Mapped[int] = mapped_column(Integer)
    latency: Mapped[int] = mapped_column(Integer)
    rem_sleep: Mapped[int] = mapped_column(Integer)
    restfulness: Mapped[int] = mapped_column(Integer)
    timing: Mapped[int] = mapped_column(Integer) 
    total_sleep: Mapped[int] = mapped_column(Integer)

# creates tables in sql from python objects 
Base.metadata.create_all(engine)

def param_builder(start_date: date, end_date: date) -> dict:
    return {
        "start_date": start_date,
        "end_date": end_date
    }

# get raw sleep data from oura api and save raw data into postgresql
"""Extract Raw Data From Oura API requests and save it into database"""
def main():
    def fetch_and_save_dailysleep():

        # Session = sessionmaker(bind=engine)
        # session = Session()

        def extract_data(session: Session, data: dict):

            logging.info("inside extract data function")

            for d in data["data"]:
                contributors = d.get("contributors", {})
                dailysleep_obj = {
                    "id": d.get("id"),
                    "day": d.get("day"),
                    "score": d.get("score"),
                    "timestamp": d.get("timestamp"),
                    "deep_sleep": contributors.get("deep_sleep"),
                    "efficiency": contributors.get("efficiency"),
                    "latency": contributors.get("latency"),
                    "rem_sleep": contributors.get("rem_sleep"),
                    "restfulness": contributors.get("restfulness"),
                    "timing": contributors.get("timing"),
                    "total_sleep": contributors.get("total_sleep")
                }

                new_dailysleep_record = DailySleep(**dailysleep_obj)
                session.merge(new_dailysleep_record) # merge checks if the primary key already exists, if it does, it updates it, if not it adds it. better than session.add() which can cause duplicate primary key if ran more than once. 

            pass

        start_of_history = date(2026, 4, 1)
        current_start = start_of_history
        end_of_history = date.today()

        while current_start < end_of_history:
            current_end = current_start + relativedelta(months=1) - relativedelta(days=1)
            
            params = param_builder(start_date=current_start, end_date=current_end)

            logging.info(f"Parameters testing: {params}")


            try:
                data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_sleep", params=params)

                logging.info("data is fine")

                Session = sessionmaker(bind=engine)
                session = Session()

                extract_data(session, data)

                session.commit()

                logging.info("extract_data was successful")



            except Exception as e:
                logging.info(e)
                logging.info(f"{params} failed")

            current_start += relativedelta(months=1)


    fetch_and_save_dailysleep()





# transform raw sleep data, remove certain fields, add fields, etc

# load to postgresql database

if __name__ == "__main__":
    logging.basicConfig(filename="sleep_etl.log", level=logging.INFO)
    logging.info("Starting main")
    main()
    logging.info("success")