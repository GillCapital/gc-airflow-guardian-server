# GC Airflow Guardian Server

This repository serves as the central hub for managing and enforcing critical aspects of our data ecosystem within the Airflow environment. It encompasses data monitoring, retention policies, governance, and service integrations.

## 🏗️ Project Structure

```
gc-airflow-guardian-server/
├── dags/                           # Airflow DAG definitions
│   ├── bigquery_sales_query_dag.py
│   ├── google_sheet_trigger_dag.py
│   └── looker_dashboard_deletion_dag.py
├── services/                       # Service-specific modules and scripts
│   └── looker/                     # Looker dashboard management service
│       ├── scripts/               # Python modules and business logic
│       ├── config/                 # Configuration files
│       ├── docs/                   # Service-specific documentation
│       └── requirements-airflow.txt
├── plugins/                        # Airflow plugins and themes
│   └── my_theme_plugin/
├── config/                         # Global configuration (to be created)
├── logs/                          # Airflow logs (auto-generated)
├── docker-compose.yml             # Docker Compose configuration
├── Dockerfile                     # Custom Airflow image
├── start_airflow.sh              # Convenient startup script
└── README.md                      # This file
```

## 🎯 Purpose

This repository serves as the central hub for:

*   **Data Monitoring:** Implementing and managing systems for continuous oversight of data pipelines and data quality.
*   **Data Retention Policy:** Defining and enforcing policies for how long data is stored and when it should be archived or deleted.
*   **Governance:** Establishing and maintaining rules, processes, and responsibilities for data management and usage.
*   **Service Integrations:** Managing integrations with various data services like Looker, BigQuery, Google Sheets, etc.
*   **Looker Dashboard Management:** Tracking and managing the lifecycle of Looker dashboards, including handling deleted dashboards and their associated metadata.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Service-specific API credentials (see individual service documentation)
- Python 3.8+ (for local development)

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/GillCapital/gc-airflow-guardian-server.git
cd gc-airflow-guardian-server

# Copy environment templates for services that need them
cp services/looker/config/env.example services/looker/config/.env
# Edit the .env file with your credentials
nano services/looker/config/.env
```

### 2. Start Airflow Services

```bash
# Make the startup script executable
chmod +x start_airflow.sh

# Start all services
./start_airflow.sh
```

### 3. Access Airflow UI

- **URL**: http://localhost:8080
- **Username**: `airflow`
- **Password**: `airflow`

## 📊 Available DAGs

### 1. BigQuery Sales Query (`bigquery_sales_query`)
- **Purpose**: Execute BigQuery queries on sales data
- **Schedule**: Manual trigger
- **Tags**: `bigquery`, `sales`

### 2. Google Sheet Trigger (`google_sheet_trigger_dag`)
- **Purpose**: Monitor Google Sheets and trigger other DAGs based on sheet content
- **Schedule**: Every 5 minutes (`*/5 * * * *`)
- **Tags**: `google_sheet`, `trigger`, `gcs_bootstrapping`

### 3. Looker Dashboard Deletion (`looker_dashboard_deletion`)
- **Purpose**: Automatically identify and soft-delete inactive Looker dashboards
- **Schedule**: Monthly (1st of each month at midnight)
- **Tags**: `looker`, `cleanup`, `maintenance`
- **Tasks**:
  - `looker_dashboard_deletion_180_days`: Main deletion process
  - `send_notification`: Notification task

## 🔧 Service-Specific Configuration

### Looker Service

The Looker service manages dashboard lifecycle and cleanup operations.

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOOKER_BASE_URL` | Your Looker instance URL | Required |
| `LOOKER_CLIENT_ID` | Looker API Client ID | Required |
| `LOOKER_CLIENT_SECRET` | Looker API Client Secret | Required |
| `DAYS_BEFORE_SOFT_DELETE` | Days of inactivity before soft delete | 180 |
| `NOTIFICATION_EMAIL` | Email for notifications | Required |
| `GCS_BUCKET_NAME` | GCS bucket for backups | Optional |
| `GCP_PROJECT_ID` | GCP Project ID | Optional |
| `LOOKER_TIMEOUT` | Looker SDK timeout (seconds) | 300 |
| `TEST_MODE_LIMIT` | Limit for test mode | 10 |

#### Features

- **Professional Logging**: Structured logging with different levels
- **Error Handling**: Comprehensive error handling and recovery
- **Type Hints**: Full type annotations for better code quality
- **Configuration Management**: Centralized configuration using dataclasses
- **Safety Modes**: Test and safe modes for development and testing
- **Notifications**: Email notifications for execution results
- **Monitoring**: Detailed execution summaries and metrics

#### Safety Features

- **Test Mode**: Limits processing to first N dashboards
- **Safe Mode**: Simulates deletion without actually deleting
- **Dry Run**: Shows what would be deleted without making changes
- **Comprehensive Logging**: Detailed logs for audit trails
- **Error Recovery**: Continues processing even if individual dashboards fail

## 🛡️ Safety Features

- **Test Mode**: Limits processing to first N dashboards
- **Safe Mode**: Simulates deletion without actually deleting
- **Dry Run**: Shows what would be deleted without making changes
- **Comprehensive Logging**: Detailed logs for audit trails
- **Error Recovery**: Continues processing even if individual dashboards fail

## 📈 Monitoring

### Airflow UI

- **DAGs**: View DAG status and execution history
- **Tasks**: Monitor individual task execution
- **Logs**: View detailed execution logs
- **Variables**: Manage configuration variables

### Logs

Logs are stored in `logs/` and include:
- DAG execution logs
- Task execution logs
- Scheduler logs
- Webserver logs

## 🔄 Maintenance

### Regular Tasks

1. **Monitor DAG Execution**: Check execution results regularly
2. **Review Logs**: Monitor for errors or issues
3. **Update Credentials**: Rotate API credentials as needed
4. **Backup Configuration**: Keep configuration files backed up

### Troubleshooting

```bash
# View service status
docker compose ps

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop services
docker compose down
```

## 🚧 Adding New Services

To add a new service (e.g., `bigquery_retention`):

1. **Create Service Directory**:
   ```bash
   mkdir -p services/bigquery_retention/{scripts,config,docs}
   ```

2. **Add Service Files**:
   - `scripts/`: Python modules and business logic
   - `config/`: Configuration files and environment templates
   - `docs/`: Service-specific documentation
   - `requirements-airflow.txt`: Service dependencies

3. **Create DAG**:
   - Add DAG file to `dags/` directory
   - Import service modules from `/opt/airflow/services/bigquery_retention/scripts`

4. **Update Dockerfile**:
   - Add service-specific requirements if needed

5. **Update Documentation**:
   - Add service information to this README

## 📚 Documentation

- [Looker Service Documentation](services/looker/docs/README.md)
- [Airflow Setup Guide](services/looker/docs/AIRFLOW_SETUP.md)

## 🤝 Contributing

1. Follow Python best practices
2. Add type hints to all functions
3. Include comprehensive error handling
4. Update documentation for any changes
5. Test thoroughly before deployment
6. Use the established service structure for new services

## 📄 License

This project is for internal use at Gill Capital.

---

**Note**: Service-specific DAGs run in safe mode by default. To enable actual operations, modify the appropriate `safe_mode=True` parameter to `safe_mode=False` in the respective DAGs.