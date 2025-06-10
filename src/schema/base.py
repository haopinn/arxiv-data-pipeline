from typing import get_args, get_origin, Optional, List
from src.schema_validator.base import MonitoredBaseModel

import pandas as pd
from pyiceberg.schema import Schema
from pyiceberg.types import (
    StringType,
    IntegerType,
    ListType,
    NestedField
)

class DataModelMixin(MonitoredBaseModel):
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(data=[self.model_dump()])

    @classmethod
    def empty_dataframe(cls) -> pd.DataFrame:
        return pd.DataFrame(columns=cls.model_fields.keys())

    @classmethod
    def to_iceberg_schema(cls) -> Schema:
        iceberg_fields = []
        element_id_counter = len(cls.__annotations__) + 1  # element_id 從 field_id 最大值 + 1 開始

        for idx, (name, annotation) in enumerate(cls.__annotations__.items(), start=1):
            origin = get_origin(annotation)
            args = get_args(annotation)

            if annotation in [str, Optional[str]] or (origin is Optional and str in args):
                iceberg_type = StringType()
            elif annotation in [int, Optional[int]] or (origin is Optional and int in args):
                iceberg_type = IntegerType()
            elif origin in [list, List]:
                iceberg_type = ListType(
                    element_id=element_id_counter,
                    element_type=StringType(),
                    element_required=False
                )
                element_id_counter += 1
            else:
                iceberg_type = StringType()

            iceberg_fields.append(
                NestedField(field_id=idx, name=name, field_type=iceberg_type, required=False)
            )

        return Schema(*iceberg_fields)
