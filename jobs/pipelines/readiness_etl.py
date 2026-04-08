from sqlalchemy import create_engine, Date, Integer, DateTime, Float, func
from sqlalchemy.orm import Mapped, Session, mapped_column, DeclarativeBase, sessionmaker
from services.oura_service import param_builder
from services.oura_service import fetch_oura_data
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DOCKER_DATABASE_URI"))

class Base(DeclarativeBase):
    pass

class RawDailyReadiness(Base):
    __tablename__ = "raw_daily_readiness"

    # root fields
    id: Mapped[str] = mapped_column(primary_key=True)
    day: Mapped[date] = mapped_column(Date)
    score: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    temperature_deviation: Mapped[Float] = mapped_column(Float, nullable=True)
    temperature_trend_deviation: Mapped[Float] = mapped_column(Float, nullable=True)

    # contributors (flattened)
    activity_balance: Mapped[int] = mapped_column(Integer, nullable=True)
    body_temperature: Mapped[int] = mapped_column(Integer, nullable=True)
    hrv_balance: Mapped[int] = mapped_column(Integer, nullable=True)
    previous_day_activity: Mapped[int] = mapped_column(Integer, nullable=True)
    previous_night: Mapped[int] = mapped_column(Integer, nullable=True)
    recovery_index: Mapped[int] = mapped_column(Integer, nullable=True)
    resting_heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    sleep_balance: Mapped[int] = mapped_column(Integer, nullable=True)
    sleep_regularity: Mapped[int] = mapped_column(Integer, nullable=True)

class DailyReadiness(Base):

    __tablename__ = "daily_readiness"
    # same fields from raw data
    id: Mapped[str] = mapped_column(primary_key=True)
    day: Mapped[date] = mapped_column(Date)
    score: Mapped[int] = mapped_column(Integer)

    # contributors (flattened)
    activity_balance: Mapped[int] = mapped_column(Integer)
    body_temperature: Mapped[int] = mapped_column(Integer)
    hrv_balance: Mapped[int] = mapped_column(Integer)
    previous_day_activity: Mapped[int] = mapped_column(Integer)
    previous_night: Mapped[int] = mapped_column(Integer)
    recovery_index: Mapped[int] = mapped_column(Integer)
    resting_heart_rate: Mapped[int] = mapped_column(Integer)
    sleep_balance: Mapped[int] = mapped_column(Integer)
    sleep_regularity: Mapped[int] = mapped_column(Integer)
    temperature_deviation: Mapped[Float] = mapped_column(Float)

    # custom fields
    vitality_score: Mapped[int] = mapped_column(Integer)
    alertness_index: Mapped[int] = mapped_column(Integer)
    resilience_score: Mapped[int] = mapped_column(Integer)
    balance_quotient: Mapped[int] = mapped_column(Integer)
    recovery_potential: Mapped[int] = mapped_column(Integer)

Base.metadata.create_all(engine)

def fetch_and_extract():
    """Extract raw data form Oura API requests and save into local db"""
    def save_raw_data(session: Session, data: dict):
        for d in data["data"]:
            contributors = d.get("contributors", {})
            dailyreadiness_obj = {
                "id": d.get("id"),
                "day": d.get("day"),
                "score": d.get("score"),
                "timestamp": d.get("timestamp"),
                "temperature_deviation": d.get("temperature_deviation"),
                "temperature_trend_deviation": d.get("temperature_trend_deviation") ,
                "activity_balance": contributors.get("activity_balance"),
                "body_temperature": contributors.get("body_temperature"),
                "hrv_balance": contributors.get("hrv_balance"),
                "previous_day_activity": contributors.get("previous_day_activity"),
                "previous_night": contributors.get("previous_night"),
                "recovery_index": contributors.get("recovery_index"),
                "resting_heart_rate": contributors.get("resting_heart_rate"),
                "sleep_balance": contributors.get("sleep_balance"),
                "sleep_regularity": contributors.get("sleep_regularity")
            }
            new_dailyreadiness_record = RawDailyReadiness(**dailyreadiness_obj)
            session.merge(new_dailyreadiness_record)

        session.commit()

    Session = sessionmaker(bind=engine)

    with Session() as session:
                
        # start_of_history = date(2024, 12, 1)
        # current_start = start_of_history
        # end_of_history = date.today()
        current_start = session.query(func.max(RawDailyReadiness.day)).scalar()
        end_of_history = date.today()

        while current_start < end_of_history:
            current_end = current_start + relativedelta(months=1) - relativedelta(days=1)
            params = param_builder(start_date=current_start, end_date=current_end)
            # print(params)
            try:
                data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_readiness", params=params)
                save_raw_data(session, data)
            except Exception as e:
                print(e)

            current_start += relativedelta(months=1)

        session.commit()

def transform_and_load():
    """Transforms raw data from RawDailyReadiness table and loads it into a new table"""

    Session = sessionmaker(bind=engine)

    with Session() as session:

        # start_of_history = date(2024, 12, 1)
        # current_start = start_of_history
        
        current_start = session.query(func.max(RawDailyReadiness.day)).scalar()
        end_of_history = date.today()

    while current_start < end_of_history:
        current_end = current_start + relativedelta(months=1) - relativedelta(days=1)

        try:
            data = session.query(RawDailyReadiness).filter(RawDailyReadiness.day >= current_start, RawDailyReadiness.day <= current_end).all()

            for d in data:

                temperature_deviation = d.temperature_deviation or 70
                activity_balance = d.activity_balance or 70
                body_temperature = d.body_temperature or 70
                hrv_balance = d.hrv_balance or 70
                previous_day_activity = d.previous_day_activity or 70
                previous_night = d.previous_night or 70
                recovery_index = d.recovery_index or 70
                resting_heart_rate = d.resting_heart_rate or 70
                sleep_balance = d.sleep_balance or 70
                sleep_regularity = d.sleep_regularity or 70

                vitality_score = (
                    0.25 * hrv_balance +
                    0.20 * resting_heart_rate +
                    0.15 * body_temperature +
                    0.10 * temperature_deviation +
                    0.10 * activity_balance +
                    0.10 * sleep_balance +
                    0.10 * sleep_regularity
                )
                alertness_index = (
                    0.30 * previous_night +
                    0.25 * previous_day_activity +
                    0.20 * sleep_regularity +
                    0.15 * activity_balance +
                    0.10 * hrv_balance
                )
                resilience_score = (
                    0.30 * recovery_index +
                    0.20 * hrv_balance +
                    0.15 * resting_heart_rate +
                    0.15 * temperature_deviation +
                    0.10 * previous_day_activity +
                    0.10 * activity_balance
                )
                balance_quotient = (
                    0.25 * sleep_balance +
                    0.20 * sleep_regularity +
                    0.15 * activity_balance +
                    0.15 * previous_day_activity +
                    0.15 * hrv_balance +
                    0.10 * body_temperature
                )
                recovery_potential = (
                    0.25 * previous_night +
                    0.20 * recovery_index +
                    0.20 * hrv_balance +
                    0.15 * activity_balance +
                    0.10 * resting_heart_rate +
                    0.10 * previous_day_activity
                )
                
                readiness_data = {
                    "id": d.id,
                    "day": d.day,
                    "score": d.score,
                    "temperature_deviation": d.temperature_deviation or 70,
                    "activity_balance": d.activity_balance or 0,
                    "body_temperature": d.body_temperature or 0,
                    "hrv_balance": d.hrv_balance or 0,
                    "previous_day_activity": d.previous_day_activity or 0,
                    "previous_night": d.previous_night or 0,
                    "recovery_index": d.recovery_index or 0,
                    "resting_heart_rate": d.resting_heart_rate or 0,
                    "sleep_balance": d.sleep_balance or 0,
                    "sleep_regularity": d.sleep_regularity or 0,
                    "vitality_score": vitality_score,
                    "alertness_index": alertness_index,
                    "resilience_score": resilience_score,
                    "balance_quotient": balance_quotient,
                    "recovery_potential": recovery_potential
                }
                pass

                transformed_data = DailyReadiness(**readiness_data)
                session.merge(transformed_data)

            session.commit()

        except Exception as e:
            print(e)

        current_start += relativedelta(months=1)

def run_dailyreadiness_pipeline():
    fetch_and_extract()
    transform_and_load()

if __name__ == "__main__":
    run_dailyreadiness_pipeline()