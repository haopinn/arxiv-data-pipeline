from pydantic import BaseModel, ValidationError
from typing import Optional

from prometheus_client import Counter

class MonitoredBaseModel(BaseModel):
    def __init__(
        __pydantic_self__,
        validation_attempt_counter: Optional[Counter] = None,
        validation_success_counter: Optional[Counter] = None,
        validation_error_counter: Optional[Counter] = None,
        default_value_used_counter: Optional[Counter] = None,
        **data,
    ):
        cls = __pydantic_self__.__class__

        if validation_attempt_counter:
            validation_attempt_counter.labels(model=cls.__name__).inc()

        if default_value_used_counter:
            for field_name, model_field in cls.model_fields.items():
                if model_field.alias not in data and field_name not in data:
                    # if default value is used
                    default_value_used_counter.labels(model=cls.__name__, field=field_name).inc()

        try:
            super().__init__(**data)
            if validation_success_counter:
                validation_success_counter.labels(model=cls.__name__).inc()
        except ValidationError as e:
            if validation_error_counter:
                for err in e.errors():
                    validation_error_counter.labels(
                        model=cls.__name__,
                        field='.'.join(str(i) for i in err.get('loc', ['unknown'])),
                        error_type=err.get('type', 'unknown')
                    ).inc()
            raise
