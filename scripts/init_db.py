from app.models.models import Base
from pipelines.etl_facade import get_database_uri
from sqlalchemy import create_engine

def init_db():
    engine = create_engine(get_database_uri())
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()