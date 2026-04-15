import pipelines.health_etl as etl
import app.models.models as model
from sqlalchemy import create_engine
import os
from app.services.oura_service import param_builder

def get_database_uri():
    # If running inside Docker, override automatically
    if os.path.exists("/.dockerenv"):
        return os.getenv(
            "DOCKER_DATABASE_URI",
            os.getenv("DATABASE_URI")
        )
    return os.getenv("DATABASE_URI")

def run_all_etl_pipelines():

    engine = create_engine(get_database_uri())
    
    # for sleep
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
    etl.run_etl_pipeline(
        engine=engine,
        raw_model_class=model.RawDailyStress,
        target_model_class=model.DailyStress,
        url="https://api.ouraring.com/v2/usercollection/daily_stress",
        param_builder=param_builder,
        extract_raw_func=etl.extract_raw_stress,
        process_func=etl.process_stress
    )

if __name__ == "__main__":
    run_all_etl_pipelines()