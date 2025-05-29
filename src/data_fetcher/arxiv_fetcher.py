import uuid
import xml
from io import BytesIO
from typing import Dict, Optional, Union
import xml.etree.ElementTree as ET

import pandas as pd
import requests
from sqlalchemy import text

from src.config import ARXIV_FETCHER_BATCH_SIZE
from src.client.postgresql_client import arxiv_postgres_engine
from src.monitoring.arxiv_monitor import ARXIV_API_REQUESTS_TOTAL, ARXIV_API_RESPONSE_LATENCY, ARXIV_FETCH_IN_PROGRESS
from src.monitoring.base import fetcher_prometheus_monitor
from src.utils.file_utils import ensure_dir_for_file
from src.utils.http_client import build_http_session_with_retry

class ArxivTaskManager:
    def __init__(self, task_id: Optional[int] = None):
        self.task_id = task_id

    def get_a_task(self) -> Dict[str, Union[str, int]]:
        query = '''
        SELECT
            id as task_id,
            cast(start_date as TEXT),
            cast(end_date as TEXT),
            start_idx 
        FROM 
            arxiv_fetch_task
        WHERE 
            not is_finished 
        limit 1 
        '''
        arxiv_fetch_task_raw = pd.read_sql(query, con=arxiv_postgres_engine)
        if not arxiv_fetch_task_raw.empty:
            self.task_id = int(arxiv_fetch_task_raw['task_id'].iloc[0])
            return arxiv_fetch_task_raw.iloc[0].to_dict()
        else:
            return {}
    
    def mark_task_status(self):
        query = '''
        UPDATE 
            arxiv_fetch_task 
        SET
            is_finished = True
        WHERE 
            id = :task_id
        '''

        with arxiv_postgres_engine.connect() as conn:
            try:
                conn.execute(text(query), parameters={"task_id": self.task_id})
                conn.commit()
            except Exception as e:
                print(f"ERROR while updating task status: {e}")
                conn.rollback()


class ArxivMetadataFetcher:
    XML_FOLDER = './tmp_xml/'
    
    def __init__(self):
        self.http: requests.Session = build_http_session_with_retry()

    def generate_tmp_xml_filepath(self) -> str:
        random_uuid = str(uuid.uuid4())[:8]
        return f"{self.XML_FOLDER}{random_uuid}.xml"
    
    @staticmethod
    def create_api_url(start_date: str, end_date: str, start_idx: int, fetch_batch_size: int) -> str:
        '''
        start_date and end_date format like 'YYYYMMDD'
        '''
        start_date = pd.to_datetime(start_date).strftime("%Y%m%d")
        end_date = pd.to_datetime(end_date).strftime("%Y%m%d")
        return (
            f"https://export.arxiv.org/api/query?"
            f"search_query=submittedDate:%5B{start_date}0000+TO+{end_date}2359%5D&"
            f"start={start_idx}&"
            f"max_results={fetch_batch_size}&"
            f"sortBy=submittedDate&"
            f"sortOrder=ascending"
        )
    
    @fetcher_prometheus_monitor(
        api_counter=ARXIV_API_REQUESTS_TOTAL,
        latency_histogram=ARXIV_API_RESPONSE_LATENCY,
        in_progress_gauge=ARXIV_FETCH_IN_PROGRESS
    ) 
    def fetch_arxiv_metadata_api(self, start_date: str, end_date: str, start_idx: int, fetch_batch_size: int) -> xml.etree.ElementTree.ElementTree:
        query = self.create_api_url(start_date, end_date, start_idx, fetch_batch_size) 
        response = self.http.get(query)
        return ET.parse(BytesIO(response.content))
    
    def save_arxiv_metadata(self, tree: xml.etree.ElementTree.ElementTree) -> str:
        # could be changed to other sotrage system like S3 ...
        tmp_xml_filepath = self.generate_tmp_xml_filepath()
        ensure_dir_for_file(tmp_xml_filepath)

        print(f"XML is temporary saving to '{tmp_xml_filepath}' ...")
        tree.write(tmp_xml_filepath, encoding='utf-8', xml_declaration=True)
        return tmp_xml_filepath
    
    def fetch_and_save_arxiv_metadata(self, start_date: str, end_date: str, start_idx: int, fetch_batch_size: int = ARXIV_FETCHER_BATCH_SIZE) -> str:
        arxiv_metdata_tree = self.fetch_arxiv_metadata_api(start_date=start_date, end_date=end_date, start_idx=start_idx, fetch_batch_size=fetch_batch_size)
        tmp_xml_filepath = self.save_arxiv_metadata(arxiv_metdata_tree)
        return tmp_xml_filepath
