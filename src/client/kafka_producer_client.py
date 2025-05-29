from kafka import KafkaProducer
import json

from src.config import KAFKA_BROKER_URL

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

if __name__ == "__main__":
    pass
    # for dev
    # producer = KafkaProducer(
    #     bootstrap_servers=KAFKA_BROKER_URL,
    #     value_serializer=lambda v: json.dumps(v).encode('utf-8')
    # )
    # # dlq_producer = KafkaProducer(bootstrap_servers=['kafka:19092'])

    # import pandas as pd
    # arxiv_metadata = pd.read_parquet('arxiv_metadata.parquet')
    # i = 1005
    # for i in range(2500, 2600):
    #     arxiv_doi = '2501.00684'
    #     arxiv_version = 1
    #     title = arxiv_metadata.iloc[i]['title']
    #     author = '+'.join(arxiv_metadata.iloc[i].authors)
    #     start_date = arxiv_metadata.iloc[i].published

    #     sample_msg = {
    #         "arxiv_doi": f"2305.5{i}",
    #         "arxiv_version": i,
    #         "title": title,
    #         "author": author,
    #         "start_date": start_date
    #     }

    #     producer.send("arxiv-to-crossref", value=sample_msg)
    #     producer.flush()

    # def handle_bad_message(message_value: Dict, dlq_topic: str, error: Exception, error_type: str):
    #     try:
    #         # 構造一個包含原始消息和錯誤信息的 DLQ 消息
    #         dlq_message = {
    #             "original_message": message_value,
    #             "error_type": error_type,
    #             "error_details": str(error),
    #             "timestamp": datetime.datetime.now().isoformat()
    #         }
    #         # 將其序列化為 JSON 字串
    #         dlq_message_bytes = json.dumps(dlq_message).encode('utf-8')
    #         # 發送到 DLQ topic
    #         dlq_producer.send('arxiv-to-crossref-dlq', value=dlq_message_bytes)
    #     except Exception as dlq_e:
    #         print(f"Failed to send message to DLQ. Original error: {error}. DLQ error: {dlq_e}")
