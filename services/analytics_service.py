from services.db_service import query_sleep_data
from services.oura_service import param_builder
from datetime import date, timedelta


def calculate_sleep_summary():

    yesterday = date.today() - timedelta(days=1)
    week_from_td = yesterday - timedelta(days=6)
    params = param_builder(start_date=week_from_td, end_date=yesterday)

    data = query_sleep_data(params=params)

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