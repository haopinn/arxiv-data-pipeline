import configparser
import os
from ast import literal_eval

# Set the current environment
config = configparser.RawConfigParser()
config.read('./src/config.ini')
PYTHON_CONFIG_SECTION_NAME = os.environ['PYTHON_CONFIG_SECTION_NAME']
config = config[PYTHON_CONFIG_SECTION_NAME]

# initialize specific variables
# --- Data Fetching ----
ARXIV_FETCHER_BATCH_SIZE=int(config['ARXIV_FETCHER_BATCH_SIZE'])
CROSSREF_API_SCORE_THRSLD=int(config['CROSSREF_API_SCORE_THRSLD'])
HTTP_RETRY_BACKOFF_FACTOR = float(config['HTTP_RETRY_BACKOFF_FACTOR'])

# --- Monitoring ---
PUSHGATEWAY_URL = config['PUSHGATEWAY_URL']

# --- Iceberg ----
ICEBERG_ARXIV_METADATA_TBL_NAME = config['ICEBERG_ARXIV_METADATA_TBL_NAME']
ICEBERG_ARXIV_NS_NAME=config['ICEBERG_ARXIV_NS_NAME']
ICEBERG_CROSSREF_AUTHOR_TBL_NAME = config['ICEBERG_CROSSREF_AUTHOR_TBL_NAME']
ICEBERG_CROSSREF_METADATA_TBL_NAME = config['ICEBERG_CROSSREF_METADATA_TBL_NAME']
ICEBERG_CROSSREF_REFERENCE_TBL_NAME = config['ICEBERG_CROSSREF_REFERENCE_TBL_NAME']
ICEBERG_REST_CATALOG_ENDPOINT = config['ICEBERG_REST_CATALOG_ENDPOINT']

# --- MinIO ---
S3_ENDPOINT = config['S3_ENDPOINT']
S3_ACCESS_KEY = config['S3_ACCESS_KEY']
S3_SECRET_KEY = config['S3_SECRET_KEY']

# --- Kafka ---
KAFKA_BROKER_URL = literal_eval(config['KAFKA_BROKER_URL'])
KAFKA_WORKER_PARTITIONS=int(config['KAFKA_WORKER_PARTITIONS'])
WORKER_ID = os.environ.get('WORKER_ID', '')

# --- Postgres ---
ARXIV_POSTGRES_URL=config['ARXIV_POSTGRES_URL']

# --- GX ---
GX_DIR = config['GX_DIR']
