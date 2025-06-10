from prometheus_client import CollectorRegistry, push_to_gateway, pushadd_to_gateway
from prometheus_client.registry import CollectorRegistry

from src.config import PUSHGATEWAY_URL

def push_to_prometheus_gateway(
    job_name: str,
    registry: CollectorRegistry,
    instance_name: str = "",
    kafka_consumer_id: str = None,
    extra_grouping: dict = None,
    push_func=push_to_gateway  # 可切換為 pushadd_to_gateway
) -> None:
    grouping_key = {
        "instance": instance_name,
    }

    if kafka_consumer_id:
        grouping_key["consumer_id"] = kafka_consumer_id

    if extra_grouping:
        grouping_key.update(extra_grouping)

    push_func(
        gateway=PUSHGATEWAY_URL,
        job=job_name,
        registry=registry,
        grouping_key=grouping_key,
    )
