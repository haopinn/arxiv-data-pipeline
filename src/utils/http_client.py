import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import HTTP_RETRY_BACKOFF_FACTOR

def build_http_session_with_retry(backoff_factor: int = HTTP_RETRY_BACKOFF_FACTOR) -> requests.Session:
    retry_strategy = Retry(
        total=5,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    return http
