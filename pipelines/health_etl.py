from datetime import date
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import func
from dateutil.relativedelta import relativedelta
from app.services.oura_service import fetch_oura_data

def fetch_and_extract(
        engine,
        model_class,
        url: str,
        param_builder,
        extract_raw_func=None
):
    Session = sessionmaker(bind=engine)

    with Session() as session:

        start_of_history = session.query(func.max(model_class.day)).scalar()
        end_date = date.today()
        
        if start_of_history is None:
            start_of_history = date(2024, 12, 1)

        while start_of_history < end_date:
            current_end_date = start_of_history + relativedelta(months=1) - relativedelta(days=1)
            params = param_builder(start_date=start_of_history, end_date=current_end_date)

            try:
                data = fetch_oura_data(url=url, params=params)
                save_raw_data_generic(session=session, model_class=model_class, data=data, extract_func=extract_raw_func)
            except Exception as e:
                print(e)

            start_of_history += relativedelta(months=1)


def save_raw_data_generic(
        session: Session,
        model_class,
        data: dict,
        extract_func=None
):
    for d in data["data"]:
        record_obj = extract_func(d=d)
        new_record = model_class(**record_obj)
        session.merge(new_record)
    session.commit()

def extract_raw_sleep(d: dict) -> dict:
    contributors = d.get("contributors", {})
    return {
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

def extract_raw_readiness(d: dict) -> dict:
    contributors = d.get("contributors", {})
    return {
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

def extract_raw_stress(d: dict) -> dict:
    return {
        "id": d.get("id"),
        "day": d.get("day"),
        "day_summary": d.get("day_summary"),
        "recovery_high": d.get("recovery_high"),
        "stress_high": d.get("stress_high")
    }

def process_and_save_data_generic(
        session: Session,
        model_class,
        data: dict,
        process_func=None
):
    
    for d in data:
        record_obj = process_func(d=d)
        new_record = model_class(**record_obj)
        session.merge(new_record)
    session.commit()

def process_sleep(d: object) -> dict:
    # formulas
    performance_score = (0.25 * d.rem_sleep) + (0.20 * d.efficiency) + (0.20 * d.latency) + (0.15 * d.total_sleep) + (0.10 * d.deep_sleep) + (0.10 * d.timing)

    recovery_score = (0.30 * d.deep_sleep) + (0.25 * d.total_sleep) + (0.15 * d.restfulness) + (0.10 * d.efficiency) + (0.10 * d.rem_sleep) + (0.10 * d.timing)

    consistency_score = (0.35 * d.timing) + (0.25 * d.latency) + (0.20 * d.efficiency) + (0.10 * d.restfulness) + (0.10 * d.total_sleep)

    custom_score = (0.25 * d.total_sleep) + (0.20 * d.rem_sleep) + (0.20 * d.efficiency) + (0.15 * d.latency) + (0.1 * d.deep_sleep) + (0.10 * d.timing)

    # transformed data obj
    return {

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

def process_readiness(d: object) -> dict:
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
    
    return {
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

def process_stress(d: object) -> dict:
    """stress_index = 0.6 * d.stress_high - 0.4 * d.recovery_high"""
    """resilience_rating = 0.7 * d.recovery_high - 0.3 * d.stress_high"""

    stress_high = d.stress_high or 7200
    recovery_high = d.recovery_high or 3600

    stress_index = 0.6 * stress_high - 0.4 * recovery_high
    resilience_rating = 0.7 * recovery_high - 0.3 * stress_high

    return {
        "id": d.id,
        "day": d.day,
        "day_summary": d.day_summary,
        "recovery_high": recovery_high,
        "stress_high": stress_high,
        "stress_index": stress_index,
        "resilience_rating": resilience_rating
    }


def transform_and_load(
        engine,
        raw_model_class,
        target_model_class,
        process_func
):
    Session = sessionmaker(bind=engine)
    

    with Session() as session:

        start_of_history = session.query(func.max(target_model_class.day)).scalar()
        end_date = date.today()

        if start_of_history is None:
            start_of_history = date(2024, 12, 1)

        while start_of_history < end_date:
            current_end_date = start_of_history + relativedelta(months=1) - relativedelta(day=1)

            try:
                data = session.query(raw_model_class).filter(raw_model_class.day >= start_of_history, raw_model_class.day <= current_end_date).all()

                process_and_save_data_generic(session=session, model_class=target_model_class, data=data, process_func=process_func)
            except Exception as e:
                print(e)

            start_of_history += relativedelta(months=1)


def run_etl_pipeline(
        engine,
        raw_model_class,
        target_model_class,
        url: str,
        param_builder,
        extract_raw_func,
        process_func
):
    try:
        fetch_and_extract(
            engine=engine,
            model_class=raw_model_class,
            url=url,
            param_builder=param_builder,
            extract_raw_func=extract_raw_func
        )
        transform_and_load(
            engine=engine,
            raw_model_class=raw_model_class,
            target_model_class=target_model_class,
            process_func=process_func
        )
        # log successful
    except Exception as e:
        print(e)
