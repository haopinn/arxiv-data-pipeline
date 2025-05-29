from typing import Dict, Type

import pyarrow as pa
import pandas as pd

from src.schema.base import DataModelMixin
from src.schema.arxiv_schema import ArxivMetadata
from src.schema.crossref_schema import (
    CrossrefMetadata,
    CrossrefAuthor,
    CrossrefReference,
)
from src.script.init_iceberg_table import (
    load_or_init_iceberg_table
)

class DataModelFactory:
    """
    A factory class to provide the correct DataModelMixin subclass
    based on the Iceberg table name.
    """
    _model_map: Dict[str, Type[DataModelMixin]] = {
        'arxiv_metadata': ArxivMetadata,
        'crossref_author': CrossrefAuthor,
        'crossref_reference': CrossrefReference,
        'crossref_metadata': CrossrefMetadata,
    }

    @staticmethod
    def get_model_class(table_name: str) -> Type[DataModelMixin]:
        """
        Returns the DataModelMixin class corresponding to the given table name.
        """
        model_cls = DataModelFactory._model_map.get(table_name)
        if model_cls is None:
            raise ValueError(f"No DataModelMixin found for table name: '{table_name}'. "
                             "Please ensure it's registered in DataModelFactory.")
        return model_cls


class DataModelManager:
    data_model_factory = DataModelFactory()

    @staticmethod
    def to_iceberg(df: pd.DataFrame, iceberg_table_name: str):
        data_model = DataModelManager.data_model_factory.get_model_class(iceberg_table_name)
        data_schema = data_model.to_iceberg_schema()

        iceberg_table = load_or_init_iceberg_table(
            table_name=iceberg_table_name,
            table_schema=data_schema
        )

        arrow_table = pa.Table.from_pandas(
            df,
            schema=data_schema.as_arrow(),
            preserve_index=False
        )

        iceberg_table.append(arrow_table)

if __name__ == "__main__":
    from src.script.init_iceberg_table import catalog
    catalog.drop_table('arxiv_data.crossref_author')
    catalog.drop_table('arxiv_data.crossref_metadata')
    catalog.drop_table('arxiv_data.crossref_reference')


