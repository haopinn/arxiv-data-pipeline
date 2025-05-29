from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

with DAG(
    dag_id="arxiv_data_fetcher",
    start_date=datetime(2023, 1, 1),
    schedule_interval='* * * * *',
    catchup=False,
) as dag:
    arvix_data_fetcher = DockerOperator(
        task_id="arxiv_data_fetcher",
        image="arxiv-data-pipeline-kafka-consumer1:latest",
        container_name="airflow_arxiv_fetcher",
        api_version="auto",
        auto_remove='force',
        command="python /app/src/pipeline/arxiv_pipeline.py",  # 視 image 而定
        docker_url="unix://var/run/docker.sock",
        environment={
            "PATH": '/app/.venv/bin:$PATH',
            "PYTHONUNBUFFERED": '1',
            "PYTHONPATH": '/app/'
        },
        network_mode="bridge",
    )
