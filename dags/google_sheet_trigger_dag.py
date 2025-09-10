from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.suite.hooks.sheets import GoogleSheetsHook
from airflow.utils.dates import days_ago
from datetime import datetime
import logging

log = logging.getLogger(__name__)

def _process_google_sheet_and_trigger_dag(**kwargs):
    dag_run = kwargs['dag_run']
    # Get the DAG object to trigger it
    target_dag = kwargs['dag'].get_dag('gcs_bootstrapping_dag')

    # Configure your Google Sheet details
    spreadsheet_id = '1K34ZxTTg4nT-wvVBlXOpiNTssueFIheeV1LG7Deawps'  # Replace with your Google Sheet ID
    range_name = 'Sheet1!A:C'  # Adjust to your sheet name and columns (e.g., Country, Brand, Status)

    # Assumes columns are in order: Country, Brand, Status
    COUNTRY_COL_INDEX = 0
    BRAND_COL_INDEX = 1
    STATUS_COL_INDEX = 2

    hook = GoogleSheetsHook(gcp_conn_id='google_cloud_default') # Assumes google_cloud_default for Sheets API access

    # Read data from Google Sheet
    try:
        # Get current values to determine which rows to update
        current_data = hook.get_values(spreadsheet_id=spreadsheet_id, range_name=range_name)
        if not current_data:
            log.info("No data found in Google Sheet.")
            return
    except Exception as e:
        log.error(f"Error reading Google Sheet: {e}")
        raise

    # Prepare updates for the sheet
    # This will be a list of lists, where each inner list is a row to update
    # and its position corresponds to the row in the sheet.
    # We'll only update the status column.
    updates = []
    rows_to_trigger = []

    # Iterate through rows, starting from the second row if the first is a header
    # Assuming first row is header, adjust if not.
    start_row_index = 1 if current_data[0][STATUS_COL_INDEX].lower() in ['status', 'run', 'running', 'triggered', 'completed', 'failed'] else 0

    for i in range(start_row_index, len(current_data)):
        row = current_data[i]
        if len(row) > STATUS_COL_INDEX and row[STATUS_COL_INDEX].lower() == 'run':
            country = row[COUNTRY_COL_INDEX]
            brand = row[BRAND_COL_INDEX]

            log.info(f"Found 'run' status for Country: {country}, Brand: {brand}. Preparing to trigger DAG.")

            # Add to list of rows to trigger
            rows_to_trigger.append({
                'country': country,
                'brand': brand,
                'sheet_row_index': i # Store original sheet row index for updating status
            })

            # Mark this row for status update to 'running'
            # The Sheets API update_values method can take a list of lists for a range
            # We need to construct the updates carefully to match the sheet's structure.
            # For simplicity, we'll update one cell at a time.
            # A more efficient way would be to collect all updates and do a batch update.
            # For now, let's collect them and do a batch update at the end.
            updates.append({
                'range': f'Sheet1!{chr(ord("A") + STATUS_COL_INDEX)}{i + 1}', # +1 for 1-indexed row
                'values': [[ 'running' ]]
            })
        else:
            log.debug(f"Row {i} status is not 'run': {row}")

    # Perform batch update of statuses in Google Sheet
    if updates:
        log.info(f"Updating {len(updates)} rows in Google Sheet to 'running' status.")
        for update_item in updates:
            try:
                hook.update_values(
                    spreadsheet_id=spreadsheet_id,
                    range_name=update_item['range'],
                    values=update_item['values']
                )
            except Exception as e:
                log.error(f"Error updating Google Sheet for range {update_item['range']}: {e}")
                # Continue processing other updates even if one fails

    # Trigger the DAGs after updating statuses
    for trigger_data in rows_to_trigger:
        try:
            target_dag.trigger_dagrun(
                run_id=f"triggered_by_sheet_{trigger_data['country']}_{trigger_data['brand']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                conf={
                    'countries': trigger_data['country'],
                    'brand': trigger_data['brand'],
                    'dry_run': 0 # Always run for real when triggered from sheet
                }
            )
            log.info(f"Successfully triggered gcs_bootstrapping_dag for Country: {trigger_data['country']}, Brand: {trigger_data['brand']}")
        except Exception as e:
            log.error(f"Error triggering DAG for Country: {trigger_data['country']}, Brand: {trigger_data['brand']}: {e}")
            # Decide if you want to re-raise or just log and continue

with DAG(
    dag_id='google_sheet_trigger_dag',
    start_date=days_ago(1),
    schedule_interval='*/5 * * * *',  # Run every 5 minutes
    catchup=False,
    tags=['google_sheet', 'trigger', 'gcs_bootstrapping'],
) as dag:
    process_sheet_and_trigger = PythonOperator(
        task_id='process_sheet_and_trigger',
        python_callable=_process_google_sheet_and_trigger_dag,
        provide_context=True,
    )