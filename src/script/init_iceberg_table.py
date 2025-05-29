from pyiceberg.partitioning import PartitionSpec, UNPARTITIONED_PARTITION_SPEC
from pyiceberg.schema import Schema

from src.client.iceberg_client import catalog
from src.config import ICEBERG_ARXIV_NS_NAME

def load_or_init_iceberg_table(
        table_name: str,
        table_schema: Schema = None,
        table_partition_spec: PartitionSpec = UNPARTITIONED_PARTITION_SPEC
    ):
    table_fullname = f"{ICEBERG_ARXIV_NS_NAME}.{table_name}"
    try:
        if not catalog.table_exists(table_fullname):
            table = catalog.create_table(
                table_fullname,
                schema=table_schema,
                partition_spec=table_partition_spec,
                properties={"format-version": "2"}, # Use V2 for more features
            )
            print(f"Created Iceberg table: {table_fullname}")
        else:
            table = catalog.load_table(table_fullname)
            print(f"Loaded existing Iceberg table: {table_fullname}")
        return table
    except Exception as e:
        print(f"Error managing table '{table_fullname}': {e}")
