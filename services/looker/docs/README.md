# Looker Dashboard Soft Deletion Script

This script automatically identifies and soft deletes Looker dashboards that haven't been accessed for more than 6 months (180 days). It's designed to help maintain a clean dashboard environment by removing unused dashboards while preserving data for potential recovery.

**This is a production-ready, refactored version that follows Python best practices with proper logging, type hints, and object-oriented design.**

## Features

- 🔍 **Automatic Detection**: Identifies dashboards not accessed for 6+ months
- 🛡️ **Safe Mode**: Default safe mode prevents accidental deletions
- 📊 **Professional Logging**: Timestamped logging with proper levels
- ⚙️ **Configurable**: Easy to modify thresholds and settings via dataclass
- 🔄 **Test Mode**: Test with limited dashboards before full execution
- 🏗️ **Object-Oriented**: Clean class-based architecture
- 🔒 **Type Safe**: Full type hints for better code clarity
- 📧 **Notification Ready**: Prepared for email notifications

## Prerequisites

- Python 3.7+
- Looker SDK (`looker-sdk>=25.0.0`)
- Google Cloud Storage (`google-cloud-storage>=2.0.0`)
- Valid Looker API credentials
- Access to Looker instance

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Credentials**:
   Update the `Config` class in the script:
   ```python
   @dataclass
   class Config:
       base_url: str = "https://your-looker-instance.com/"
       client_id: str = "your_client_id"
       client_secret: str = "your_client_secret"
       # ... other settings
   ```

## Configuration

### Config Class
The script uses a `Config` dataclass for all settings:

```python
@dataclass
class Config:
    base_url: str = "https://gillcapital.cloud.looker.com/"
    client_id: str = "PPyDTxfQbstpn6smvrhC"
    client_secret: str = "vJ4M8T32t5vn6pFNNWSHRHqW"
    days_before_soft_delete: int = 180  # 6 months
    days_before_hard_delete: int = 180  # 6 months
    notification_email: str = "pinyapat.a@hthai.co.th"
    gcs_bucket_name: str = "gc_looker_test"
    gcp_project_id: str = "gillcapital-datamart"
    timeout: int = 300
    test_mode_limit: int = 10
```

### Environment Variables
The script automatically sets these environment variables from the config:

```python
LOOKERSDK_BASE_URL = config.base_url
LOOKERSDK_API_VERSION = "4.0"
LOOKERSDK_VERIFY_SSL = "true"
LOOKERSDK_TIMEOUT = str(config.timeout)
LOOKERSDK_CLIENT_ID = config.client_id
LOOKERSDK_CLIENT_SECRET = config.client_secret
```

## Usage

### 1. Test Mode (Recommended First Run)
```bash
python looker_dashboard_deletion.py
```
This runs in test mode, checking only the first 10 dashboards.

### 2. Production Mode
To run on all dashboards:

1. **Enable Production Mode**:
   ```python
   # In the main() function, change:
   inactive_dashboards = manager.find_inactive_dashboards(test_mode=False)
   ```

2. **Enable Soft Delete**:
   ```python
   # In the soft_delete_dashboard() method, change:
   manager.soft_delete_dashboard(dashboard['id'], safe_mode=False)
   ```

3. **Run the Script**:
   ```bash
   python looker_dashboard_deletion.py
   ```

## How It Works

### 1. Dashboard Detection
- Retrieves all dashboards from your Looker instance
- Checks each dashboard's `last_accessed_at` timestamp
- Falls back to `last_viewed_at` if `last_accessed_at` is not available
- Uses `created_at` as final fallback

### 2. Inactivity Check
- Calculates days since last access
- Compares against the threshold (default: 180 days)
- Identifies dashboards exceeding the threshold

### 3. Soft Deletion
- Marks dashboards as deleted using Looker's soft delete feature
- Preserves dashboard data for potential recovery
- Logs all actions for audit purposes

## Code Structure

```
looker_dashboard_deletion.py
├── Config (dataclass)
│   ├── Configuration parameters
│   └── Default values
├── LookerDashboardManager (class)
│   ├── SDK initialization
│   ├── Dashboard operations
│   ├── Logging setup
│   └── Error handling
├── Helper Functions
│   ├── print_configuration()
│   └── main()
└── Main Execution
    └── if __name__ == "__main__"
```

### Key Classes and Methods

- **`Config`**: Dataclass containing all configuration settings
- **`LookerDashboardManager`**: Main class handling all Looker operations
  - `get_dashboard_last_access()`: Retrieves dashboard access times
  - `is_dashboard_inactive()`: Checks inactivity threshold
  - `find_inactive_dashboards()`: Identifies inactive dashboards
  - `soft_delete_dashboard()`: Performs soft deletion

## Safety Features

### Safe Mode (Default)
```python
manager.soft_delete_dashboard(dashboard_id, safe_mode=True)  # Safe mode - no actual deletion
```

### Test Mode
```python
inactive_dashboards = manager.find_inactive_dashboards(test_mode=True)  # Test with limited dashboards
```

### Professional Logging
- Timestamped log entries
- Different log levels (INFO, ERROR, WARNING)
- Structured logging format

## Sample Output

```
============================================================
LOOKER DASHBOARD SOFT DELETE SCRIPT
============================================================
Configuration:
  - Days before soft delete: 180
  - Notification email: pinyapat.a@hthai.co.th
  - GCS Bucket: gc_looker_test
  - Timeout: 300s
============================================================
Looker SDK 4.0 initialized successfully.
Running in TEST MODE - checking only first 10 dashboards
2025-09-16 15:57:34,129 - __main__ - INFO - Fetching all dashboards...
2025-09-16 15:57:34,129 - __main__ - INFO - Checking 10 dashboards for inactivity...
2025-09-16 15:57:34,129 - __main__ - INFO - Checking dashboard: Thailand - MTD Country Sales Performance (ID: 2)
2025-09-16 15:57:35,762 - __main__ - INFO -   -> Active: Thailand - MTD Country Sales Performance
2025-09-16 15:57:35,762 - __main__ - INFO - Checking dashboard: Hourly sales (ID: 7)
2025-09-16 15:57:36,292 - __main__ - INFO -   -> Active: Hourly sales
...
No inactive dashboards found.
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**:
   - Increase `LOOKERSDK_TIMEOUT` value
   - Check network connectivity

2. **Authentication Errors**:
   - Verify API credentials
   - Check Looker instance URL

3. **Permission Errors**:
   - Ensure API user has dashboard management permissions
   - Check Looker admin settings

### Debug Mode
Add debug prints to troubleshoot:
```python
print(f"Dashboard {dashboard_id}: last_access = {last_access}")
print(f"Days since access: {days_since_access}")
```

## Customization

### Change Inactivity Threshold
```python
config = Config()
config.days_before_soft_delete = 365  # 1 year instead of 6 months
```

### Add Email Notifications
```python
def send_notification(manager, inactive_dashboards):
    # Add email notification logic here
    pass
```

### Filter Specific Dashboards
```python
def should_process_dashboard(dashboard):
    # Add custom filtering logic
    return not dashboard.title.startswith("TEMP_")
```

## Best Practices

1. **Always Test First**: Run in test mode before production
2. **Backup Important Dashboards**: Export critical dashboards before deletion
3. **Monitor Logs**: Review output for any unexpected behavior
4. **Schedule Regular Runs**: Set up cron job for automated execution
5. **Review Thresholds**: Adjust inactivity periods based on usage patterns

## Security Considerations

- **API Credentials**: Store securely, never commit to version control
- **Permissions**: Use minimal required permissions
- **Audit Trail**: Keep logs of all deletion activities
- **Recovery Plan**: Have a process to restore accidentally deleted dashboards

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Looker SDK documentation
3. Contact your Looker administrator

## License

This script is provided as-is for internal use. Please ensure compliance with your organization's policies and Looker's terms of service.
