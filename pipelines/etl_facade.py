import pipelines.health_etl as etl
import app.models.models as model
from sqlalchemy import create_engine
import os
from app.services.oura_service import param_builder
import logging

logger = logging.getLogger(__name__)

def get_database_uri():
    # If running inside Docker, override automatically
    try:
        if os.path.exists("/.dockerenv"):
            return os.getenv(
                "DOCKER_DATABASE_URI",
                os.getenv("DATABASE_URI")
            )
        return os.getenv("DATABASE_URI")
    except Exception as e:
        logger.exception("Failed while getting Database URI, %s", e)

def run_all_etl_pipelines():

    engine = create_engine(get_database_uri())
    
    # for daily sleep
    logger.info("Starting Daily Sleep ETL pipeline")
    etl.run_etl_pipeline(
        engine=engine,
        raw_model_class=model.RawDailySleep,
        target_model_class=model.DailySleep,
        url="https://api.ouraring.com/v2/usercollection/daily_sleep",
        param_builder=param_builder,
        extract_raw_func=etl.extract_raw_sleep,
        process_func=etl.process_sleep
    )

    # for readiness
    logger.info("Starting Daily Readiness ETL pipeline")
    etl.run_etl_pipeline(
        engine=engine,
        raw_model_class=model.RawDailyReadiness,
        target_model_class=model.DailyReadiness,
        url="https://api.ouraring.com/v2/usercollection/daily_readiness",
        param_builder=param_builder,
        extract_raw_func=etl.extract_raw_readiness,
        process_func=etl.process_readiness
    )

    # for stress
    logger.info("Starting Daily Stress ETL Pipeline")
    etl.run_etl_pipeline(
        engine=engine,
        raw_model_class=model.RawDailyStress,
        target_model_class=model.DailyStress,
        url="https://api.ouraring.com/v2/usercollection/daily_stress",
        param_builder=param_builder,
        extract_raw_func=etl.extract_raw_stress,
        process_func=etl.process_stress
    )

    # for sleep routes
    logger.info("Starting Sleep Routes ETL Pipeline")
    etl.run_etl_pipeline(
        engine=engine,
        raw_model_class=model.RawSleepRoute,
        target_model_class=model.SleepRoute,
        url="https://api.ouraring.com/v2/usercollection/sleep",
        param_builder=param_builder,
        extract_raw_func=etl.extract_raw_sleep_routes,
        process_func=etl.process_sleep_routes
    )

    logger.info("Finished executing all ETL pipelines")

if __name__ == "__main__":
    run_all_etl_pipelines()