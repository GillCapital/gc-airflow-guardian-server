# Operational Runbook

## Overview

This runbook provides step-by-step procedures for operating, monitoring, and troubleshooting the Gill Capital Airflow Guardian Server.

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Monitoring & Alerting](#monitoring--alerting)
3. [Troubleshooting Guide](#troubleshooting-guide)
4. [Maintenance Procedures](#maintenance-procedures)
5. [Emergency Procedures](#emergency-procedures)
6. [Performance Optimization](#performance-optimization)
7. [Security Operations](#security-operations)

## Daily Operations

### Morning Checklist (9:00 AM)

```bash
# 1. Check system health
docker compose ps

# 2. Review overnight DAG executions
curl -u airflow:airflow http://localhost:8080/api/v1/dags/looker_dashboard_deletion/runs

# 3. Check error logs
docker compose logs --tail=100 airflow-scheduler | grep ERROR

# 4. Verify resource utilization
docker stats --no-stream

# 5. Check disk space
df -h
```

### Afternoon Checklist (2:00 PM)

```bash
# 1. Review manual DAG triggers
curl -u airflow:airflow http://localhost:8080/api/v1/dags/bigquery_sales_query/runs

# 2. Check Google Sheets sync status
docker compose logs --tail=50 airflow-worker | grep "google_sheet"

# 3. Monitor performance metrics
docker compose logs airflow-scheduler | grep "execution_time"

# 4. Review alert notifications
tail -f logs/scheduler/latest/looker_dashboard_deletion_dag.py.log
```

### Evening Checklist (6:00 PM)

```bash
# 1. Backup critical data
docker exec postgres pg_dump -U airflow airflow > backup_$(date +%Y%m%d).sql

# 2. Review daily performance report
docker compose logs airflow-webserver | grep "performance"

# 3. Check for pending maintenance
docker compose logs airflow-scheduler | grep "maintenance"

# 4. Verify backup completion
ls -la backup_*.sql
```

## Monitoring & Alerting

### Key Metrics to Monitor

#### System Metrics
- **CPU Usage**: Should be < 80%
- **Memory Usage**: Should be < 85%
- **Disk Usage**: Should be < 90%
- **Network Latency**: Should be < 100ms

#### Application Metrics
- **DAG Success Rate**: Should be > 95%
- **Task Execution Time**: Monitor for anomalies
- **Queue Length**: Should be < 10 pending tasks
- **Error Rate**: Should be < 5%

#### Business Metrics
- **Looker Dashboards Processed**: Monthly count
- **BigQuery Queries Executed**: Daily count
- **Google Sheets Syncs**: Every 5 minutes
- **Data Quality Score**: Should be > 90%

### Alert Thresholds

```yaml
# Alert Configuration
alerts:
  critical:
    - cpu_usage > 90%
    - memory_usage > 95%
    - disk_usage > 95%
    - dag_failure_rate > 10%
  
  warning:
    - cpu_usage > 80%
    - memory_usage > 85%
    - disk_usage > 90%
    - dag_failure_rate > 5%
  
  info:
    - successful_dag_completion
    - backup_completion
    - maintenance_completion
```

### Monitoring Commands

```bash
# Check DAG status
curl -u airflow:airflow http://localhost:8080/api/v1/dags

# Check task instances
curl -u airflow:airflow http://localhost:8080/api/v1/dags/looker_dashboard_deletion/taskInstances

# Check system health
curl -u airflow:airflow http://localhost:8080/health

# Check logs
docker compose logs -f airflow-scheduler
```

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. DAG Not Starting

**Symptoms:**
- DAG shows as "No Status" in UI
- Scheduler logs show "DAG not found"

**Diagnosis:**
```bash
# Check DAG file syntax
python -m py_compile dags/looker_dashboard_deletion_dag.py

# Check DAG parsing
docker compose exec airflow-scheduler airflow dags list

# Check logs
docker compose logs airflow-scheduler | grep "looker_dashboard_deletion"
```

**Solution:**
```bash
# Restart scheduler
docker compose restart airflow-scheduler

# Refresh DAGs
docker compose exec airflow-scheduler airflow dags reserialize
```

#### 2. Task Failures

**Symptoms:**
- Tasks show as "Failed" in UI
- Error messages in logs

**Diagnosis:**
```bash
# Check task logs
docker compose logs airflow-worker | grep "ERROR"

# Check specific task
curl -u airflow:airflow http://localhost:8080/api/v1/dags/looker_dashboard_deletion/taskInstances/looker_dashboard_deletion_180_days/2024-01-01T00:00:00+00:00/logs/1

# Check dependencies
docker compose exec airflow-worker pip list | grep looker
```

**Solution:**
```bash
# Clear task instance
docker compose exec airflow-scheduler airflow tasks clear looker_dashboard_deletion looker_dashboard_deletion_180_days

# Restart worker
docker compose restart airflow-worker
```

#### 3. Database Connection Issues

**Symptoms:**
- "Connection refused" errors
- Database timeout errors

**Diagnosis:**
```bash
# Check database status
docker compose ps postgres

# Test connection
docker compose exec airflow-webserver airflow db check

# Check database logs
docker compose logs postgres | tail -50
```

**Solution:**
```bash
# Restart database
docker compose restart postgres

# Wait for database to be ready
docker compose exec postgres pg_isready -U airflow

# Restart Airflow services
docker compose restart airflow-webserver airflow-scheduler
```

#### 4. Memory Issues

**Symptoms:**
- Out of memory errors
- Slow performance
- Container restarts

**Diagnosis:**
```bash
# Check memory usage
docker stats --no-stream

# Check system memory
free -h

# Check container memory limits
docker inspect airflow-worker | grep -i memory
```

**Solution:**
```bash
# Increase memory limits in docker-compose.yml
services:
  airflow-worker:
    deploy:
      resources:
        limits:
          memory: 4G

# Restart with new limits
docker compose up -d --force-recreate airflow-worker
```

### Performance Issues

#### Slow DAG Execution

**Diagnosis:**
```bash
# Check execution times
docker compose logs airflow-scheduler | grep "execution_time"

# Check resource usage
docker stats --no-stream

# Check queue length
curl -u airflow:airflow http://localhost:8080/api/v1/dags/looker_dashboard_deletion/taskInstances
```

**Solutions:**
1. **Scale Workers:**
   ```bash
   # Add more workers
   docker compose up -d --scale airflow-worker=3
   ```

2. **Optimize Queries:**
   - Review BigQuery query performance
   - Add indexes to database tables
   - Optimize Looker API calls

3. **Resource Allocation:**
   ```bash
   # Increase CPU/memory limits
   docker compose up -d --force-recreate
   ```

## Maintenance Procedures

### Weekly Maintenance

#### Database Maintenance
```bash
# Vacuum database
docker compose exec postgres psql -U airflow -d airflow -c "VACUUM ANALYZE;"

# Check database size
docker compose exec postgres psql -U airflow -d airflow -c "SELECT pg_size_pretty(pg_database_size('airflow'));"

# Clean old logs
docker compose exec airflow-scheduler airflow db clean --clean-before-timestamp 2024-01-01
```

#### Log Rotation
```bash
# Rotate logs
docker compose exec airflow-scheduler find /opt/airflow/logs -name "*.log" -mtime +7 -delete

# Compress old logs
docker compose exec airflow-scheduler find /opt/airflow/logs -name "*.log" -mtime +3 -exec gzip {} \;
```

### Monthly Maintenance

#### Security Updates
```bash
# Update base images
docker compose pull

# Update Python packages
docker compose exec airflow-worker pip list --outdated

# Security scan
docker scout cves airflow-webserver
```

#### Performance Review
```bash
# Generate performance report
docker compose logs airflow-scheduler | grep "execution_time" > performance_report_$(date +%Y%m).txt

# Review resource utilization
docker stats --no-stream > resource_usage_$(date +%Y%m).txt
```

### Quarterly Maintenance

#### Architecture Review
- Review service performance
- Update documentation
- Plan capacity upgrades
- Security audit

#### Disaster Recovery Test
```bash
# Test backup restoration
docker compose down
docker volume rm gc-airflow-guardian-server_postgres_data
docker compose up -d postgres
docker compose exec postgres psql -U airflow -d airflow < backup_20240101.sql
```

## Emergency Procedures

### Service Outage

#### Immediate Response (0-15 minutes)
1. **Assess Impact:**
   ```bash
   # Check service status
   docker compose ps
   
   # Check error logs
   docker compose logs --tail=100 | grep ERROR
   ```

2. **Notify Team:**
   - Send alert to team Slack channel
   - Update status page
   - Escalate if critical

3. **Initial Recovery:**
   ```bash
   # Restart services
   docker compose restart
   
   # Check health
   curl -u airflow:airflow http://localhost:8080/health
   ```

#### Detailed Response (15-60 minutes)
1. **Root Cause Analysis:**
   - Review logs
   - Check system resources
   - Identify failure point

2. **Implement Fix:**
   - Apply configuration changes
   - Update code if needed
   - Restart affected services

3. **Verify Recovery:**
   - Test DAG execution
   - Monitor for 30 minutes
   - Confirm all services healthy

### Data Loss Prevention

#### Immediate Actions
```bash
# Stop all DAGs
docker compose exec airflow-scheduler airflow dags pause looker_dashboard_deletion
docker compose exec airflow-scheduler airflow dags pause bigquery_sales_query
docker compose exec airflow-scheduler airflow dags pause google_sheet_trigger_dag

# Create emergency backup
docker compose exec postgres pg_dump -U airflow airflow > emergency_backup_$(date +%Y%m%d_%H%M).sql
```

#### Recovery Actions
```bash
# Restore from backup
docker compose exec postgres psql -U airflow -d airflow < emergency_backup_20240101_1200.sql

# Verify data integrity
docker compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM dag_run;"

# Resume operations
docker compose exec airflow-scheduler airflow dags unpause looker_dashboard_deletion
```

## Performance Optimization

### Resource Optimization

#### CPU Optimization
```bash
# Check CPU usage per container
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Optimize worker count
# In docker-compose.yml:
services:
  airflow-worker:
    deploy:
      replicas: 2  # Adjust based on CPU cores
```

#### Memory Optimization
```bash
# Monitor memory usage
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Set memory limits
services:
  airflow-worker:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Query Optimization

#### BigQuery Optimization
```python
# Use query optimization techniques
def optimize_bigquery_query():
    # Use appropriate partitioning
    # Limit columns selected
    # Use WHERE clauses effectively
    # Consider materialized views
    pass
```

#### Looker API Optimization
```python
# Optimize API calls
def optimize_looker_calls():
    # Use pagination
    # Cache results
    # Batch operations
    # Use appropriate timeouts
    pass
```

## Security Operations

### Access Control

#### User Management
```bash
# List users
docker compose exec airflow-webserver airflow users list

# Create new user
docker compose exec airflow-webserver airflow users create \
    --username newuser \
    --firstname New \
    --lastname User \
    --role User \
    --email newuser@company.com \
    --password securepassword

# Update user role
docker compose exec airflow-webserver airflow users update \
    --username newuser \
    --role Admin
```

#### Permission Management
```bash
# Check DAG permissions
docker compose exec airflow-webserver airflow dags permissions

# Set DAG permissions
docker compose exec airflow-webserver airflow dags permissions \
    --dag-id looker_dashboard_deletion \
    --username newuser \
    --action can_read
```

### Security Monitoring

#### Audit Logging
```bash
# Check access logs
docker compose logs airflow-webserver | grep "login"

# Check API access
docker compose logs airflow-webserver | grep "api"

# Monitor failed logins
docker compose logs airflow-webserver | grep "failed"
```

#### Security Scanning
```bash
# Scan for vulnerabilities
docker scout cves airflow-webserver

# Check for security updates
docker compose exec airflow-worker pip list --outdated

# Review security logs
docker compose logs | grep -i "security\|auth\|permission"
```

---

## Quick Reference

### Essential Commands
```bash
# Start services
./start_airflow.sh

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart services
docker compose restart

# Access UI
open http://localhost:8080
```

### Emergency Contacts
- **On-Call Engineer**: [Phone Number]
- **Data Engineering Lead**: [Email]
- **DevOps Team**: [Slack Channel]
- **Security Team**: [Email]

### Key URLs
- **Airflow UI**: http://localhost:8080
- **Monitoring Dashboard**: [URL]
- **Documentation**: ./docs/
- **GitHub Repository**: https://github.com/GillCapital/gc-airflow-guardian-server

---

*Last Updated: September 2024*
*Version: 1.0*
