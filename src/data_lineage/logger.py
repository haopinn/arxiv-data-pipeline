import time

from src.utils.git_utils import get_git_verision_hash

class DataLineageLogger:
    def __init__(self, job_name: str, instance_id: str):
        self.job_name = job_name
        self.instance_id = instance_id
        self.git_hash = get_git_verision_hash()

    def log_metadata(
        self,
        step_type: str,
        step_name: str,
        source: str = None,
        output: str = None,
        transformation: str = None,
        record_count: int = None,
        extra_metadata: dict = {},
    ):
        log_entry = {
            "job_name": self.job_name,
            "instance_id": self.instance_id,
            "git_hash": self.git_hash,
            "step_type": step_type,
            "step_name": step_name,
            "source": source,
            "output": output,
            "transformation": transformation,
            "record_count": record_count,
            "timestamp": time.time(),
            "extra_metadata": extra_metadata,
        }
        print("[LINEAGE LOG]", log_entry)  # or send to Kafka, DB, MinIO, etc.

    def log_fetch(
        self,
        step_name: str,
        source: str,
        output: str,
        transformation: str,
        record_count: int,
        extra_metadata: dict = {},
    ):
        self.log_metadata(
            step_type="fetch",
            step_name=step_name,
            source=source,
            output=output,
            transformation=transformation,
            record_count=record_count,
            extra_metadata=extra_metadata,
        )

    def log_parse(
        self,
        step_name: str,
        source: str,
        output: str,
        transformation: str,
        record_count: int,
        extra_metadata: dict = {},
    ):
        self.log_metadata(
            step_type="parse",
            step_name=step_name,
            source=source,
            output=output,
            transformation=transformation,
            record_count=record_count,
            extra_metadata=extra_metadata,
        )

    def log_transformation(self, step_name: str, source: str, output: str, transformation: str, record_count: int, extra_metadata: dict = {}):
        self.log_metadata(
            step_type="transformation",
            step_name=step_name,
            source=source,
            output=output,
            transformation=transformation,
            record_count=record_count,
            extra_metadata=extra_metadata,
        )

    def log_validation(self, step_name: str, source: str, transformation: str, validation_passed: bool, extra_metadata: dict = {}):
        self.log_metadata(
            step_type="validation",
            step_name=step_name,
            source=source,
            output=None,
            transformation=transformation,
            record_count=None,
            extra_metadata={**extra_metadata, "validation_passed": validation_passed},
        )

    def log_storage(self, step_name: str, source: str, output: str, record_count: int, transformation: str = "write_to_storage", extra_metadata: dict = {}):
        self.log_metadata(
            step_type="storage",
            step_name=step_name,
            source=source,
            output=output,
            transformation=transformation,
            record_count=record_count,
            extra_metadata=extra_metadata,
        )

    def log_message_publish(self, step_name: str, source: str, output: str, transformation: str = "publish_kafka", record_count: int = None, extra_metadata: dict = {}):
        self.log_metadata(
            step_type="message_publish",
            step_name=step_name,
            source=source,
            output=output,
            transformation=transformation,
            record_count=record_count,
            extra_metadata=extra_metadata,
        )
