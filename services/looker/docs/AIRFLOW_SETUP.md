# Airflow 2.9 Setup with Looker Dashboard Deletion DAG

## Overview

This setup provides a complete Airflow 2.9 environment with Docker that includes:
- **DAG Name**: `looker_dashboard_deletion`
- **Task Name**: `looker_dashboard_deletion_180_days`
- **Schedule**: Runs on the 1st of every month at midnight (`0 0 1 * *`)
- **Purpose**: Automatically identifies and soft deletes Looker dashboards inactive for 180+ days

## Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- At least 2 CPU cores
- At least 10GB free disk space

### 2. Setup Environment
```bash
# Copy environment configuration
cp env.example .env

# Edit .env file with your settings
nano .env
```

### 3. Start Airflow
```bash
# Initialize Airflow (first time only)
docker-compose up airflow-init

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Access Airflow Web UI
- **URL**: http://localhost:8080
- **Username**: airflow
- **Password**: airflow

### 5. Configure Variables (Optional)
In the Airflow UI, go to Admin > Variables and set:
- `LOOKER_BASE_URL`: Your Looker instance URL
- `LOOKER_CLIENT_ID`: Your Looker API client ID
- `LOOKER_CLIENT_SECRET`: Your Looker API client secret
- `DAYS_BEFORE_SOFT_DELETE`: Days threshold (default: 180)
- `NOTIFICATION_EMAIL`: Email for notifications

## DAG Details

### DAG Configuration
- **DAG ID**: `looker_dashboard_deletion`
- **Schedule**: `0 0 1 * *` (1st of every month at midnight)
- **Owner**: data-team
- **Tags**: looker, cleanup, maintenance
- **Max Active Runs**: 1

### Tasks
1. **`looker_dashboard_deletion_180_days`**: Main task that runs the dashboard deletion process
2. **`send_notification`**: Sends summary notification after completion

### Features
- ✅ **Safe Mode**: Default safe mode prevents accidental deletions
- ✅ **Production Ready**: Runs on all dashboards (not test mode)
- ✅ **Error Handling**: Comprehensive error handling and retries
- ✅ **Logging**: Detailed logging for monitoring
- ✅ **Notifications**: Email notifications on success/failure
- ✅ **Configurable**: Uses Airflow Variables for configuration

## File Structure

```
/Users/pinyapat.amornrattanaroj/looker/
├── docker-compose.yml              # Airflow services configuration
├── Dockerfile                      # Custom Airflow image with Looker dependencies
├── requirements-airflow.txt        # Python dependencies for Airflow
├── env.example                     # Environment configuration template
├── dags/
│   ├── looker_dashboard_deletion.py        # Original script (imported by DAG)
│   └── looker_dashboard_deletion_dag.py    # Airflow DAG definition
├── logs/                           # Airflow logs directory
├── config/                         # Airflow configuration directory
└── plugins/                        # Airflow plugins directory
```

## Usage

### Manual DAG Trigger
1. Go to Airflow UI (http://localhost:8080)
2. Find the `looker_dashboard_deletion` DAG
3. Click "Trigger DAG" to run manually

### Monitor Execution
1. Click on the DAG name
2. Click on the task name to see logs
3. Check the "Logs" tab for detailed output

### Enable Actual Deletion
To enable actual soft deletion (currently in safe mode):
1. Edit `dags/looker_dashboard_deletion_dag.py`
2. Change `safe_mode=True` to `safe_mode=False` in the task function
3. Redeploy the DAG

## Troubleshooting

### Common Issues

1. **Docker Build Fails**:
   ```bash
   # Check Docker daemon is running
   docker --version
   
   # Rebuild the image
   docker-compose build --no-cache
   ```

2. **DAG Not Appearing**:
   ```bash
   # Check DAG files are in correct location
   ls -la dags/
   
   # Check Airflow logs
   docker-compose logs airflow-scheduler
   ```

3. **Permission Issues**:
   ```bash
   # Fix file permissions
   sudo chown -R 50000:0 dags/ logs/ config/ plugins/
   ```

4. **Memory Issues**:
   - Ensure at least 4GB RAM available
   - Close other applications
   - Increase Docker memory limit

### Useful Commands

```bash
# View logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver

# Restart services
docker-compose restart airflow-scheduler
docker-compose restart airflow-webserver

# Stop all services
docker-compose down

# Remove all data (careful!)
docker-compose down -v
```

## Security Notes

- Change default Airflow credentials in production
- Store sensitive variables in Airflow Variables or external secret management
- Use HTTPS for Looker connections in production
- Regularly update dependencies

## Production Considerations

1. **External Database**: Use external PostgreSQL instead of Docker volume
2. **External Secrets**: Use HashiCorp Vault or AWS Secrets Manager
3. **Monitoring**: Add monitoring and alerting
4. **Backup**: Regular backup of Airflow metadata
5. **Scaling**: Use CeleryExecutor for horizontal scaling
