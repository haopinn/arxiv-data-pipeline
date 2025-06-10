from datetime import date
from typing import List, Tuple, Optional

from src.schema.crossref_schema import (
    CrossrefRawAuthor,
    CrossrefAuthor,
    CrossrefRawReference,
    CrossrefReference,
    CrossrefMetadata,
    CrossrefRawMetadata
)

from src.schema_validator.metrics import MetricProvider

class CrossrefAuthorTransformer:
    def __init__(self, metrics_provider: Optional[MetricProvider] = None):
        self.metrics_provider = metrics_provider

    def transform(self, doi: str, sequence_index: int, crossref_raw_author: CrossrefRawAuthor) -> CrossrefAuthor:
        given_name=crossref_raw_author.given
        family_name=crossref_raw_author.family

        counters = self.metrics_provider.get_counters() if self.metrics_provider else {}

        return CrossrefAuthor(
            doi=doi,
            given_name=given_name,
            family_name=family_name,
            full_name=f"{given_name} {family_name}",
            sequence_index=sequence_index,
            sequence_type=crossref_raw_author.sequence,
            affiliation=crossref_raw_author.affiliation[0].name, # for now, only take first affiliation name for example
            **counters
        )

    def transform_from_list(self, doi: str, crossref_raw_author_list: List[CrossrefRawAuthor]) -> List[CrossrefAuthor]:
        results = [
            self.transform(
                doi=doi,
                sequence_index=sequence_index,
                crossref_raw_author=crossref_raw_author,
            )
            for sequence_index, crossref_raw_author in enumerate(crossref_raw_author_list)
        ]

        return results


class CrossrefReferenceTransformer:
    def __init__(self, metrics_provider: Optional[MetricProvider] = None):
        self.metrics_provider = metrics_provider

    @staticmethod
    def determin_reference_title(crossref_raw_reference: CrossrefRawReference) -> str:
        ref_title = ''
        if crossref_raw_reference.article_title:
            ref_title = crossref_raw_reference.article_title
        elif crossref_raw_reference.volume_title:
            ref_title = crossref_raw_reference.volume_title
        elif crossref_raw_reference.unstructured:
            ref_title = crossref_raw_reference.unstructured.split(".")[1]
        return ref_title

    def transform(self, doi: str, ref_index: int, crossref_raw_reference: CrossrefRawReference) -> CrossrefReference:
        counters = self.metrics_provider.get_counters() if self.metrics_provider else {}

        return CrossrefReference(
            doi=doi,
            ref_index=ref_index,
            ref_doi=crossref_raw_reference.doi,
            ref_author=crossref_raw_reference.author,
            ref_year=crossref_raw_reference.year,
            ref_title=self.determin_reference_title(crossref_raw_reference=crossref_raw_reference),
            ref_unstructured=crossref_raw_reference.unstructured,
            **counters
        )

    def transform_from_list(self, doi: str, crossref_raw_reference_list: List[CrossrefRawReference]) -> List[CrossrefReference]:
        results = [
            self.transform(
                doi=doi,
                ref_index=ref_index,
                crossref_raw_reference=crossref_raw_refernece
            )
            for ref_index, crossref_raw_refernece in enumerate(crossref_raw_reference_list)
        ]


        return results

class CrossrefMetadataTransformer:
    @staticmethod
    def parse_pages(pages: str) -> Tuple[Optional[int]]:
        '''
        example: pages: '201-255'
        '''
        try:
            pages_int = tuple([int(page) for page in pages.split('-')])
            if len(pages_int) == 2:
                return pages_int
        except:
            return (None, None)

    @staticmethod
    def trim_date_parts(date_parts: List[int]) -> List[int]:
        # assume that date_parts should be [y: 2024, m: 2, d: 7]-like
        return [*date_parts, 1] if len(date_parts) == 2 else date_parts[:3]

    @staticmethod
    def get_publish_date(crossref_raw_metadata: CrossrefRawMetadata) -> str:
        for field in ['issued', 'published', 'published_print', 'created']:
            date_parts = getattr(crossref_raw_metadata, field)
            if isinstance(date_parts, CrossrefRawMetadata.DateParts):
                date_parts = date_parts.date_parts[0]
                if len(date_parts) == 1: # 如果只有年 -> 資料太少
                    continue
                trimmed_date_parts = CrossrefMetadataTransformer.trim_date_parts(date_parts)
                return date(*trimmed_date_parts).strftime('%Y-%m-%d')
        return ''

    def transform(self, arxiv_doi: str, arxiv_version: int, crossref_raw_metadata: CrossrefRawMetadata, metrics_provider: MetricProvider) -> CrossrefMetadata:
        page_start, page_end = self.parse_pages(crossref_raw_metadata.pages)

        counters = metrics_provider.get_counters() if metrics_provider else {}

        result = CrossrefMetadata(
            doi=crossref_raw_metadata.doi,
            arxiv_doi=arxiv_doi,
            arxiv_version=arxiv_version,
            publisher=crossref_raw_metadata.publisher,
            title=crossref_raw_metadata.title,
            published_date=self.get_publish_date(crossref_raw_metadata=crossref_raw_metadata),
            reference_count=crossref_raw_metadata.reference_count,
            citation_count=crossref_raw_metadata.citation_count,
            isbn=crossref_raw_metadata.isbn,
            issn=crossref_raw_metadata.issn,
            container_title=crossref_raw_metadata.container_title,
            page_start=page_start,
            page_end=page_end,
            fulltext_url=crossref_raw_metadata.fulltext_urls[0].url,
            **counters
        )

        return result
