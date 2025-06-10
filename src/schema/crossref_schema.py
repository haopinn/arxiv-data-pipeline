from typing import List, Optional
from pydantic import BaseModel, Field

from src.schema.base import DataModelMixin

class AuthorAffiliation(BaseModel):
    name: str = ''

class CrossrefRawAuthor(BaseModel):
    given: str = ''
    family: str = ''
    sequence: str = ''
    affiliation: List[AuthorAffiliation] = []

class CrossrefAuthor(DataModelMixin):
    # --- Identifiers ---
    doi: str
    sequence_index: int

    # --- Authors ---
    sequence_type: str # 'first' / 'additional'
    given_name: str
    family_name: str
    full_name: str
    affiliation: str

class CrossrefRawReference(DataModelMixin):
    # --- Identifiers ---
    doi: str = Field('', alias='DOI')

    # --- Authors ---
    author: str = ''

    # --- Title & Journal Info ---
    article_title: str = Field('', alias='artical-title')
    journal_title: str = Field('', alias='journal-title')
    volume_title: str = Field('', alias="volume-title")

    # --- Dates ---
    year: Optional[int] = None

    unstructured: str = ''
    
    class Config:
        extra = "ignore"

class CrossrefReference(DataModelMixin):
    doi: str
    ref_index: int
    ref_doi: str
    ref_author: str
    ref_year: Optional[int] = None
    ref_title: str
    ref_unstructured: str

class CrossrefRawMetadata(DataModelMixin):
    # --- Nested Schemas ---
    class SingleLink(BaseModel):
        url: str = Field('', alias='URL')
        class Config:
            extra = "ignore"

    class DateParts(BaseModel):
        date_parts: List[List[int]] = Field(..., alias='date-parts')
        class Config:
            extra = "ignore"

    # --- Identifiers ---
    doi: str = Field(..., alias='DOI')

    # --- Authors & References ---
    authors: List[Optional[CrossrefRawAuthor]] = Field([], alias='author')
    references: List[Optional[CrossrefRawReference]] = Field([], alias='reference')

    # --- Title & Journal Info ---
    publisher: str = ''
    title: List[Optional[str]] = []
    container_title: List[Optional[str]] = Field([], alias='container-title')

    # --- Dates ---
    issued: DateParts = [[]]
    published: DateParts = [[]]
    published_print: DateParts = Field([[]], alias='published-print')
    created: DateParts = [[]]

    # --- Metrics ---
    reference_count: Optional[int] = Field(None, alias='referenced-count')
    citation_count: Optional[int] = Field(None, alias='is-referenced-by-count')

    # --- IDs ---
    isbn: List[Optional[str]] = Field([], alias="ISBN")
    issn: List[Optional[str]] = Field([], alias="ISSN")

    # --- Page Info ---
    pages: str = Field('', alias='page')

    # --- Links ---
    fulltext_urls: List[SingleLink] = Field([SingleLink()], alias='link')

class CrossrefMetadata(DataModelMixin):
    # --- Identifiers ---
    doi: str
    arxiv_doi: str
    arxiv_version: int

    # --- Title & Journal Info ---
    publisher: str
    title: List[Optional[str]]
    container_title: List[Optional[str]]

    # --- Dates ---
    published_date: str

    # --- Metrics ---
    reference_count: Optional[int]
    citation_count: Optional[int]

    # --- IDs ---
    isbn: List[Optional[str]]
    issn: List[Optional[str]]
    
    # --- Page Info ---
    page_start: Optional[int]
    page_end: Optional[int]

    # --- Links ---
    fulltext_url: str
