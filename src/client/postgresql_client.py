from sqlalchemy import create_engine

from src.config import ARXIV_POSTGRES_URL

arxiv_postgres_engine = create_engine(ARXIV_POSTGRES_URL)
