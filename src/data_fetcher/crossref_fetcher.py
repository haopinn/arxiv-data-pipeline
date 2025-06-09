from typing import Optional

import pandas as pd

from src.config import CROSSREF_API_SCORE_THRSLD, WORKER_ID
from src.monitoring.fetcher_monitor import fetcher_prometheus_monitor
from src.monitoring.crossref_monitor import CrossrefFetcherMetricsCollector
from src.schema.crossref_schema import CrossrefRawMetadata
from src.utils.http_client import build_http_session_with_retry

crossref_fetcher_metrics = CrossrefFetcherMetricsCollector()

class CrossrefDataFetcher:
    @staticmethod
    @fetcher_prometheus_monitor(
        job_name='crossref_data_fetcher',
        kafka_consumer_id=WORKER_ID,
        api_counter=crossref_fetcher_metrics.request_count,
        latency_histogram=crossref_fetcher_metrics.latency,
        in_progress_gauge=crossref_fetcher_metrics.in_progress
    )
    def search_crossref(title: str, author: str, start_date: str):
        start_date = pd.to_datetime(start_date).strftime('%Y-%m-%d')

        url = "https://api.crossref.org/works"
        params = {
            "query.title": title,
            "query.author": author,
            "filter": f"from-issued-date:{start_date}" if start_date else "",
            "sort": "score",
            "order": "desc",
            "rows": 1,
        }
        http_retry = build_http_session_with_retry()
        r = http_retry.get(url, params=params)
        r.raise_for_status()
        return r
    
    @staticmethod
    def parse_crossref_api(response):
        content = response.json()["message"]["items"]
        if not content:
            return dict()
        else:
            return content[0]

    def find_fittest_crossref_result(
            self,
            title: str,
            author: str,
            start_date: str,
            score_thrsld: int = CROSSREF_API_SCORE_THRSLD
        ) -> Optional[CrossrefRawMetadata]:
        search_crossref_response = self.search_crossref(title=title, author=author, start_date=start_date)
        search_crossref_raw = self.parse_crossref_api(search_crossref_response)
        result = None
        try:
            if search_crossref_raw['score'] >= score_thrsld:
               result = search_crossref_raw
               return CrossrefRawMetadata.model_validate(result)
        except:
            pass
        return result
