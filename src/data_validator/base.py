from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Callable

import pandas as pd
import great_expectations as gx
from great_expectations.checkpoint import SimpleCheckpoint

from src.config import GX_DIR

ExpectationCallable = Callable[[object], None]

class AbstractValidator(ABC):
    def __init__(self, df: pd.DataFrame, dataset_name: str):
        self.df = df
        self.dataset_name = dataset_name
        self.context = gx.get_context(context_root_dir=GX_DIR)

    @abstractmethod
    def get_expectations(self) -> List[ExpectationCallable]:
        pass

    def validate(self) -> Tuple[bool, Dict]:
        datasource = self.context.sources.add_or_update_pandas(name=f"{self.dataset_name}_source")
        data_asset = datasource.add_dataframe_asset(name=f"{self.dataset_name}_asset", dataframe=self.df)
        batch_request = data_asset.build_batch_request()
        
        expectation_suite_name = f"{self.dataset_name}_expectations"
        self.context.add_or_update_expectation_suite(expectation_suite_name)

        validator = self.context.get_validator(
            batch_request=batch_request,
            expectation_suite_name=expectation_suite_name,
        )

        for expectation in self.get_expectations():
            expectation(validator)

        validator.save_expectation_suite(discard_failed_expectations=False)

        checkpoint = SimpleCheckpoint(
            name=f"{self.dataset_name}_validation_checkpoint",
            data_context=self.context,
            validations=[{
                "batch_request": batch_request,
                "expectation_suite_name": validator.get_expectation_suite().expectation_suite_name
            }],
        )
        result = checkpoint.run()
        return result["success"], result["run_results"]