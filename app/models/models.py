from sqlalchemy import Date, Integer, DateTime, Float, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.dialects.postgresql import ARRAY
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

class RawDailyStress(Base):
    __tablename__ = "raw_daily_stress"

    # root fields
    id: Mapped[str] = mapped_column(String, primary_key=True)
    day: Mapped[date] = mapped_column(Date)
    day_summary: Mapped[str] = mapped_column(String, nullable=True)
    recovery_high: Mapped[int] = mapped_column(Integer, nullable=True)
    stress_high: Mapped[int] = mapped_column(Integer, nullable=True)

class DailyStress(Base):
    __tablename__ = "daily_stress"

    # same fields from raw daily stress
    id: Mapped[str] = mapped_column(String, primary_key=True)
    day: Mapped[date] = mapped_column(Date)
    day_summary: Mapped[str] = mapped_column(String, nullable=True)
    recovery_high: Mapped[int] = mapped_column(Integer, nullable=True)
    stress_high: Mapped[int] = mapped_column(Integer, nullable=True)

    # custom fields
    stress_index: Mapped[int] = mapped_column(Integer, nullable=True)
    resilience_rating: Mapped[int] = mapped_column(Integer, nullable=True)

class RawSleepRoute(Base):
    __tablename__ = "raw_sleep_routes"

    # identifiers (required)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    day: Mapped[date] = mapped_column(Date)

    # meta
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=True)

    # averages
    average_breath: Mapped[float] = mapped_column(Float, nullable=True)
    average_heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    average_hrv: Mapped[int] = mapped_column(Integer, nullable=True)

    # sleep timing
    bedtime_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    bedtime_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    latency: Mapped[int] = mapped_column(Integer, nullable=True)

    # durations
    awake_time: Mapped[int] = mapped_column(Integer, nullable=True)
    deep_sleep_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    light_sleep_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    rem_sleep_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    total_sleep_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    time_in_bed: Mapped[int] = mapped_column(Integer, nullable=True)

    # efficiency + quality
    efficiency: Mapped[int] = mapped_column(Integer, nullable=True)
    restless_periods: Mapped[int] = mapped_column(Integer, nullable=True)

    # heart metrics
    lowest_heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)

    # readiness (flattened)
    readiness_score: Mapped[int] = mapped_column(Integer, nullable=True)
    activity_balance: Mapped[int] = mapped_column(Integer, nullable=True)
    body_temperature: Mapped[int] = mapped_column(Integer, nullable=True)
    hrv_balance: Mapped[int] = mapped_column(Integer, nullable=True)
    previous_day_activity: Mapped[int] = mapped_column(Integer, nullable=True)
    previous_night: Mapped[int] = mapped_column(Integer, nullable=True)
    recovery_index: Mapped[int] = mapped_column(Integer, nullable=True)
    resting_heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    sleep_balance: Mapped[int] = mapped_column(Integer, nullable=True)
    sleep_regularity: Mapped[int] = mapped_column(Integer, nullable=True)

    temperature_deviation: Mapped[float] = mapped_column(Float, nullable=True)
    temperature_trend_deviation: Mapped[float] = mapped_column(Float, nullable=True)

    readiness_score_delta: Mapped[int] = mapped_column(Integer, nullable=True)
    sleep_score_delta: Mapped[int] = mapped_column(Integer, nullable=True)

    # flags / misc
    low_battery_alert: Mapped[bool] = mapped_column(Boolean, nullable=True)
    ring_id: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=True)

    sleep_algorithm_version: Mapped[str] = mapped_column(String, nullable=True)
    sleep_analysis_reason: Mapped[str] = mapped_column(String, nullable=True)

    # heart rate series
    heart_rate_interval: Mapped[int] = mapped_column(Integer, nullable=True)
    heart_rate_items: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    heart_rate_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # HRV series
    hrv_interval: Mapped[int] = mapped_column(Integer, nullable=True)
    hrv_items: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    hrv_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # raw signals
    movement_30_sec: Mapped[str] = mapped_column(String, nullable=True)
    sleep_phase_30_sec: Mapped[str] = mapped_column(String, nullable=True)
    sleep_phase_5_min: Mapped[str] = mapped_column(String, nullable=True)
    app_sleep_phase_5_min: Mapped[str] = mapped_column(String, nullable=True)

    # period
    period: Mapped[int] = mapped_column(Integer, nullable=True)

class SleepRoute(Base):
    __tablename__ = "sleep_routes"

    # identifiers (required)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    day: Mapped[date] = mapped_column(Date)

    # averages
    average_breath: Mapped[float] = mapped_column(Float, nullable=True)
    average_heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    average_hrv: Mapped[int] = mapped_column(Integer, nullable=True)

    # sleep timing
    bedtime_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    bedtime_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    latency: Mapped[int] = mapped_column(Integer, nullable=True)

    # durations
    awake_time: Mapped[int] = mapped_column(Integer, nullable=True)
    deep_sleep_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    light_sleep_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    rem_sleep_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    total_sleep_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    time_in_bed: Mapped[int] = mapped_column(Integer, nullable=True)

    # efficiency + quality
    efficiency: Mapped[int] = mapped_column(Integer, nullable=True)
    restless_periods: Mapped[int] = mapped_column(Integer, nullable=True)

    # heart metrics
    lowest_heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)

    # heart rate series
    heart_rate_interval: Mapped[int] = mapped_column(Integer, nullable=True)
    heart_rate_items: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    heart_rate_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # HRV series
    hrv_interval: Mapped[int] = mapped_column(Integer, nullable=True)
    hrv_items: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    hrv_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)