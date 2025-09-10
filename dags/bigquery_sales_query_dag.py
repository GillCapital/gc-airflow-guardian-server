from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from datetime import datetime

with DAG(
    dag_id='bigquery_sales_query',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['bigquery', 'sales'],
) as dag:
    # Define your BigQuery project, dataset, and table
    gcp_project_id = 'gillcapital-datalake'
    bigquery_dataset_id = 'th_ls_central_on_saas'
    # The table name is now fully specified as 'lsc_trans_sales_entry' within the dataset 'th_ls_central_on_saas'
    bigquery_table_id = 'lsc_trans_sales_entry'

    # Example query: Select all data from the specified table
    # You can customize this query as needed
    sql_query = f"""
        SELECT *
        FROM `{gcp_project_id}.{bigquery_dataset_id}.{bigquery_table_id}`
        LIMIT 100
    """

    execute_bigquery_query = BigQueryExecuteQueryOperator(
        task_id='execute_sales_query',
        sql=sql_query,
        use_legacy_sql=False,  # Use standard SQL
        gcp_conn_id='google_cloud_default',  # Assumes a default GCP connection is configured in Airflow
    )