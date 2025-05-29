from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from src.config import KAFKA_BROKER_URL, KAFKA_WORKER_PARTITIONS

def create_topic_if_needed(topic: str, num_partitions: int = KAFKA_WORKER_PARTITIONS, replication_factor: int = 1):
    admin = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER_URL)
    try:
        admin.create_topics([
            NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication_factor)
        ])
        print(f"Topic '{topic}' created.")
    except TopicAlreadyExistsError:
        print(f"ℹTopic '{topic}' already exists.")
    finally:
        admin.close()
