from typing import List

import pandas as pd

from src.data_validator.base import AbstractValidator, ExpectationCallable

class ArxivMetadataValidator(AbstractValidator):
    def get_expectations(self) -> List[ExpectationCallable]:
        return [
            lambda v: v.expect_column_values_to_match_regex("arxiv_doi", r"^\d{4}\.\d{5}$"),
            lambda v: v.expect_column_values_to_be_between("arxiv_version", min_value=1),
            lambda v: v.expect_column_values_to_match_strftime_format("updated", "%Y-%m-%dT%H:%M:%SZ"),
            lambda v: v.expect_column_values_to_match_regex("publishded", r"^$|^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"),
        ]

def validate_arxiv_metadata(df: pd.DataFrame):
    return ArxivMetadataValidator(df, dataset_name="crossref_metadata").validate()
