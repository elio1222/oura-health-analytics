from app.repositories.db_repo import query_from_db
from app.services.oura_service import param_builder
from datetime import date, timedelta


def calculate_sleep_summary():
    
    yesterday = date.today()
    week_from_td = yesterday - timedelta(days=6)
    params = param_builder(start_date=week_from_td, end_date=yesterday)

    data = query_from_db(type_of_data="sleep", params=params)

    scores = [d.score for d in data]
    avg_score = round(sum(scores) / len(scores))

    sleep_quality = [
        (d.deep_sleep + d.rem_sleep + d.efficiency + d.restfulness) / 4
        for d in data
    ]

    recovery = [
        (d.recovery_score + d.latency) / 2
        for d in data
    ]

    consistency = [
        (d.timing + d.consistency_score) / 2
        for d in data
    ]

    performance = [
        (d.performance_score + d.custom_score) / 2
        for d in data
    ]

    category_avgs = {
        "sleep_quality": round(sum(sleep_quality) / len(sleep_quality)),
        "recovery": round(sum(recovery) / len(recovery)),
        "consistency": round(sum(consistency) / len(consistency)),
        "performance": round(sum(performance) / len(performance)),
    }

    best_day = max(data, key=lambda d: d.score)
    worst_day = min(data, key=lambda d: d.score)

    return {
        "avg_score": avg_score,
        "days_tracked": len(data),

        "avg_category_scores": category_avgs,

        "trend": calculate_trend(scores=scores),

        "best_day": {
            "date": best_day.day,
            "score": best_day.score
        },

        "worst_day": {
            "date": worst_day.day,
            "score": worst_day.score
        }
    }

def calculate_readiness_summary() -> dict:

    yesterday = date.today()
    week_from_td = yesterday - timedelta(days=6)
    params = param_builder(start_date=week_from_td, end_date=yesterday)


    data = query_from_db(type_of_data="readiness", params=params)

    scores = [d.score for d in data]
    activity_balance = [d.activity_balance for d in data if d.activity_balance is not None]
    body_temperature = [d.body_temperature for d in data if d.body_temperature is not None]
    hrv_balance = [d.hrv_balance for d in data if d.hrv_balance is not None]
    previous_day_activity = [d.previous_day_activity for d in data if d.previous_day_activity is not None]
    previous_night = [d.previous_night for d in data if d.previous_night is not None]
    recovery_index = [d.recovery_index for d in data if d.recovery_index is not None]
    resting_heart_rate = [d.resting_heart_rate for d in data if d.resting_heart_rate is not None]
    sleep_balance = [d.sleep_balance for d in data if d.sleep_balance is not None]
    sleep_regularity = [d.sleep_regularity for d in data if d.sleep_regularity is not None]

    category_avgs = {
        "activity_balance": round(sum(activity_balance) / len(activity_balance)),
        "body_temperature": round(sum(body_temperature) / len(body_temperature)),
        "hrv_balance": round(sum(hrv_balance) / len(hrv_balance)),
        "previous_day_activity": round(sum(previous_day_activity) / len(previous_day_activity)),
        "previous_night": round(sum(previous_night) / len(previous_night)),
        "recovery_index": round(sum(recovery_index) / len(recovery_index)),
        "resting_heart_rate": round(sum(resting_heart_rate) / len(resting_heart_rate)),
        "sleep_balance": round(sum(sleep_balance) / len(sleep_balance)),
        "sleep_regularity": round(sum(sleep_regularity) / len(sleep_regularity))
        }
    
    best_day = max(data, key=lambda d: d.score)
    worst_day = min(data, key=lambda d: d.score)

    return {
        "avg_score": round(sum(scores) / len(data)),
        "days_tracked": len(data),

        "avg_category_scores": category_avgs,

        "trend": calculate_trend(scores=scores),

        "best_day": {
            "date": best_day.day,
            "score": best_day.score
        },

        "worst_day": {
            "date": worst_day.day,
            "score": worst_day.score
        }
    }

def calculate_stress_summary():
    today = date.today()
    week_from_td = date.today() - timedelta(days=6)
    params = param_builder(start_date=week_from_td, end_date=today)
    data = query_from_db(type_of_data="stress", params=params)

    recovery_high = [d.recovery_high for d in data if d.recovery_high is not None]
    
    stress_high = [d.stress_high for d in data if d.stress_high is not None]

    counts = {}

    for d in data:
        if not d.day_summary:
            continue
        counts[d.day_summary] = counts.get(d.day_summary, 0) + 1

    week_summary = max(counts, key=counts.get)

    category_avgs = {
        "avg_recovery_time": round(round(sum(recovery_high) / len(data)) / 3600, 2),
        "avg_stress_time": round(round(sum(stress_high) / len(data)) / 3600, 2)
    }


    return {
        "week_summary": week_summary,
        "days_tracked": len(data),
        "avg_category_times": category_avgs,
    }

def calculate_activity_summary() -> dict:

    yesterday = date.today()
    week_from_td = yesterday - timedelta(days=6)
    params = param_builder(start_date=week_from_td, end_date=yesterday)

    data = query_from_db(type_of_data="activity", params=params)

    # Core scores
    scores = [d.score for d in data if d.score is not None]
    
    # Key physical metrics
    steps = [d.steps for d in data if d.steps is not None]
    active_calories = [d.active_calories for d in data if d.active_calories is not None]
    high_activity_time = [d.high_activity_time for d in data if d.high_activity_time is not None]
    sedentary_time = [d.sedentary_time for d in data if d.sedentary_time is not None]

    # Contributors
    meet_daily_targets = [d.meet_daily_targets for d in data if d.meet_daily_targets is not None]
    move_every_hour = [d.move_every_hour for d in data if d.move_every_hour is not None]
    recovery_time = [d.recovery_time for d in data if d.recovery_time is not None]
    stay_active = [d.stay_active for d in data if d.stay_active is not None]
    training_frequency = [d.training_frequency for d in data if d.training_frequency is not None]
    training_volume = [d.training_volume for d in data if d.training_volume is not None]

    category_avgs = {
        "steps": round(sum(steps) / len(steps)) if steps else 0,
        "active_calories": round(sum(active_calories) / len(active_calories)) if active_calories else 0,
        "high_activity_time": round(sum(high_activity_time) / len(high_activity_time)) if high_activity_time else 0,
        "sedentary_time": round(sum(sedentary_time) / len(sedentary_time)) if sedentary_time else 0,
        
        "meet_daily_targets": round(sum(meet_daily_targets) / len(meet_daily_targets)) if meet_daily_targets else 0,
        "move_every_hour": round(sum(move_every_hour) / len(move_every_hour)) if move_every_hour else 0,
        "recovery_time": round(sum(recovery_time) / len(recovery_time)) if recovery_time else 0,
        "stay_active": round(sum(stay_active) / len(stay_active)) if stay_active else 0,
        "training_frequency": round(sum(training_frequency) / len(training_frequency)) if training_frequency else 0,
        "training_volume": round(sum(training_volume) / len(training_volume)) if training_volume else 0
    }
    
    best_day = max(data, key=lambda d: d.score)
    worst_day = min(data, key=lambda d: d.score)

    return {
        "avg_score": round(sum(scores) / len(scores)) if scores else 0,
        "days_tracked": len(data),

        "avg_category_scores": category_avgs,

        "trend": calculate_trend(scores=scores),

        "best_day": {
            "date": best_day.day,
            "score": best_day.score
        },

        "worst_day": {
            "date": worst_day.day,
            "score": worst_day.score
        }
    }

def calculate_trend(scores: list) -> str:
    mid = len(scores) // 2
    first_half = scores[:mid]
    second_half = scores[mid:]

    trend = "stable"
    if first_half and second_half:
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        if second_avg > first_avg + 2:
            trend = "improving"
        elif second_avg < first_avg - 2:
            trend = "declining"

    return trend


def get_all_summaries():
    return {
        "days_tracked": {
            "start_date": date.today() - timedelta(days=6),
            "end_date": date.today()
        },
        "sleep_summary": calculate_sleep_summary(),
        "readiness_summary": calculate_readiness_summary(),
        "stress_summary": calculate_stress_summary()
    }