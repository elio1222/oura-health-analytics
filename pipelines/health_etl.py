from datetime import date
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import func
from dateutil.relativedelta import relativedelta
from app.services.oura_service import fetch_oura_data
import logging

logger = logging.getLogger(__name__)

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
                logger.info("Fetched %d records", len(data))
                save_raw_data_generic(session=session, model_class=model_class, data=data, extract_func=extract_raw_func)
                logger.info("Extracted %d records (raw data) into PSQL", len(data))
            except Exception as e:
                logger.exception("Failed whilst fetching and/or extracting with the following parameters: %s", params)

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

def extract_raw_sleep_routes(d: dict) -> dict:
    heart_rate = d.get("heart_rate", {})
    hrv = d.get("hrv", {})
    readiness = d.get("readiness", {})
    contributors = readiness.get("contributors", {})

    return {
        # identifiers
        "id": d.get("id"),
        "day": d.get("day"),
        "type": d.get("type"),
        "ring_id": d.get("ring_id"),

        # meta
        "updated_at": d.get("meta", {}).get("updated_at"),
        "version": d.get("meta", {}).get("version"),

        # averages
        "average_breath": d.get("average_breath"),
        "average_heart_rate": d.get("average_heart_rate"),
        "average_hrv": d.get("average_hrv"),

        # sleep timing
        "bedtime_start": d.get("bedtime_start"),
        "bedtime_end": d.get("bedtime_end"),
        "latency": d.get("latency"),

        # sleep durations
        "awake_time": d.get("awake_time"),
        "deep_sleep_duration": d.get("deep_sleep_duration"),
        "light_sleep_duration": d.get("light_sleep_duration"),
        "rem_sleep_duration": d.get("rem_sleep_duration"),
        "total_sleep_duration": d.get("total_sleep_duration"),
        "time_in_bed": d.get("time_in_bed"),

        # quality metrics
        "efficiency": d.get("efficiency"),
        "lowest_heart_rate": d.get("lowest_heart_rate"),
        "restless_periods": d.get("restless_periods"),

        # deltas
        "readiness_score_delta": d.get("readiness_score_delta"),
        "sleep_score_delta": d.get("sleep_score_delta"),

        # flags / misc
        "low_battery_alert": d.get("low_battery_alert"),
        "sleep_algorithm_version": d.get("sleep_algorithm_version"),
        "sleep_analysis_reason": d.get("sleep_analysis_reason"),

        # heart rate (arrays kept structured, not flattened)
        "heart_rate_interval": heart_rate.get("interval"),
        "heart_rate_items": heart_rate.get("items"),
        "heart_rate_timestamp": heart_rate.get("timestamp"),

        # HRV
        "hrv_interval": hrv.get("interval"),
        "hrv_items": hrv.get("items"),
        "hrv_timestamp": hrv.get("timestamp"),

        # readiness
        "readiness_score": readiness.get("score"),
        "temperature_deviation": readiness.get("temperature_deviation"),
        "temperature_trend_deviation": readiness.get("temperature_trend_deviation"),

        # readiness contributors
        "activity_balance": contributors.get("activity_balance"),
        "body_temperature": contributors.get("body_temperature"),
        "hrv_balance": contributors.get("hrv_balance"),
        "previous_day_activity": contributors.get("previous_day_activity"),
        "previous_night": contributors.get("previous_night"),
        "recovery_index": contributors.get("recovery_index"),
        "resting_heart_rate": contributors.get("resting_heart_rate"),
        "sleep_balance": contributors.get("sleep_balance"),
        "sleep_regularity": contributors.get("sleep_regularity"),

        # phases / signals
        "movement_30_sec": d.get("movement_30_sec"),
        "sleep_phase_30_sec": d.get("sleep_phase_30_sec"),
        "sleep_phase_5_min": d.get("sleep_phase_5_min"),
        "app_sleep_phase_5_min": d.get("app_sleep_phase_5_min"),

        # period
        "period": d.get("period"),
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

def process_sleep_routes(d: object) -> dict:

    return {
        # identifiers
        "id": d.id,
        "day": d.day,

        # averages
        "average_breath": d.average_breath,
        "average_heart_rate": d.average_heart_rate,
        "average_hrv": d.average_hrv,

        # sleep timing
        "bedtime_start": d.bedtime_start,
        "bedtime_end": d.bedtime_end,
        "latency": d.latency,

        # durations
        "awake_time": d.awake_time,
        "deep_sleep_duration": d.deep_sleep_duration,
        "light_sleep_duration": d.light_sleep_duration,
        "rem_sleep_duration": d.rem_sleep_duration,
        "total_sleep_duration": d.total_sleep_duration,
        "time_in_bed": d.time_in_bed,

        # quality
        "efficiency": d.efficiency,
        "restless_periods": d.restless_periods,
        "lowest_heart_rate": d.lowest_heart_rate,

        # heart rate (ORM sub-object)
        "heart_rate_interval": d.heart_rate_interval,
        "heart_rate_items": d.heart_rate_items,
        "heart_rate_timestamp": d.heart_rate_timestamp,

        # HRV
        "hrv_interval": d.hrv_interval,
        "hrv_items": d.hrv_items,
        "hrv_timestamp": d.hrv_timestamp,
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
                logger.info("Querying raw data from PSQL database")
                data = session.query(raw_model_class).filter(raw_model_class.day >= start_of_history, raw_model_class.day <= current_end_date).all()
                logger.info("Queried %d records", len(data))
                process_and_save_data_generic(session=session, model_class=target_model_class, data=data, process_func=process_func)
                logger.info("Processed and saved %d into PSQL database", len(data))
            except Exception as e:
                logger.exception("Failed whilst querying and/or processing and saving data with the following parameters: start_date: %s end_date: %s", start_of_history, current_end_date)

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
        logger.info("Fetching & Extracting raw data from Oura API")
        fetch_and_extract(
            engine=engine,
            model_class=raw_model_class,
            url=url,
            param_builder=param_builder,
            extract_raw_func=extract_raw_func
        )
        logger.info("Transforming & Loading raw data to processed data")
        transform_and_load(
            engine=engine,
            raw_model_class=raw_model_class,
            target_model_class=target_model_class,
            process_func=process_func
        )
        logger.info("Completed ETL pipeline")
    except Exception as e:
        print(e)
