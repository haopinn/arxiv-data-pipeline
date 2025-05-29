from typing import List

import pandas as pd

from src.data_validator.base import AbstractValidator, ExpectationCallable

tommorrow_str = (pd.Timestamp.now() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

class CrossrefMetadataValidator(AbstractValidator):
    def get_expectations(self) -> List[ExpectationCallable]:
        tommorrow_str = (pd.Timestamp.now() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        return [
            # example doi: '10.30757/alea.v22-22'
            lambda v: v.expect_column_values_to_match_regex("doi", r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$"),
            lambda v: v.expect_column_values_to_be_between("arxiv_version", min_value=1),
            # updated is ISO format timestamp
            lambda v: v.expect_column_values_to_match_strftime_format("updated", "%Y-%m-%dT%H:%M:%SZ"),
            # published could be empty or in ISO format
            lambda v: v.expect_column_values_to_match_regex("publishded", r"^$|^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"),
            # page_start and page_end must > 0 & page_end must >= page_start
            lambda v: v.expect_column_values_to_be_between("page_start", min_value=1),
            lambda v: v.expect_column_values_to_be_between("page_end", min_value=1),
            lambda v: v.expect_column_pair_values_A_to_be_greater_than_B("page_end", "page_start", or_equal=True),
            # published_date is in 'YYYY-MM-DD' format and earlier than today
            lambda v: v.expect_column_values_to_match_strftime_format("published_date", "%Y-%m-%d"),
            lambda v: v.expect_column_values_to_be_less_than("published_date", tommorrow_str),
            lambda v: v.expect_column_values_to_be_between("reference_count", min_value=1),
            lambda v: v.expect_column_values_to_be_between("citation_count", min_value=1),
        ]

def validate_crossref_metadata(df: pd.DataFrame):
    return CrossrefMetadataValidator(df, dataset_name="crossref_metadata").validate()



class CrossrefReferenceValidator(AbstractValidator):
    def get_expectations(self) -> List[ExpectationCallable]:
        return [
            # pass for demo stage
        ]

def validate_crossref_reference(df: pd.DataFrame):
    return CrossrefReferenceValidator(df, dataset_name="crossref_reference").validate()


class CrossrefAuthorValidator(AbstractValidator):
    def get_expectations(self) -> List[ExpectationCallable]:
        return [
            # pass for demo stage
        ]

def validate_crossref_author(df: pd.DataFrame):
    return CrossrefAuthorValidator(df, dataset_name="crossref_author").validate()
