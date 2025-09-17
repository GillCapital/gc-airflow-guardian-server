# DAG Dependencies & Scheduling

## DAG Overview

```mermaid
gantt
    title Airflow DAG Schedule Overview
    dateFormat  YYYY-MM-DD
    section Looker Service
    Dashboard Deletion    :done, looker, 2024-01-01, 2024-12-31
    section BigQuery Service
    Sales Query          :manual, bq, 2024-01-01, 2024-12-31
    section Google Sheets Service
    Sheet Trigger        :active, gs, 2024-01-01, 2024-12-31
```

## DAG Execution Flow

```mermaid
flowchart TD
    subgraph "Scheduled DAGs"
        LD[Looker Dashboard Deletion<br/>Monthly: 1st at 00:00]
        GS[Google Sheets Trigger<br/>Every 5 minutes]
    end
    
    subgraph "Manual DAGs"
        BQ[BigQuery Sales Query<br/>Manual Trigger Only]
    end
    
    subgraph "Looker DAG Tasks"
        LD_START[Start Task]
        LD_MAIN[Dashboard Deletion Task]
        LD_END[End Task]
    end
    
    subgraph "BigQuery DAG Tasks"
        BQ_START[Start Task]
        BQ_MAIN[Sales Query Task]
        BQ_END[End Task]
    end
    
    subgraph "Google Sheets DAG Tasks"
        GS_START[Start Task]
        GS_MAIN[Sheet Trigger Task]
        GS_END[End Task]
    end
    
    LD --> LD_START
    LD_START --> LD_MAIN
    LD_MAIN --> LD_END
    
    BQ --> BQ_START
    BQ_START --> BQ_MAIN
    BQ_MAIN --> BQ_END
    
    GS --> GS_START
    GS_START --> GS_MAIN
    GS_MAIN --> GS_END
```

## Service Integration Points

```mermaid
graph LR
    subgraph "External APIs"
        L_API[Looker API]
        BQ_API[BigQuery API]
        GS_API[Google Sheets API]
    end
    
    subgraph "Airflow DAGs"
        L_DAG[looker_dashboard_deletion]
        BQ_DAG[bigquery_sales_query]
        GS_DAG[google_sheet_trigger_dag]
    end
    
    subgraph "Service Scripts"
        L_SCRIPT[looker_dashboard_deletion.py]
        BQ_SCRIPT[bigquery_sales_query.py]
        GS_SCRIPT[google_sheet_trigger.py]
    end
    
    subgraph "Output Systems"
        AUDIT[Audit Logs]
        GCS[GCS Storage]
        EMAIL[Email Notifications]
        SHEETS[Updated Sheets]
    end
    
    L_API --> L_DAG
    BQ_API --> BQ_DAG
    GS_API --> GS_DAG
    
    L_DAG --> L_SCRIPT
    BQ_DAG --> BQ_SCRIPT
    GS_DAG --> GS_SCRIPT
    
    L_SCRIPT --> AUDIT
    L_SCRIPT --> GCS
    L_SCRIPT --> EMAIL
    
    BQ_SCRIPT --> SHEETS
    BQ_SCRIPT --> AUDIT
    
    GS_SCRIPT --> SHEETS
    GS_SCRIPT --> AUDIT
```

## Resource Utilization Timeline

```mermaid
timeline
    title Daily Resource Usage Pattern
    
    section Morning (6-12)
        Low Usage    : BigQuery manual queries
                     : Google Sheets sync (every 5min)
    
    section Afternoon (12-18)
        Medium Usage : Manual DAG triggers
                     : Google Sheets sync continues
                     : Monitoring and alerts
    
    section Evening (18-24)
        Low Usage    : Google Sheets sync continues
                     : System maintenance
                     : Log analysis
    
    section Night (0-6)
        Peak Usage   : Looker cleanup (1st of month)
                     : Google Sheets sync continues
                     : Backup operations
```

## Error Handling & Recovery

```mermaid
flowchart TD
    START[DAG Execution Starts]
    
    START --> CHECK{Health Check}
    CHECK -->|Pass| EXECUTE[Execute Task]
    CHECK -->|Fail| RETRY{Retry Available?}
    
    RETRY -->|Yes| WAIT[Wait & Retry]
    RETRY -->|No| ALERT[Send Alert]
    
    WAIT --> CHECK
    
    EXECUTE --> SUCCESS{Task Success?}
    SUCCESS -->|Yes| NEXT[Next Task]
    SUCCESS -->|No| ERROR[Error Handling]
    
    ERROR --> LOG[Log Error]
    LOG --> NOTIFY[Notify Team]
    NOTIFY --> CLEANUP[Cleanup Resources]
    CLEANUP --> END[End DAG]
    
    NEXT --> FINAL{Final Task?}
    FINAL -->|No| EXECUTE
    FINAL -->|Yes| END
```

## Data Pipeline Dependencies

```mermaid
graph TB
    subgraph "Data Sources"
        L_DATA[Looker Dashboard Data]
        BQ_DATA[BigQuery Sales Data]
        GS_DATA[Google Sheets Data]
    end
    
    subgraph "Processing Stages"
        INGEST[Data Ingestion]
        VALIDATE[Data Validation]
        TRANSFORM[Data Transformation]
        QUALITY[Quality Checks]
    end
    
    subgraph "Output Stages"
        STORE[Data Storage]
        BACKUP[Data Backup]
        REPORT[Reporting]
        NOTIFY[Notifications]
    end
    
    L_DATA --> INGEST
    BQ_DATA --> INGEST
    GS_DATA --> INGEST
    
    INGEST --> VALIDATE
    VALIDATE --> TRANSFORM
    TRANSFORM --> QUALITY
    
    QUALITY --> STORE
    QUALITY --> BACKUP
    QUALITY --> REPORT
    QUALITY --> NOTIFY
```

## Monitoring & Alerting Flow

```mermaid
sequenceDiagram
    participant DAG as Airflow DAG
    participant MON as Monitoring System
    participant ALERT as Alert Manager
    participant TEAM as Team Notification
    participant LOG as Log System
    
    DAG->>MON: Execution Status
    MON->>LOG: Log Metrics
    
    alt Success
        MON->>LOG: Log Success Metrics
    else Failure
        MON->>ALERT: Trigger Alert
        ALERT->>TEAM: Send Notification
        TEAM->>LOG: Acknowledge Alert
    end
    
    MON->>LOG: Performance Metrics
    LOG->>TEAM: Generate Reports
```

## Service Health Monitoring

```mermaid
graph TB
    subgraph "Health Checks"
        HC_DAG[DAG Health]
        HC_API[API Connectivity]
        HC_DB[Database Health]
        HC_STORAGE[Storage Health]
    end
    
    subgraph "Monitoring Systems"
        PROM[Prometheus Metrics]
        GRAF[Grafana Dashboards]
        ALERT[Alert Manager]
    end
    
    subgraph "Notification Channels"
        EMAIL[Email Alerts]
        SLACK[Slack Notifications]
        PAGER[PagerDuty]
    end
    
    HC_DAG --> PROM
    HC_API --> PROM
    HC_DB --> PROM
    HC_STORAGE --> PROM
    
    PROM --> GRAF
    PROM --> ALERT
    
    ALERT --> EMAIL
    ALERT --> SLACK
    ALERT --> PAGER
```
