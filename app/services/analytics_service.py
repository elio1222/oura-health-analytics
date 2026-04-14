from app.repositories.db_repo import query_from_db
from app.services.oura_service import param_builder
from datetime import date, timedelta


def calculate_sleep_summary():

    yesterday = date.today() - timedelta(days=1)
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

    return {
        "avg_score": avg_score,
        "days_tracked": len(data),

        "categories": category_avgs,

        "trend": trend,

        "best_day": {
            "date": best_day.day,
            "score": best_day.score
        },

        "worst_day": {
            "date": worst_day.day,
            "score": worst_day.score
        }
    }

def calculate_readiness_summary(params: dict) -> dict:


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

    # unpacking parameter
    week_from_td, today = params.values()

    readiness_stats = {
        "dates": {
            "start_date": week_from_td,
            "end_date": today
        },
        "avg_scores": {
            "score": round(sum(scores) / len(scores), 2),
            "activity_balance": round(sum(activity_balance) / len(activity_balance), 2),
            "body_temperature": round(sum(body_temperature) / len(body_temperature), 2),
            "hrv_balance": round(sum(hrv_balance) / len(hrv_balance), 2),
            "previous_day_activity": round(sum(previous_day_activity) / len(previous_day_activity), 2),
            "previous_night": round(sum(previous_night) / len(previous_night), 2),
            "recovery_index": round(sum(recovery_index) / len(recovery_index), 2),
            "resting_heart_rate": round(sum(resting_heart_rate) / len(resting_heart_rate), 2),
            "sleep_balance": round(sum(sleep_balance) / len(sleep_balance), 2),
            "sleep_regularity": round(sum(sleep_regularity) / len(sleep_regularity), 2)
        }
    }

    return readiness_stats