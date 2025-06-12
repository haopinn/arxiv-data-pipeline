import time
from typing import List, Tuple

import pandas as pd
from prometheus_client import CollectorRegistry

from src.config import (
    ICEBERG_CROSSREF_METADATA_TBL_NAME,
    ICEBERG_CROSSREF_REFERENCE_TBL_NAME,
    ICEBERG_CROSSREF_AUTHOR_TBL_NAME,
)
from src.data_fetcher.crossref_fetcher import CrossrefDataFetcher
from src.data_lineage.logger import DataLineageLogger
from src.data_processor.crossref_parser import (
    CrossrefAuthorTransformer,
    CrossrefMetadataTransformer,
    CrossrefReferenceTransformer,
)
from src.schema.crossref_schema import (
    CrossrefRawMetadata,
    CrossrefMetadata,
    CrossrefAuthor,
    CrossrefReference
)
from src.schema_validator.metrics import MetricProvider
from src.storage.iceberg_storage import DataModelManager

class CrossrefDataPipeline:
    def __init__(self):
        self.unix_timestamp = str(time.time())
        registry = CollectorRegistry()
        self.metrics_provider = MetricProvider(
            job_name='crossref_parser',
            registry=registry,
            instance_name=self.unix_timestamp
        )
        self.data_lineage_logger = DataLineageLogger(job_name='arxiv', instance_id=self.unix_timestamp)

    def fetch(self, title: str, author: str, start_date: str) -> CrossrefRawMetadata:
        crossref_data_fetcher = CrossrefDataFetcher(metrics_provider=self.metrics_provider)
        crossref_match_result = crossref_data_fetcher.find_fittest_crossref_result(
            title=title,
            author=author,
            start_date=start_date
        )

        self.data_lineage_logger.log_fetch(
            step_name='crossref_api_fetch',
            source='crossref_api',
            output="CrossrefRawMetadata",
            transformation='CrossrefDataFetcher.find_fittest_crossref_result',
            record_count=None,
        )

        return crossref_match_result

    def _transform_metadata(self, arxiv_doi: str, arxiv_version: int, raw_metadata: CrossrefRawMetadata) -> CrossrefMetadata:
        metadata_transformer = CrossrefMetadataTransformer()
        metadata = metadata_transformer.transform(arxiv_doi=arxiv_doi, arxiv_version=arxiv_version, crossref_raw_metadata=raw_metadata, metrics_provider=self.metrics_provider)

        self.data_lineage_logger.log_transformation(
            step_name='crossref_metadata_transformation',
            source='CrossrefRawMetadata',
            output='CrossrefMetadata',
            transformation='CrossrefMetadataTransformer.transform',
            record_count=1,
        )

        return metadata

    def _transform_author(self, raw_metadata: CrossrefRawMetadata) -> List[CrossrefAuthor]:
        author_transformer = CrossrefAuthorTransformer(metrics_provider=self.metrics_provider)
        authors = author_transformer.transform_from_list(doi=raw_metadata.doi, crossref_raw_author_list=raw_metadata.authors)

        self.data_lineage_logger.log_transformation(
            step_name='crossref_author_transformation',
            source='CrossrefRawMetadata',
            output='CrossrefAuthor',
            transformation='CrossrefAuthorTransformer.transform_from_list',
            record_count=len(authors),
        )

        return authors

    def _transform_reference(self, raw_metadata: CrossrefRawMetadata) -> List[CrossrefReference]:
        reference_transformer = CrossrefReferenceTransformer(metrics_provider=self.metrics_provider)
        references = reference_transformer.transform_from_list(doi=raw_metadata.doi, crossref_raw_reference_list=raw_metadata.references)

        self.data_lineage_logger.log_transformation(
            step_name='crossref_reference_transformation',
            source='CrossrefRawMetadata',
            output='CrossrefReference',
            transformation='CrossrefReferenceTransformer.transform_from_list',
            record_count=len(references),
        )

        return references

    def transform(self, crossref_match_result: CrossrefRawMetadata, arxiv_doi: str, arxiv_version: int) -> Tuple[List[CrossrefMetadata], List[CrossrefAuthor], List[CrossrefReference]]:
        raw_metadata = CrossrefRawMetadata.model_validate(crossref_match_result)
        metadata = self._transform_metadata(arxiv_doi=arxiv_doi, arxiv_version=arxiv_version, raw_metadata=raw_metadata)
        authors = self._transform_author(raw_metadata=raw_metadata)
        references = self._transform_reference(raw_metadata=raw_metadata)

        return metadata, authors, references
    
    def _concate_metadata_results(self, metadata: CrossrefMetadata) -> pd.DataFrame:
        metadata_df = metadata.to_dataframe()

        self.data_lineage_logger.log_transformation(
            step_name='crossref_metadata_results_concatenation',
            source='CrossrefMetadata',
            output='pd.DataFrame',
            transformation='CrossrefMetadata.to_dataframe',
            record_count=metadata_df.shape[0]
        )

        return metadata_df

    def _concate_author_results(self, authors: List[CrossrefAuthor]) -> pd.DataFrame:
        author_df = pd.concat([author.to_dataframe() for author in authors], ignore_index=True)

        self.data_lineage_logger.log_transformation(
            step_name='crossref_author_results_concatenation',
            source='CrossrefAuthor',
            output='pd.DataFrame',
            transformation='pd.concat + CrossrefAuthor.to_dataframe',
            record_count=author_df.shape[0]
        )

        return author_df

    def _concate_reference_results(self, references: List[CrossrefReference]) -> pd.DataFrame:
        references_df = pd.concat([reference.to_dataframe() for reference in references], ignore_index=True)

        self.data_lineage_logger.log_transformation(
            step_name='crossref_reference_results_concatenation',
            source='CrossrefReference',
            output='pd.DataFrame',
            transformation='pd.concat + CrossrefReference.to_dataframe',
            record_count=references_df.shape[0]
        )

        return references_df

    def concate_results(self, metadata: CrossrefMetadata, authors: List[CrossrefAuthor], references: List[CrossrefReference]) -> Tuple[pd.DataFrame]:
        metadata_df = self._concate_metadata_results(metadata=metadata)
        author_df = self._concate_author_results(authors=authors)
        reference_df = self._concate_reference_results(references=references)

        return metadata_df, author_df, reference_df
    
    def _storage_metadata(self, metadata_df: pd.DataFrame):
        DataModelManager.to_iceberg(metadata_df, ICEBERG_CROSSREF_METADATA_TBL_NAME)

        self.data_lineage_logger.log_storage(
            step_name='crossref_metadata_storage',
            source='pd.Dataframe',
            output=ICEBERG_CROSSREF_METADATA_TBL_NAME,
            record_count=metadata_df.shape[0]
        )

    def _storage_author(self, authors_df: pd.DataFrame):
        DataModelManager.to_iceberg(authors_df, ICEBERG_CROSSREF_AUTHOR_TBL_NAME)

        self.data_lineage_logger.log_storage(
            step_name='crossref_author_storage',
            source='pd.Dataframe',
            output=ICEBERG_CROSSREF_AUTHOR_TBL_NAME,
            record_count=authors_df.shape[0]
        )

    def _storage_refernece(self, references_df: pd.DataFrame):
        DataModelManager.to_iceberg(references_df, ICEBERG_CROSSREF_REFERENCE_TBL_NAME)

        self.data_lineage_logger.log_storage(
            step_name='crossref_reference_storage',
            source='pd.Dataframe',
            output=ICEBERG_CROSSREF_REFERENCE_TBL_NAME,
            record_count=references_df.shape[0]
        )

    def storage(self, metadata_df: pd.DataFrame, authors_df: pd.DataFrame, references_df: pd.DataFrame):
        self._storage_metadata(metadata_df=metadata_df)
        self._storage_author(authors_df=authors_df)
        self._storage_refernece(references_df=references_df)

    def ingest(self, arxiv_doi: str, arxiv_version: int, title: str, author: str, start_date: str):
        match_result = self.fetch(
            title=title,
            author=author,
            start_date=start_date
        )

        metadata, authors, references = self.transform(
            crossref_match_result=match_result,
            arxiv_doi=arxiv_doi,
            arxiv_version=arxiv_version
        )

        metadata_df, authors_df, references_df = self.concate_results(
            metadata=metadata,
            authors=authors,
            references=references
        )

        self.storage(
            metadata_df=metadata_df,
            authors_df=authors_df,
            references_df=references_df
        )

        self.metrics_provider.push()

if __name__ == "__main__":
    pass
    # for dev
    # i = 5
    # for i in range(10, 100):
    #     df_i = df.iloc[i]
    #     crossref_match_result = crossref_data_fetcher.find_fittest_crossref_result(
    #         title=df_i['title'],
    #         author='+'.join(df_i['authors']),
    #         start_date='2024-01-01'
    #     )
    #     if not crossref_match_result:
    #         continue
    #     metadata = metadata_transformer.transform(arxiv_doi='123', arxiv_version=123, crossref_raw_metadata=crossref_match_result)
    #     print(metadata.doi)

    