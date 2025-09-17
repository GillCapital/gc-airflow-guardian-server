"""
Looker Dashboard Deletion DAG

This DAG runs monthly to identify and soft delete Looker dashboards
that haven't been accessed for more than 180 days (6 months).
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import os
import sys

# Add the services directory to Python path to import our module
sys.path.append('/opt/airflow/services/looker/scripts')

# Import our Looker dashboard deletion classes
from looker_dashboard_deletion import Config, LookerDashboardManager


# Default arguments for the DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email': ['pinyapat.a@hthai.co.th'],  # Update with your email
}

# Create the DAG
dag = DAG(
    'looker_dashboard_deletion',
    default_args=default_args,
    description='Monthly Looker dashboard cleanup - soft delete inactive dashboards',
    schedule_interval='0 0 1 * *',  # Run on the 1st of every month at midnight
    catchup=False,
    tags=['looker', 'cleanup', 'maintenance'],
    max_active_runs=1,
)


def create_config_from_variables():
    """Create Config object from Airflow Variables or use defaults."""
    try:
        config = Config(
            base_url=Variable.get("LOOKER_BASE_URL", default_var="https://gillcapital.cloud.looker.com/"),
            gcp_project_id=Variable.get("GCP_PROJECT_ID", default_var="gillcapital-datalake"),
            secret_name=Variable.get("LOOKER_SECRET_NAME", default_var="looker-pinyapat-client-id-secret"),
            days_before_soft_delete=int(Variable.get("DAYS_BEFORE_SOFT_DELETE", default_var=180)),
            notification_email=Variable.get("NOTIFICATION_EMAIL", default_var="pinyapat.a@hthai.co.th"),
            gcs_bucket_name=Variable.get("GCS_BUCKET_NAME", default_var="gc_looker_test"),
            timeout=int(Variable.get("LOOKER_TIMEOUT", default_var=300)),
            test_mode_limit=int(Variable.get("TEST_MODE_LIMIT", default_var=10))
        )
        return config
    except Exception as e:
        print(f"Error creating config: {e}")
        # Return default config if variables fail
        return Config()


def run_looker_dashboard_deletion(**context):
    """
    Main task function to run the Looker dashboard deletion process.
    
    Args:
        **context: Airflow context dictionary
        
    Returns:
        dict: Summary of the deletion process
    """
    try:
        # Get configuration
        config = create_config_from_variables()
        
        # Initialize dashboard manager
        manager = LookerDashboardManager(config)
        
        # Log start
        print("=" * 60)
        print("LOOKER DASHBOARD SOFT DELETE DAG")
        print("=" * 60)
        print(f"Execution Date: {context['ds']}")
        print(f"Days before soft delete: {config.days_before_soft_delete}")
        print(f"Notification email: {config.notification_email}")
        print("=" * 60)
        
        # Find inactive dashboards (run in production mode for DAG)
        print("Running in PRODUCTION MODE - checking all dashboards")
        inactive_dashboards = manager.find_inactive_dashboards(test_mode=False)
        
        if not inactive_dashboards:
            print("No inactive dashboards found.")
            return {
                'status': 'success',
                'inactive_count': 0,
                'processed_count': 0,
                'message': 'No inactive dashboards found'
            }
        
        print(f"\nFound {len(inactive_dashboards)} inactive dashboards:")
        for dashboard in inactive_dashboards:
            print(f"  - {dashboard['title']} (ID: {dashboard['id']})")
            print(f"    Last access: {dashboard['last_access']}")
        
        # Process inactive dashboards
        success_count = 0
        failed_count = 0
        
        for dashboard in inactive_dashboards:
            print(f"\nProcessing dashboard: {dashboard['title']}")
            try:
                # Run in safe mode by default - change to False for actual deletion
                if manager.soft_delete_dashboard(dashboard['id'], safe_mode=True):
                    success_count += 1
                    print(f"✅ Successfully processed: {dashboard['title']}")
                else:
                    failed_count += 1
                    print(f"❌ Failed to process: {dashboard['title']}")
            except Exception as e:
                failed_count += 1
                print(f"❌ Error processing {dashboard['title']}: {e}")
        
        # Summary
        summary = {
            'status': 'success' if failed_count == 0 else 'partial_success',
            'inactive_count': len(inactive_dashboards),
            'processed_count': success_count,
            'failed_count': failed_count,
            'message': f'Processed {success_count}/{len(inactive_dashboards)} dashboards successfully'
        }
        
        print(f"\n{'='*60}")
        print("EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total inactive dashboards found: {len(inactive_dashboards)}")
        print(f"Successfully processed: {success_count}")
        print(f"Failed to process: {failed_count}")
        print(f"Status: {summary['status']}")
        print(f"{'='*60}")
        
        return summary
        
    except Exception as e:
        error_msg = f"Error in dashboard deletion process: {e}"
        print(error_msg)
        return {
            'status': 'error',
            'inactive_count': 0,
            'processed_count': 0,
            'failed_count': 0,
            'message': error_msg
        }


def send_notification(**context):
    """
    Send notification about the dashboard deletion results.
    
    Args:
        **context: Airflow context dictionary
    """
    try:
        # Get the result from the previous task
        result = context['task_instance'].xcom_pull(task_ids='looker_dashboard_deletion_180_days')
        
        if result:
            print("=" * 60)
            print("NOTIFICATION SUMMARY")
            print("=" * 60)
            print(f"Execution Date: {context['ds']}")
            print(f"Status: {result['status']}")
            print(f"Total inactive dashboards: {result['inactive_count']}")
            print(f"Successfully processed: {result['processed_count']}")
            print(f"Failed: {result['failed_count']}")
            print(f"Message: {result['message']}")
            print("=" * 60)
            
            # Here you could add actual email notification logic
            # For now, we'll just log the summary
            
        else:
            print("No result found from previous task")
            
    except Exception as e:
        print(f"Error sending notification: {e}")


# Define the main task
looker_dashboard_deletion_task = PythonOperator(
    task_id='looker_dashboard_deletion_180_days',
    python_callable=run_looker_dashboard_deletion,
    dag=dag,
    provide_context=True,
)

# Define the notification task
notification_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    dag=dag,
    provide_context=True,
)

# Set up task dependencies
looker_dashboard_deletion_task >> notification_task
