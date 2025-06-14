import time
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, REGISTRY
from prometheus_client.registry import CollectorRegistry

from src.client.prometheus_gateway_client import push_to_prometheus_gateway

def fetcher_prometheus_monitor(
        job_name: str,
        api_counter: Counter,
        latency_histogram: Histogram,
        response_size_histogram: Histogram,
        in_progress_gauge: Gauge,
        url_endpoint: str = '',
        kafka_consumer_id: str = '',
        registry: CollectorRegistry = REGISTRY,
    ):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            instance_name = kwargs.get("instance_name", str(time.time()))
            in_progress_gauge.inc()
            with latency_histogram.time():
                try:
                    result = func(*args, **kwargs)
                    api_counter.labels(status='success').inc()
                    if hasattr(result, 'content'):
                        response_size_histogram.labels(endpoint=url_endpoint).observe(len(result.content))
                    return result
                except Exception as e:
                    api_counter.labels(status='failure').inc()
                    raise
                finally:
                    in_progress_gauge.dec()
                    # Push metrics to Prometheus Pushgateway
                    push_to_prometheus_gateway(
                        job_name=job_name,
                        instance_name=instance_name,
                        registry=registry,
                        kafka_consumer_id=kafka_consumer_id
                    )
        return wrapper
    return decorator
