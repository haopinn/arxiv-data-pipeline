from prometheus_client import Counter, Histogram, Gauge, REGISTRY
from prometheus_client.registry import CollectorRegistry

class CrossrefFetcherMetricsCollector:
    @staticmethod
    def build_request_counter(registry: CollectorRegistry):
        return Counter(
            'crossref_api_requests_total',
            'Total number of CrossRef API requests',
            ['status'],
            registry=registry
        )

    @staticmethod
    def build_response_latency_histogram(registry: CollectorRegistry):
        return Histogram(
            'crossref_api_response_latency_seconds',
            'Latency of CrossRef API responses',
            registry=registry
        )

    @staticmethod
    def build_fetch_in_progress_gauge(registry: CollectorRegistry):
        return Gauge(
            'crossref_api_fetch_in_progress',
            'Number of CrossRef fetch operations in progress',
            registry=registry
        )

    @staticmethod
    def build_response_size_histogram(registry: CollectorRegistry):
        return Histogram(
            'crossref_api_response_size_bytes',
            'Size of CrossRef API response payload in bytes',
            ['endpoint'],
            registry=registry
        )

    def __init__(self, registry: CollectorRegistry = REGISTRY):
        self.request_count = self.build_request_counter(registry)
        self.latency = self.build_response_latency_histogram(registry)
        self.in_progress = self.build_fetch_in_progress_gauge(registry)
        self.response_size = self.build_response_size_histogram(registry=registry)
