from typing import List, Optional

import pandas as pd

from src.client.kafka_producer_client import producer
from src.schema.arxiv_schema import ArxivMetadata
from src.schema.kafka_schema import ArxivToCrossrefMessage

class ArxivCrossrefMessageHandler:
    @staticmethod
    def concate_author_list(author_list: List[Optional[str]]) -> str:
        return '+'.join(author_list)
    
    @staticmethod
    def create_crossref_start_date(published_timestamp: str) -> str:
        if not published_timestamp:
            return ''
        published_datetime = pd.to_datetime(published_timestamp)
        return (published_datetime + pd.Timedelta(days=-30)).strftime("%Y-%m-%d")

    def create(self, arxiv_metadata: ArxivMetadata) -> ArxivToCrossrefMessage:
        arxiv_metadata_dict = arxiv_metadata.model_dump()
        author_list = arxiv_metadata_dict['authors']
        published_timestamp = arxiv_metadata_dict['published']
        arxiv_metadata_dict.update({"author": self.concate_author_list(author_list=author_list)})
        arxiv_metadata_dict.update({"start_date": self.create_crossref_start_date(published_timestamp=published_timestamp)})

        arxiv_crossref_message = ArxivToCrossrefMessage.model_validate(
            obj=arxiv_metadata_dict
        )  

        return arxiv_crossref_message

    @staticmethod
    def send(arxiv_crossref_message: ArxivToCrossrefMessage):
        producer.send("arxiv-to-crossref", value=arxiv_crossref_message.model_dump())
        producer.flush()
        print('kafka message sent')
    
    def create_and_send(self, arxiv_metadata: ArxivMetadata):
        arxiv_crossref_message = self.create(arxiv_metadata=arxiv_metadata)
        self.send(arxiv_crossref_message=arxiv_crossref_message)
