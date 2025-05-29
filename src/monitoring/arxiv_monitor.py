from prometheus_client import Counter, Histogram, Gauge

ARXIV_API_REQUESTS_TOTAL = Counter(
    'arxiv_api_requests_total',
    'Total number of Arxiv API requests',
    ['status']
)

ARXIV_API_RESPONSE_LATENCY = Histogram(
    'arxiv_api_response_latency_seconds',
    'Latency of Arxiv API responses'
)

ARXIV_FETCH_IN_PROGRESS = Gauge(
    'arxiv_api_fetch_in_progress',
    'Number of Arxiv fetch operations in progress'
)
