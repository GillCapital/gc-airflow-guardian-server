# GCP Compute Engine Deployment Guide

## Overview

This guide covers deploying the Airflow Guardian Server on Google Cloud Platform Compute Engine with Secret Manager integration for secure credential management.

## Prerequisites

### 1. GCP Project Setup
- GCP Project: `gillcapital-datalake`
- Secret Manager API enabled
- Compute Engine API enabled
- Cloud Storage API enabled

### 2. Service Account Setup

Create a service account with the following roles:
```bash
# Create service account
gcloud iam service-accounts create airflow-guardian-sa \
    --display-name="Airflow Guardian Service Account" \
    --description="Service account for Airflow Guardian Server"

# Grant necessary roles
gcloud projects add-iam-policy-binding gillcapital-datalake \
    --member="serviceAccount:airflow-guardian-sa@gillcapital-datalake.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding gillcapital-datalake \
    --member="serviceAccount:airflow-guardian-sa@gillcapital-datalake.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding gillcapital-datalake \
    --member="serviceAccount:airflow-guardian-sa@gillcapital-datalake.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"
```

### 3. Secret Manager Setup

Create the Looker credentials secret:
```bash
# Create secret
gcloud secrets create looker-pinyapat-client-id-secret \
    --data-file=- <<EOF
{
  "client_id": "PPyDTxfQbstpn6smvrhC",
  "client_secret": "vJ4M8T32t5vn6pFNNWSHRHqW"
}
EOF

# Grant access to service account
gcloud secrets add-iam-policy-binding looker-pinyapat-client-id-secret \
    --member="serviceAccount:airflow-guardian-sa@gillcapital-datalake.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Compute Engine Deployment

### 1. Create Compute Engine Instance

```bash
# Create instance
gcloud compute instances create airflow-guardian-server \
    --zone=us-central1-a \
    --machine-type=e2-standard-4 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-standard \
    --service-account=airflow-guardian-sa@gillcapital-datalake.iam.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=airflow-server \
    --metadata=startup-script='#!/bin/bash
# Update system
apt-get update
apt-get install -y docker.io docker-compose git python3 python3-pip

# Start Docker
systemctl start docker
systemctl enable docker

# Add user to docker group
usermod -aG docker $USER

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Clone repository
git clone https://github.com/GillCapital/gc-airflow-guardian-server.git /opt/airflow-guardian
cd /opt/airflow-guardian

# Set up environment
cp config/gcp.env .env
chmod +x start_airflow.sh

# Start services
./start_airflow.sh'
```

### 2. Instance Configuration

```bash
# SSH into instance
gcloud compute ssh airflow-guardian-server --zone=us-central1-a

# Verify Docker installation
docker --version
docker-compose --version

# Verify GCP authentication
gcloud auth list
gcloud config get-value project
```

### 3. Environment Setup

```bash
# Navigate to project directory
cd /opt/airflow-guardian

# Set up environment variables
export GCP_PROJECT_ID=gillcapital-datalake
export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow-guardian/config/service-account-key.json

# Download service account key (if needed for local testing)
gcloud iam service-accounts keys create config/service-account-key.json \
    --iam-account=airflow-guardian-sa@gillcapital-datalake.iam.gserviceaccount.com
```

## Docker Compose for GCP

### 1. GCP-Optimized Docker Compose

Create `docker-compose.gcp.yml`:

```yaml
version: '3.8'

x-airflow-common:
  &airflow-common
  build: .
  environment: &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session'
    AIRFLOW__SCHEDULER__ENABLE_HEALTH_CHECK: 'true'
    _PIP_ADDITIONAL_REQUIREMENTS: ''
    # GCP Configuration
    GCP_PROJECT_ID: ${GCP_PROJECT_ID:-gillcapital-datalake}
    GOOGLE_APPLICATION_CREDENTIALS: /opt/airflow/config/service-account-key.json
    LOOKER_SECRET_NAME: ${LOOKER_SECRET_NAME:-looker-pinyapat-client-id-secret}
  volumes:
    - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
    - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
    - ${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config
    - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins
    - ${AIRFLOW_PROJ_DIR:-.}/services:/opt/airflow/services
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on: &airflow-common-depends-on
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - airflow_network

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command:
      - -c
      - |
        mkdir -p /sources/logs /sources/dags /sources/plugins /sources/services
        chown -R "${AIRFLOW_UID}:0" /sources/{logs,dags,plugins,services}
        exec /entrypoint airflow version
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow}
      _PIP_ADDITIONAL_REQUIREMENTS: ''
    user: "0:0"
    volumes:
      - ${AIRFLOW_PROJ_DIR:-.}:/sources

  airflow-webserver:
    <<: *airflow-common
    command: airflow webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 30s
      retries: 5
    restart: always
    networks:
      - airflow_network

  airflow-scheduler:
    <<: *airflow-common
    command: airflow scheduler
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 30s
      retries: 5
    restart: always
    networks:
      - airflow_network

volumes:
  postgres_data:

networks:
  airflow_network:
    driver: bridge
```

### 2. Start Services

```bash
# Start with GCP configuration
docker-compose -f docker-compose.gcp.yml up -d

# Check status
docker-compose -f docker-compose.gcp.yml ps

# View logs
docker-compose -f docker-compose.gcp.yml logs -f
```

## Security Configuration

### 1. Firewall Rules

```bash
# Allow Airflow web UI (restrict to specific IPs in production)
gcloud compute firewall-rules create allow-airflow-ui \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --target-tags airflow-server \
    --description "Allow Airflow web UI access"

# Allow SSH (restrict to specific IPs in production)
gcloud compute firewall-rules create allow-ssh \
    --allow tcp:22 \
    --source-ranges 0.0.0.0/0 \
    --target-tags airflow-server \
    --description "Allow SSH access"
```

### 2. SSL/TLS Configuration

For production deployment, consider:
- Using Cloud Load Balancer with SSL termination
- Implementing HTTPS for Airflow web UI
- Using Cloud SQL instead of local PostgreSQL

## Monitoring and Logging

### 1. Cloud Logging Integration

```bash
# Install Cloud Logging agent
curl -sSO https://dl.google.com/cloudagents/add-logging-agent-repo.sh
sudo bash add-logging-agent-repo.sh --also-install

# Configure logging
sudo systemctl enable google-fluentd
sudo systemctl start google-fluentd
```

### 2. Monitoring Setup

```bash
# Install Cloud Monitoring agent
curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh
sudo bash add-monitoring-agent-repo.sh --also-install

# Start monitoring
sudo systemctl enable stackdriver-agent
sudo systemctl start stackdriver-agent
```

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup script
cat > /opt/airflow-guardian/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/opt/airflow-guardian/backups/airflow_backup_${BACKUP_DATE}.sql"

mkdir -p /opt/airflow-guardian/backups

docker-compose exec -T postgres pg_dump -U airflow airflow > ${BACKUP_FILE}

# Upload to Cloud Storage
gsutil cp ${BACKUP_FILE} gs://gc_looker_test/backups/

echo "Backup completed: ${BACKUP_FILE}"
EOF

chmod +x /opt/airflow-guardian/backup_db.sh

# Schedule daily backups
echo "0 2 * * * /opt/airflow-guardian/backup_db.sh" | crontab -
```

### 2. Configuration Backup

```bash
# Backup configuration
gsutil -m rsync -r /opt/airflow-guardian/config/ gs://gc_looker_test/config/
gsutil -m rsync -r /opt/airflow-guardian/dags/ gs://gc_looker_test/dags/
```

## Troubleshooting

### 1. Common Issues

**Secret Manager Access Issues:**
```bash
# Test secret access
gcloud secrets versions access latest --secret="looker-pinyapat-client-id-secret"

# Check service account permissions
gcloud projects get-iam-policy gillcapital-datalake \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:airflow-guardian-sa@gillcapital-datalake.iam.gserviceaccount.com"
```

**Docker Issues:**
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check container logs
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

### 2. Performance Optimization

```bash
# Monitor resource usage
htop
docker stats

# Optimize PostgreSQL
docker-compose exec postgres psql -U airflow -d airflow -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
"
```

## Production Considerations

### 1. High Availability

- Use Cloud SQL for PostgreSQL
- Implement multiple Compute Engine instances
- Use Cloud Load Balancer for traffic distribution
- Set up automated failover

### 2. Security Hardening

- Restrict firewall rules to specific IP ranges
- Use Cloud IAM for fine-grained access control
- Implement VPC for network isolation
- Enable audit logging

### 3. Scaling

- Use managed instance groups for auto-scaling
- Implement horizontal pod autoscaling
- Monitor resource utilization
- Set up alerting for capacity planning

---

## Quick Commands

```bash
# Deploy to GCP
gcloud compute instances create airflow-guardian-server --zone=us-central1-a --machine-type=e2-standard-4

# SSH to instance
gcloud compute ssh airflow-guardian-server --zone=us-central1-a

# Start services
cd /opt/airflow-guardian && docker-compose -f docker-compose.gcp.yml up -d

# Check status
docker-compose -f docker-compose.gcp.yml ps

# View logs
docker-compose -f docker-compose.gcp.yml logs -f airflow-webserver
```

---

*This guide assumes familiarity with GCP and Docker. For production deployments, consider additional security and monitoring configurations.*
