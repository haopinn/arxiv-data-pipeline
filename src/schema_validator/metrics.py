import time
from typing import Dict

from prometheus_client import Counter, CollectorRegistry
from src.client.prometheus_gateway_client import push_to_prometheus_gateway

class MetricProvider:
    def __init__(self, job_name: str, registry: CollectorRegistry = None, instance_name: str = str(time.time())):
        self.job_name = job_name
        self.instance_name = instance_name
        self.registry = registry or CollectorRegistry()

        self._validation_error_counter  = Counter(
            'pydantic_validation_errors',
            'Pydantic model field validation failures',
            ['model', 'field', 'error_type'],
            registry=self.registry
        )

        self._default_value_counter = Counter(
            'pydantic_default_values_used',
            'Number of times a field default value was used',
            ['model', 'field'],
            registry=self.registry
        )

        self._validation_attempt_counter = Counter(
            'pydantic_validation_attempts_total',
            'Total number of model validation attempts (successful or failed)',
            ['model'],
            registry=self.registry
        )

        self._validation_success_counter = Counter(
            'pydantic_validation__success_total',
            'Total number of model validating successfully',
            ['model'],
            registry=self.registry
        )

    def get_counters(self) -> Dict[str, Counter]:
        return {
            "validation_attempt_counter": self._validation_attempt_counter,
            "validation_success_counter": self._validation_success_counter,
            "validation_error_counter": self._validation_error_counter,
            "default_value_used_counter": self._default_value_counter,
        }

    def push(self):
        try:
            push_to_prometheus_gateway(
                job_name=self.job_name,
                instance_name=self.instance_name,
                registry=self.registry
            )
        except Exception as e:
            print(f"Warning: Could not push metrics to gateway: {e}")
        