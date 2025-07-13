import pandas as pd
from sqlalchemy import text

from src.client.postgresql_client import arxiv_postgres_session
from src.client.postgresql_client import arxiv_postgres_engine

def init_arxiv_fetch_task_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS arxiv_fetch_task (
        id SERIAL PRIMARY KEY,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        start_idx INTEGER NOT NULL,
        is_finished BOOLEAN NOT NULL DEFAULT FALSE,
        create_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """

    with arxiv_postgres_session() as session:
        try:
            session.execute(text(create_table_query))
            session.commit()
        except:
            session.rollback()

    arxiv_fetch_task = pd.read_parquet('./src/script/arxiv_fetch_task.parquet')
    arxiv_fetch_task.to_sql('arxiv_fetch_task', con=arxiv_postgres_engine, if_exists='append', index=False)

if __name__ == "__main__":
    init_arxiv_fetch_task_table()
