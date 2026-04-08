import requests
from jobs.pipelines.sleep_etl import run_dailysleep_pipeline


def main():
    run_dailysleep_pipeline()

if __name__ == "__main__":
    main()
