from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class DailySleepSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    day: date
    score: int

    deep_sleep: int
    efficiency: int
    latency: int
    rem_sleep: int
    restfulness: int
    timing: int
    total_sleep: int

    performance_score: int
    recovery_score: int
    consistency_score: int
    custom_score: int

class DailyReadinessSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    day: date
    score: int

    activity_balance: int
    body_temperature: int
    hrv_balance: int
    previous_day_activity: int
    previous_night: int
    recovery_index: int
    resting_heart_rate: int
    sleep_balance: int
    sleep_regularity: int
    temperature_deviation: float

    vitality_score: int
    alertness_index: int
    resilience_score: int
    balance_quotient: int
    recovery_potential: int

class DailyStressSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    day: date

    day_summary: Optional[str] = None
    recovery_high: Optional[int] = None
    stress_high: Optional[int] = None

    stress_index: Optional[int] = None
    resilience_rating: Optional[int] = None
