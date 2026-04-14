from sqlalchemy import Date, Integer, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import date, datetime


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
