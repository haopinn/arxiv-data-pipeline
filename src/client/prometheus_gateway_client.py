from prometheus_client import CollectorRegistry, push_to_gateway
from prometheus_client.registry import CollectorRegistry

from src.config import PUSHGATEWAY_URL

def push_to_prometheus_gateway(
        job_name: str,
        instance_name: str,
        registry: CollectorRegistry,
        kafka_consumer_id: str = ''
    ):
    return push_to_gateway(
        gateway=PUSHGATEWAY_URL,
        job=job_name,
        registry=registry,
        grouping_key={
            'instance': instance_name,
            'consumer_id': kafka_consumer_id
        }
    )
