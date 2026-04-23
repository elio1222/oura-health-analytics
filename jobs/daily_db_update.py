from pipelines.etl_facade import run_all_etl_pipelines
from pathlib import Path
import logging
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "etl.log"


def main():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        filemode="w",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting daily ETL pipelines for %s", date.today())

    run_all_etl_pipelines()

    logger.info("Finished executing daily ETL pipelines for %s", date.today())



if __name__ == "__main__":
    main()