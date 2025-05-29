from prometheus_client import Counter, Histogram, Gauge

CROSSREF_API_REQUESTS_TOTAL = Counter(
    'crossref_api_requests_total',
    'Total number of Crossref API requests',
    ['status']
)

CROSSREF_API_RESPONSE_LATENCY = Histogram(
    'crossref_api_response_latency_seconds',
    'Latency of Crossref API responses'
)

CROSSREF_FETCH_IN_PROGRESS = Gauge(
    'crossref_api_fetch_in_progress',
    'Number of Crossref fetch operations in progress'
)
