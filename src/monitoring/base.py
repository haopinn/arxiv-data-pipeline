from functools import wraps
from prometheus_client import Counter, Histogram, Gauge

def fetcher_prometheus_monitor(
        api_counter: Counter,
        latency_histogram: Histogram,
        in_progress_gauge: Gauge
    ):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            in_progress_gauge.inc()
            with latency_histogram.time():
                try:
                    result = func(*args, **kwargs)
                    api_counter.labels(status='success').inc()
                    return result
                except Exception as e:
                    api_counter.labels(status='failure').inc()
                    raise
                finally:
                    in_progress_gauge.dec()
        return wrapper
    return decorator
