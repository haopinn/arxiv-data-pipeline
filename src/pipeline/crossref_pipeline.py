import pandas as pd

from src.config import (
    ICEBERG_CROSSREF_METADATA_TBL_NAME,
    ICEBERG_CROSSREF_REFERENCE_TBL_NAME,
    ICEBERG_CROSSREF_AUTHOR_TBL_NAME,
)
from src.data_fetcher.crossref_fetcher import CrossrefDataFetcher
from src.data_processor.crossref_parser import (
    CrossrefAuthorTransformer,
    CrossrefMetadataTransformer,
    CrossrefReferenceTransformer,
)
from src.schema.crossref_schema import (
    CrossrefRawMetadata
)
from src.storage.iceberg_storage import DataModelManager

class CrossrefDataPipeline:
    @staticmethod
    def ingest(arxiv_doi: str, arxiv_version: int, title: str, author: str, start_date: str):
        crossref_data_fetcher = CrossrefDataFetcher()
        crossref_match_result = crossref_data_fetcher.find_fittest_crossref_result(
            title=title,
            author=author,
            start_date=start_date
        )
        
        raw_metadata = CrossrefRawMetadata.model_validate(crossref_match_result)
        author_transformer = CrossrefAuthorTransformer()
        reference_transformer = CrossrefReferenceTransformer()
        metadata_transformer = CrossrefMetadataTransformer()

        metadata = metadata_transformer.transform(arxiv_doi=arxiv_doi, arxiv_version=arxiv_version, crossref_raw_metadata=raw_metadata)
        authors = author_transformer.transform_from_list(doi=raw_metadata.doi, crossref_raw_author_list=raw_metadata.authors)
        references = reference_transformer.transform_from_list(doi=raw_metadata.doi, crossref_raw_reference_list=raw_metadata.references)

        metadata_df = metadata.to_dataframe()
        authors_df = pd.concat([author.to_dataframe() for author in authors], ignore_index=True)
        references_df = pd.concat([reference.to_dataframe() for reference in references], ignore_index=True)

        DataModelManager.to_iceberg(metadata_df, ICEBERG_CROSSREF_METADATA_TBL_NAME)
        DataModelManager.to_iceberg(authors_df, ICEBERG_CROSSREF_AUTHOR_TBL_NAME)
        DataModelManager.to_iceberg(references_df, ICEBERG_CROSSREF_REFERENCE_TBL_NAME)

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

    