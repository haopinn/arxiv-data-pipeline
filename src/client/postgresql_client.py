from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import ARXIV_POSTGRES_URL

arxiv_postgres_engine = create_engine(ARXIV_POSTGRES_URL)
arxiv_postgres_session = sessionmaker(arxiv_postgres_engine)
