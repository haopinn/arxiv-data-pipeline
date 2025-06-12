import json

from kafka import KafkaConsumer

from src.client.kafka_base_client import create_topic_if_needed
from src.config import KAFKA_BROKER_URL
from src.schema.kafka_schema import ArxivToCrossrefMessage, DlqMessage
from src.pipeline.crossref_pipeline import CrossrefDataPipeline

def process_arxiv_to_crossref_message(msg: dict):
    print("Received message:", msg)
    message = ArxivToCrossrefMessage.model_validate(msg)
    print("Message is validated.")
    print("Message is ingesting ...")
    crossref_data_pipeline = CrossrefDataPipeline()
    crossref_data_pipeline.ingest(
        arxiv_doi=message.arxiv_doi,
        arxiv_version=message.arxiv_version,
        title=message.title,
        author=message.author,
        start_date=message.start_date,
    )
    print("Message's Arxiv to Crossref DataPipeline is DONE")

def consume_messages(topic: str, group_id: str, bootstrap_servers: list = KAFKA_BROKER_URL):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='earliest',   # 從頭開始讀
        enable_auto_commit=True,        # 自動 commit offset
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # 假設是 JSON 格式
    )

    print(f"Start consuming from topic '{topic}'...")

    for msg in consumer:
        try:
            process_arxiv_to_crossref_message(msg.value)  # 傳給自定義處理邏輯
        except Exception as e:
            print(e)
            print('Do Some Error Handling Here ...')

if __name__ == "__main__":
    create_topic_if_needed(topic='arxiv-to-crossref')
    consume_messages(
        topic='arxiv-to-crossref',
        group_id='crossref-ingest-group'
    )

    # for dev
    # class KafkaDlqConsumer:
    #     def run_dlq_consumer(dlq_topic: str, group_id: str, kafka_brokers: List[str] = KAFKA_BROKER):
    #         consumer = KafkaConsumer(
    #             dlq_topic,
    #             bootstrap_servers=kafka_brokers,
    #             group_id=group_id,
    #             auto_offset_reset='earliest',
    #             enable_auto_commit=True,
    #             value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    #         )

    #         try:
    #             for message in consumer:
    #                 dlq_record = message.value

    #                 try:
    #                     validated_dlq_message = DlqMessage.model_validate(dlq_record)
    #                     print(f"  Original Message: {validated_dlq_message.original_message}")
    #                     print(f"  Error Type: {validated_dlq_message.error_type}")
    #                     print(f"  Error Details: {validated_dlq_message.error_details}")
    #                     print(f"  Timestamp: {validated_dlq_message.timestamp}")

    #                     print(f"--- DLQ Record Logged ---")
    #                     # Example: write to a file
    #                     # with open("dlq_errors.log", "a") as f:
    #                     #     f.write(json.dumps(dlq_record) + "\n")
    #                     # Example: send to Splunk/ELK
    #                     # send_to_logging_system(dlq_record)

    #                 except Exception as e:
    #                     print(f"Failed to parse DLQ message: {dlq_record}. Error: {e}")

    #         except KeyboardInterrupt:
    #             print("DLQ Consumer interrupted. Shutting down.")
    #         except Exception as e:
    #             print(f"DLQ Consumer encountered a critical error: {e}", exc_info=True)
    #         finally:
    #             consumer.close()
    #             print("DLQ Consumer closed.")
