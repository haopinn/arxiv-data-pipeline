from prometheus_client import Counter, Histogram, Gauge, REGISTRY
from prometheus_client.registry import CollectorRegistry

class ArxivFetcherMetricsCollector:
    @staticmethod
    def build_request_counter(registry: CollectorRegistry):
        return Counter(
            'arxiv_api_requests_total',
            'Total number of Arxiv API requests',
            ['status'],
            registry=registry
        )
    
    @staticmethod
    def build_response_latency_histogram(registry: CollectorRegistry):
        return Histogram(
            'arxiv_api_response_latency_seconds',
            'Latency of Arxiv API responses',
            registry=registry
        )
    
    @staticmethod
    def build_fetch_in_progress_gauge(registry: CollectorRegistry):
        return Gauge(
            'arxiv_api_fetch_in_progress',
            'Number of Arxiv fetch operations in progress',
            registry=registry
        )

    def __init__(self, registry: CollectorRegistry = REGISTRY):
        self.request_count = self.build_request_counter(registry)
        self.latency = self.build_response_latency_histogram(registry)
        self.in_progress = self.build_fetch_in_progress_gauge(registry)
