import time

import pandas as pd
from prometheus_client import CollectorRegistry

from src.config import ICEBERG_ARXIV_METADATA_TBL_NAME
from src.data_fetcher.arxiv_fetcher import ArxivTaskManager, ArxivMetadataFetcher
from src.data_processor.arxiv_parser import ArxivRawMetadataParser, ArxivMetadataTransformer
from src.data_validator.arxiv_validator import validate_arxiv_metadata
from src.kafka_message.arxiv_to_crossref_message import ArxivCrossrefMessageHandler
from src.storage.iceberg_storage import DataModelManager
from src.schema_validator.metrics import MetricProvider

class ArxivDataPipeline:
    @staticmethod
    def ingest():
        arxiv_task_manager = ArxivTaskManager()
        arxiv_task = arxiv_task_manager.get_a_task()
        unix_timestamp = str(time.time())
        registry = CollectorRegistry()
        metrics_provider = MetricProvider(job_name='arxiv_parser', registry=registry, instance_name=unix_timestamp)

        if not arxiv_task:
            print("There is none NOT DONE arxiv fetching task.")
            return 

        arxiv_metadata_fetcher = ArxivMetadataFetcher()
        arxiv_xml_filepath = arxiv_metadata_fetcher.fetch_and_save_arxiv_metadata(
            instance_name=unix_timestamp,
            **arxiv_task
        )

        arxiv_raw_metadatas = ArxivRawMetadataParser.from_xml_filepath(
            xml_filepath=arxiv_xml_filepath,
            metrics_provider=metrics_provider
        )
        arxiv_metadatas = ArxivMetadataTransformer.transform_from_list(
            arxiv_raw_metadatas=arxiv_raw_metadatas,
            metrics_provider=metrics_provider
        )

        if not arxiv_metadatas:
            print("There is no availables data rows for concating to metadata DataFrame ...")
            metrics_provider.push()
            return 

        arxiv_metadata_df = pd.concat([arxiv_metadata.to_dataframe() for arxiv_metadata in arxiv_metadatas], ignore_index=True)

        # GX
        success, _ = validate_arxiv_metadata(arxiv_metadata_df)

        if success:
            DataModelManager.to_iceberg(arxiv_metadata_df, ICEBERG_ARXIV_METADATA_TBL_NAME)

            arxiv_crossref_message_handler = ArxivCrossrefMessageHandler()
            _ = [arxiv_crossref_message_handler.create_and_send(arxiv_metadata) for arxiv_metadata in arxiv_metadatas]

            arxiv_task_manager.mark_task_status()

        metrics_provider.push()



if __name__ == "__main__":
    ArxivDataPipeline.ingest()
    # for dev
    # arxiv_raw_metadatas = ArxivRawMetadataParser.from_xml_filepath(xml_filepath='./tmp_xml/0deb32df.xml')
    # arxiv_metadatas = ArxivMetadataTransformer.transform_from_list(arxiv_raw_metadatas=arxiv_raw_metadatas)

    # arxiv_metadata_df = pd.concat([arxiv_metadata.to_dataframe() for arxiv_metadata in arxiv_metadatas], ignore_index=True)
    # arxiv_metadata_df.iloc[0].to_dict()
