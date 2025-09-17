# DataOps Documentation

## Overview

This document provides comprehensive DataOps guidelines and practices for the Gill Capital Airflow Guardian Server. Our DataOps approach focuses on automation, monitoring, reliability, and collaboration across data engineering teams.

## Table of Contents

1. [DataOps Principles](#dataops-principles)
2. [Architecture Overview](#architecture-overview)
3. [Service Management](#service-management)
4. [Data Quality & Monitoring](#data-quality--monitoring)
5. [Deployment & CI/CD](#deployment--cicd)
6. [Security & Compliance](#security--compliance)
7. [Troubleshooting & Maintenance](#troubleshooting--maintenance)
8. [Team Collaboration](#team-collaboration)

## DataOps Principles

### 1. **Automation First**
- All data pipelines are automated through Airflow DAGs
- Infrastructure is containerized and reproducible
- Configuration management through environment variables
- Automated testing and validation

### 2. **Observability & Monitoring**
- Comprehensive logging across all services
- Health checks and alerting
- Performance monitoring and optimization
- Error tracking and resolution workflows

### 3. **Data Quality Assurance**
- Data validation at every stage
- Schema evolution management
- Data lineage tracking
- Automated quality checks

### 4. **Security & Compliance**
- Credential management through environment variables
- Audit logging for all operations
- Data privacy and protection
- Access control and permissions

### 5. **Collaboration & Documentation**
- Self-documenting code and configurations
- Clear service boundaries and interfaces
- Comprehensive documentation and runbooks
- Knowledge sharing and team onboarding

## Architecture Overview

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Airflow Guardian Server                   │
├─────────────────────────────────────────────────────────────┤
│  Services Layer                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Looker    │  │  BigQuery   │  │ Google Sheets│        │
│  │   Service   │  │   Service   │  │   Service    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  Orchestration Layer (Apache Airflow 2.9)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Scheduler │  │  Webserver   │  │   Worker    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │    Redis    │  │   Docker    │        │
│  │  Database   │  │   Broker    │  │ Containers  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
External Systems → Services → Airflow DAGs → Data Processing → Output/Storage
     ↓              ↓           ↓              ↓              ↓
  Looker API    Looker      Dashboard      Soft Delete    Audit Logs
  BigQuery      BigQuery    Sales Query    Data Export    GCS Backup
  Google Sheets Google      Sheet Trigger  Data Sync      Notifications
```

## Service Management

### Service Structure

Each service follows a standardized structure:

```
services/
├── {service_name}/
│   ├── scripts/           # Core business logic
│   ├── config/            # Configuration files
│   ├── docs/              # Service-specific documentation
│   ├── requirements.txt   # Python dependencies
│   └── requirements-airflow.txt  # Airflow-specific dependencies
```

### Current Services

#### 1. **Looker Service**
- **Purpose**: Dashboard lifecycle management and cleanup
- **Schedule**: Monthly (1st of each month)
- **DAG**: `looker_dashboard_deletion`
- **Features**: Soft delete, audit logging, safety modes

#### 2. **BigQuery Service**
- **Purpose**: Sales data queries and analytics
- **Schedule**: Manual trigger
- **DAG**: `bigquery_sales_query`
- **Features**: Data export, query optimization

#### 3. **Google Sheets Service**
- **Purpose**: Trigger-based data synchronization
- **Schedule**: Every 5 minutes
- **DAG**: `google_sheet_trigger_dag`
- **Features**: Real-time sync, error handling

## Data Quality & Monitoring

### Monitoring Strategy

1. **DAG Health Monitoring**
   - Success/failure rates
   - Execution time trends
   - Resource utilization

2. **Data Quality Checks**
   - Schema validation
   - Data completeness
   - Business rule validation

3. **Alerting Framework**
   - Email notifications for failures
   - Slack integration for critical alerts
   - Dashboard for real-time monitoring

### Logging Standards

```python
# Standard logging format across all services
import logging

logger = logging.getLogger(__name__)
logger.info(f"Operation started: {operation_name}")
logger.warning(f"Warning: {warning_message}")
logger.error(f"Error occurred: {error_details}")
```

## Deployment & CI/CD

### Docker-Based Deployment

```bash
# Development
docker compose up -d

# Production
docker compose -f docker-compose.prod.yml up -d
```

### Environment Management

- **Development**: Local Docker containers
- **Staging**: Cloud-based staging environment
- **Production**: Production-ready cloud deployment

### CI/CD Pipeline

1. **Code Commit** → GitHub
2. **Automated Testing** → Unit tests, integration tests
3. **Build** → Docker image creation
4. **Deploy** → Staging environment
5. **Validation** → Smoke tests, health checks
6. **Production** → Blue-green deployment

## Security & Compliance

### Credential Management

- All sensitive data stored in environment variables
- No hardcoded credentials in code
- Regular credential rotation
- Access audit logging

### Data Privacy

- Data anonymization where required
- Compliance with data protection regulations
- Secure data transmission
- Access control and permissions

## Troubleshooting & Maintenance

### Common Issues

1. **DAG Failures**
   - Check logs in Airflow UI
   - Verify environment variables
   - Test service connectivity

2. **Performance Issues**
   - Monitor resource utilization
   - Optimize query performance
   - Scale resources as needed

3. **Data Quality Issues**
   - Validate input data
   - Check business rules
   - Review data lineage

### Maintenance Procedures

- **Daily**: Monitor DAG executions and alerts
- **Weekly**: Review performance metrics and logs
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Architecture review and optimization

## Team Collaboration

### Development Workflow

1. **Feature Development**
   - Create feature branch
   - Implement changes
   - Add tests and documentation
   - Submit pull request

2. **Code Review Process**
   - Peer review required
   - Automated testing
   - Documentation review
   - Security review

3. **Deployment Process**
   - Staging deployment
   - Validation testing
   - Production deployment
   - Post-deployment monitoring

### Documentation Standards

- **Code Documentation**: Inline comments and docstrings
- **API Documentation**: OpenAPI/Swagger specifications
- **Architecture Documentation**: Diagrams and technical specifications
- **Runbooks**: Operational procedures and troubleshooting guides

## Best Practices

### Code Quality

- Follow PEP 8 Python style guide
- Use type hints for better code clarity
- Implement comprehensive error handling
- Write unit tests for all functions

### Data Pipeline Design

- Design for failure and recovery
- Implement idempotent operations
- Use appropriate data formats and compression
- Plan for data volume growth

### Monitoring & Alerting

- Set up proactive monitoring
- Define clear alert thresholds
- Implement escalation procedures
- Regular review of alert effectiveness

---

## Quick Reference

### Essential Commands

```bash
# Start services
./start_airflow.sh

# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart services
docker compose restart

# Access Airflow UI
open http://localhost:8080
```

### Key URLs

- **Airflow UI**: http://localhost:8080
- **GitHub Repository**: https://github.com/GillCapital/gc-airflow-guardian-server
- **Documentation**: ./docs/

### Emergency Contacts

- **Data Engineering Team**: [Team Contact]
- **DevOps Team**: [DevOps Contact]
- **On-Call Engineer**: [On-Call Contact]

---

*Last Updated: September 2024*
*Version: 1.0*
