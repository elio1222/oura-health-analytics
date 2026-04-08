import requests
from jobs.pipelines.sleep_etl import run_dailysleep_pipeline
from jobs.pipelines.readiness_etl import run_dailyreadiness_pipeline

def main():
    run_dailysleep_pipeline()
    run_dailyreadiness_pipeline()

if __name__ == "__main__":
    main()
