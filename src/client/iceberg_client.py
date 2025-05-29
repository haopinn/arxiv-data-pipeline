import os

from pyiceberg.catalog import load_catalog

from src.config import (
    ICEBERG_REST_CATALOG_ENDPOINT,
    S3_ENDPOINT,
    S3_ACCESS_KEY,
    S3_SECRET_KEY,
)

os.environ["PYICEBERG_S3_ENDPOINT"] = S3_ENDPOINT
os.environ["PYICEBERG_S3_ACCESS_KEY_ID"] = S3_ACCESS_KEY
os.environ["PYICEBERG_S3_SECRET_ACCESS_KEY"] = S3_SECRET_KEY
os.environ["PYICEBERG_S3_REGION"] = "us-east-1"
os.environ["PYICEBERG_S3_SECURE"] = "false"

# Define the catalog properties
catalog_properties = {
    "uri": ICEBERG_REST_CATALOG_ENDPOINT,
    "warehouse": "s3://warehouse",
    "s3.endpoint": S3_ENDPOINT,
    "s3.access-key-id": S3_ACCESS_KEY,
    "s3.secret-access-key": S3_SECRET_KEY,
    "s3.region": "us-east-1",
    "s3.ssl.enabled": "false",
}

catalog = load_catalog("default", **catalog_properties)
