from sqlalchemy import create_engine, DateTime, Date, Integer, String, func
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, sessionmaker, Session
from dotenv import load_dotenv
from typing import List, Dict
from datetime import date, datetime
import os
from services.oura_service import fetch_oura_data 
from dateutil.relativedelta import relativedelta

load_dotenv()

engine = create_engine(os.getenv("DOCKER_DATABASE_URI"))

class Base(DeclarativeBase):
    pass

class RawDailySleep(Base):
    __tablename__ = "raw_daily_sleep"

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

class DailySleep(Base):
    __tablename__ = "daily_sleep"

    # same fields from raw data
    id: Mapped[str] = mapped_column(String, primary_key=True)
    day: Mapped[date] = mapped_column(Date)
    score: Mapped[int] = mapped_column(Integer)

    # contributors (flattened)
    deep_sleep: Mapped[int] = mapped_column(Integer)
    efficiency: Mapped[int] = mapped_column(Integer)
    latency: Mapped[int] = mapped_column(Integer)
    rem_sleep: Mapped[int] = mapped_column(Integer)
    restfulness: Mapped[int] = mapped_column(Integer)
    timing: Mapped[int] = mapped_column(Integer)
    total_sleep: Mapped[int] = mapped_column(Integer)

    # custom fields
    performance_score: Mapped[int] = mapped_column(Integer)
    recovery_score : Mapped[int] = mapped_column(Integer)
    consistency_score: Mapped[int] = mapped_column(Integer)
    custom_score: Mapped[int] = mapped_column(Integer)

# creates tables in sql from python objects 
Base.metadata.create_all(engine)

def param_builder(start_date: date, end_date: date) -> dict:
    return {
        "start_date": start_date,
        "end_date": end_date
    }

def fetch_and_extract():
    """Extract Raw Data From Oura API requests and save it into database"""
    def save_raw_data(session: Session, data: dict):

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

            new_dailysleep_record = RawDailySleep(**dailysleep_obj)
            session.merge(new_dailysleep_record) # merge checks if the primary key already exists, if it does, it updates it, if not it adds it. better than session.add() which can cause duplicate primary key if ran more than once. 

        session.commit()

    # start_of_history = date(2024, 12, 1)
    # current_start = start_of_history
    # end_of_history = date.today()
    
    Session = sessionmaker(bind=engine)

    with Session() as session:

        current_start = session.query(func.max(RawDailySleep.day)).scalar()
        end_of_history = date.today()

        while current_start < end_of_history:
            current_end = current_start + relativedelta(months=1) - relativedelta(days=1)
            params = param_builder(start_date=current_start, end_date=current_end)
            print(params)
            try:
                data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_sleep", params=params)
                save_raw_data(session, data)
            except Exception as e:
                print(e)

            current_start += relativedelta(months=1)

# transform raw sleep data, remove certain fields, add fields, etc and load into postgresql database
def transform_and_load():
    """Transforms Raw Data from RawDailySleep table and loads it into a new table"""
    Session = sessionmaker(bind=engine)

    # start_of_history = date(2024, 12, 1)
    # current_start = start_of_history
    # end_of_history = date.today()

    with Session() as session:
        current_start = session.query(func.max(RawDailySleep.day)).scalar()
        end_of_history = date.today()

    while current_start < end_of_history:
        current_end = current_start + relativedelta(months=1) - relativedelta(days=1)

        with Session() as session:

            try:
                data = session.query(RawDailySleep).filter(RawDailySleep.day >= current_start, RawDailySleep.day <= current_end).all()

                for d in data:
                    # formulas
                    performance_score = (0.25 * d.rem_sleep) + (0.20 * d.efficiency) + (0.20 * d.latency) + (0.15 * d.total_sleep) + (0.10 * d.deep_sleep) + (0.10 * d.timing)

                    recovery_score = (0.30 * d.deep_sleep) + (0.25 * d.total_sleep) + (0.15 * d.restfulness) + (0.10 * d.efficiency) + (0.10 * d.rem_sleep) + (0.10 * d.timing)

                    consistency_score = (0.35 * d.timing) + (0.25 * d.latency) + (0.20 * d.efficiency) + (0.10 * d.restfulness) + (0.10 * d.total_sleep)

                    custom_score = (0.25 * d.total_sleep) + (0.20 * d.rem_sleep) + (0.20 * d.efficiency) + (0.15 * d.latency) + (0.1 * d.deep_sleep) + (0.10 * d.timing)

                    # transformed data obj
                    sleep_data = {

                        # fields from raw data
                        "id": d.id,
                        "day": d.day,
                        "score": d.score,
                        "deep_sleep": d.deep_sleep,
                        "efficiency": d.efficiency,
                        "latency": d.latency,
                        "rem_sleep": d.rem_sleep,
                        "restfulness": d.restfulness,
                        "timing": d.timing,
                        "total_sleep": d.total_sleep,

                        # custom fields
                        "performance_score": round(performance_score),
                        "recovery_score": round(recovery_score),
                        "consistency_score": round(consistency_score),
                        "custom_score": round(custom_score)
                    }

                    transformed_data = DailySleep(**sleep_data)
                    session.merge(transformed_data)
                session.commit()

            except Exception as e:
                print(e)

        current_start += relativedelta(months=1)


# etl pipeline (run dailly pipeline)
def run_daily_pipeline():
    try:
        fetch_and_extract()
    except Exception as e:
        return
    try:
        transform_and_load()
    except Exception as e:
        return

if __name__ == "__main__":
    run_daily_pipeline()