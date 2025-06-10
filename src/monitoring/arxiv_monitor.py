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
    
    @staticmethod
    def build_response_size_histogram(registry: CollectorRegistry):
        return Histogram(
            'arxiv_api_response_size_bytes',
            'Size of CrossRef API response payload in bytes',
            labelnames=['endpoint'],
            registry=registry,
            buckets=[75_000, 150_000, 200_000, 250_000, 300_000, 350_000, 400_000, 500_000, 1_000_000, float('inf')]
        )

    def __init__(self, registry: CollectorRegistry = REGISTRY):
        self.request_count = self.build_request_counter(registry)
        self.latency = self.build_response_latency_histogram(registry)
        self.in_progress = self.build_fetch_in_progress_gauge(registry)
        self.response_size = self.build_response_size_histogram(registry=registry)
