import time
from typing import List

import pandas as pd
from prometheus_client import CollectorRegistry

from src.config import ICEBERG_ARXIV_METADATA_TBL_NAME
from src.data_fetcher.arxiv_fetcher import ArxivTaskManager, ArxivMetadataFetcher
from src.data_lineage.logger import DataLineageLogger
from src.data_processor.arxiv_parser import ArxivRawMetadataParser, ArxivMetadataTransformer
from src.data_validator.arxiv_validator import validate_arxiv_metadata
from src.kafka_message.arxiv_to_crossref_message import ArxivCrossrefMessageHandler
from src.schema.arxiv_schema import ArxivMetadata, ArxivRawMetadata
from src.schema_validator.metrics import MetricProvider
from src.storage.iceberg_storage import DataModelManager

class ArxivDataPipeline:
    def __init__(self):
        self.unix_timestamp = str(time.time())
        registry = CollectorRegistry()
        self.metrics_provider = MetricProvider(job_name='arxiv_parser', registry=registry, instance_name=self.unix_timestamp)
        self.data_lineage_logger = DataLineageLogger(job_name='arxiv', instance_id=self.unix_timestamp)

    def fetch(self, arxiv_task: dict) -> str:
        arxiv_metadata_fetcher = ArxivMetadataFetcher()
        arxiv_xml_filepath = arxiv_metadata_fetcher.fetch_and_save_arxiv_metadata(
            instance_name=self.unix_timestamp,
            **arxiv_task
        )
        self.data_lineage_logger.log_fetch(
            step_name='arxiv_api_fetch',
            source='arxiv_api',
            output=arxiv_xml_filepath,
            transformation='fetch_and_save_arxiv_metadata',
            record_count=None,
        )
        return arxiv_xml_filepath

    def parse(self, arxiv_xml_filepath: str) -> List[ArxivRawMetadata]:
        arxiv_raw_metadatas = ArxivRawMetadataParser.from_xml_filepath(
            xml_filepath=arxiv_xml_filepath,
            metrics_provider=self.metrics_provider
        )

        self.data_lineage_logger.log_parse(
            step_name='arxiv_api_parse',
            source=arxiv_xml_filepath,
            output='ArxivRawMetadata',
            transformation='ArxivRawMetadataParser.from_xml_filepath',
            record_count=len(arxiv_raw_metadatas),
        )

        return arxiv_raw_metadatas
    
    def transform(self, arxiv_raw_metadatas: List[ArxivRawMetadata]) -> List[ArxivMetadata]:
        arxiv_metadatas = ArxivMetadataTransformer.transform_from_list(
            arxiv_raw_metadatas=arxiv_raw_metadatas,
            metrics_provider=self.metrics_provider
        )

        self.data_lineage_logger.log_transformation(
            step_name='arxiv_api_transformation',
            source='ArxivRawMetadata',
            output='ArxivMetadata',
            transformation='ArxivMetadataTransformer.transform_from_list',
            record_count=len(arxiv_metadatas),
        )

        return arxiv_metadatas
    
    def concate_results(self, arxiv_metadatas: List[ArxivMetadata]) -> pd.DataFrame:
        arxiv_metadata_df = pd.concat([arxiv_metadata.to_dataframe() for arxiv_metadata in arxiv_metadatas], ignore_index=True)

        self.data_lineage_logger.log_transformation(
            step_name='arxiv_api_results_concatenation',
            source='ArxivMetadata',
            output='pd.DataFrame',
            transformation='pd.concat + ArxivMetadata.to_dataframe',
            record_count=arxiv_metadata_df.shape[0]
        )
        return arxiv_metadata_df
    
    def validate(self, arxiv_metadata_df: pd.DataFrame) -> bool:
        success, _ = validate_arxiv_metadata(arxiv_metadata_df)
        self.data_lineage_logger.log_validation(
            step_name='arxiv_api_validation',
            source='ArxivMetadata',
            transformation='validate_arxiv_metadata',
            validation_passed=success
        )
        return success
    
    def storage(self, arxiv_metadata_df: pd.DataFrame):
        DataModelManager.to_iceberg(arxiv_metadata_df, ICEBERG_ARXIV_METADATA_TBL_NAME)
        self.data_lineage_logger.log_storage(
            step_name='arxiv_api_storage',
            source='pd.Dataframe',
            output=ICEBERG_ARXIV_METADATA_TBL_NAME,
            record_count=arxiv_metadata_df.shape[0]
        )

    def publish_kafka(self, arxiv_metadatas: List[ArxivMetadata]):
        arxiv_crossref_message_handler = ArxivCrossrefMessageHandler()
        _ = [arxiv_crossref_message_handler.create_and_send(arxiv_metadata) for arxiv_metadata in arxiv_metadatas]
        self.data_lineage_logger.log_message_publish(
            step_name='arxiv_api_message_publish',
            source='pd.Dataframe',
            output=None,
            transformation="ArxivCrossrefMessageHandler.create_and_send"
        )

    def ingest(self):
        arxiv_task_manager = ArxivTaskManager()
        arxiv_task: dict = arxiv_task_manager.get_a_task()

        if not arxiv_task:
            print("There is none NOT DONE arxiv fetching task.")
            return 

        arxiv_xml_filepath = self.fetch(arxiv_task=arxiv_task)

        arxiv_raw_metadatas = self.parse(arxiv_xml_filepath)
        arxiv_metadatas = self.transform(arxiv_raw_metadatas=arxiv_raw_metadatas)

        if not arxiv_metadatas:
            print("There is no availables data rows for concating to metadata DataFrame ...")
            self.metrics_provider.push()
            return 
        
        arxiv_metadata_df = self.concate_results(arxiv_metadatas=arxiv_metadatas)
        validation_success = self.validate(arxiv_metadata_df=arxiv_metadata_df)

        if validation_success:
            self.storage(arxiv_metadata_df=arxiv_metadata_df)
            self.publish_kafka(arxiv_metadatas=arxiv_metadatas)
            arxiv_task_manager.mark_task_status()

        self.metrics_provider.push()

if __name__ == "__main__":
    arxiv_data_pipeline = ArxivDataPipeline()
    arxiv_data_pipeline.ingest()
    # for dev
    # arxiv_raw_metadatas = ArxivRawMetadataParser.from_xml_filepath(xml_filepath='./tmp_xml/0deb32df.xml')
    # arxiv_metadatas = ArxivMetadataTransformer.transform_from_list(arxiv_raw_metadatas=arxiv_raw_metadatas)

    # arxiv_metadata_df = pd.concat([arxiv_metadata.to_dataframe() for arxiv_metadata in arxiv_metadatas], ignore_index=True)
    # arxiv_metadata_df.iloc[0].to_dict()
