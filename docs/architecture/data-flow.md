# Data Flow Architecture

## Overall Data Flow

```mermaid
flowchart TD
    subgraph "Data Sources"
        L_API[Looker API<br/>Dashboard Data]
        BQ_API[BigQuery API<br/>Sales Data]
        GS_API[Google Sheets API<br/>Sheet Data]
    end
    
    subgraph "Airflow Orchestration"
        AF_SCH[Scheduler]
        AF_WS[Webserver]
        AF_WK[Worker]
    end
    
    subgraph "Service Processing"
        L_SVC[Looker Service<br/>Dashboard Cleanup]
        BQ_SVC[BigQuery Service<br/>Sales Analytics]
        GS_SVC[Google Sheets Service<br/>Data Sync]
    end
    
    subgraph "Data Processing"
        VALIDATE[Data Validation]
        TRANSFORM[Data Transformation]
        QUALITY[Quality Checks]
    end
    
    subgraph "Output & Storage"
        AUDIT[Audit Logs]
        GCS[GCS Backup]
        EMAIL[Email Notifications]
        SHEETS[Updated Sheets]
        REPORTS[Analytics Reports]
    end
    
    L_API --> AF_SCH
    BQ_API --> AF_SCH
    GS_API --> AF_SCH
    
    AF_SCH --> AF_WS
    AF_SCH --> AF_WK
    
    AF_WK --> L_SVC
    AF_WK --> BQ_SVC
    AF_WK --> GS_SVC
    
    L_SVC --> VALIDATE
    BQ_SVC --> VALIDATE
    GS_SVC --> VALIDATE
    
    VALIDATE --> TRANSFORM
    TRANSFORM --> QUALITY
    
    QUALITY --> AUDIT
    QUALITY --> GCS
    QUALITY --> EMAIL
    QUALITY --> SHEETS
    QUALITY --> REPORTS
```

## Looker Service Data Flow

```mermaid
sequenceDiagram
    participant Scheduler as Airflow Scheduler
    participant LookerAPI as Looker API
    participant LookerSvc as Looker Service
    participant Database as PostgreSQL
    participant GCS as Google Cloud Storage
    participant Email as Email Service
    
    Scheduler->>LookerSvc: Trigger Monthly Cleanup
    LookerSvc->>LookerAPI: Get All Dashboards
    LookerAPI-->>LookerSvc: Dashboard List
    
    loop For Each Dashboard
        LookerSvc->>LookerAPI: Get Dashboard Details
        LookerAPI-->>LookerSvc: Dashboard Metadata
        LookerSvc->>LookerSvc: Check Last Access Date
        LookerSvc->>LookerSvc: Determine if Inactive
        
        alt Dashboard Inactive
            LookerSvc->>LookerAPI: Soft Delete Dashboard
            LookerAPI-->>LookerSvc: Deletion Confirmation
            LookerSvc->>Database: Log Deletion Event
            LookerSvc->>GCS: Backup Dashboard Data
            LookerSvc->>Email: Send Notification
        end
    end
    
    LookerSvc->>Database: Log Summary Report
    LookerSvc->>Email: Send Completion Report
```

## BigQuery Service Data Flow

```mermaid
sequenceDiagram
    participant User as User/Trigger
    participant Scheduler as Airflow Scheduler
    participant BQAPI as BigQuery API
    participant BQSvc as BigQuery Service
    participant Database as PostgreSQL
    participant Sheets as Google Sheets
    
    User->>Scheduler: Manual Trigger
    Scheduler->>BQSvc: Execute Sales Query
    BQSvc->>BQAPI: Run Sales Analytics Query
    BQAPI-->>BQSvc: Query Results
    
    BQSvc->>BQSvc: Process & Validate Data
    BQSvc->>Database: Store Query Metadata
    BQSvc->>Sheets: Update Sales Dashboard
    BQSvc->>Database: Log Execution Summary
```

## Google Sheets Service Data Flow

```mermaid
sequenceDiagram
    participant Scheduler as Airflow Scheduler
    participant SheetsAPI as Google Sheets API
    participant SheetsSvc as Google Sheets Service
    participant Database as PostgreSQL
    participant External as External Data Sources
    
    loop Every 5 Minutes
        Scheduler->>SheetsSvc: Trigger Sync
        SheetsSvc->>SheetsAPI: Check for Changes
        SheetsAPI-->>SheetsSvc: Change Detection
        
        alt Changes Detected
            SheetsSvc->>External: Fetch Updated Data
            External-->>SheetsSvc: Fresh Data
            SheetsSvc->>SheetsAPI: Update Sheets
            SheetsAPI-->>SheetsSvc: Update Confirmation
            SheetsSvc->>Database: Log Sync Event
        else No Changes
            SheetsSvc->>Database: Log No Changes
        end
    end
```

## Data Quality Pipeline

```mermaid
flowchart TD
    subgraph "Data Ingestion"
        RAW[Raw Data]
        SCHEMA[Schema Validation]
        FORMAT[Format Check]
    end
    
    subgraph "Data Processing"
        CLEAN[Data Cleaning]
        DEDUP[Deduplication]
        ENRICH[Data Enrichment]
    end
    
    subgraph "Quality Checks"
        COMPLETENESS[Completeness Check]
        ACCURACY[Accuracy Check]
        CONSISTENCY[Consistency Check]
        VALIDITY[Validity Check]
    end
    
    subgraph "Quality Gates"
        PASS[Quality Pass]
        FAIL[Quality Fail]
        REVIEW[Manual Review]
    end
    
    subgraph "Output"
        CLEAN_DATA[Clean Data]
        QUALITY_REPORT[Quality Report]
        ALERTS[Quality Alerts]
    end
    
    RAW --> SCHEMA
    SCHEMA --> FORMAT
    FORMAT --> CLEAN
    
    CLEAN --> DEDUP
    DEDUP --> ENRICH
    
    ENRICH --> COMPLETENESS
    COMPLETENESS --> ACCURACY
    ACCURACY --> CONSISTENCY
    CONSISTENCY --> VALIDITY
    
    VALIDITY --> PASS
    VALIDITY --> FAIL
    VALIDITY --> REVIEW
    
    PASS --> CLEAN_DATA
    FAIL --> QUALITY_REPORT
    REVIEW --> ALERTS
```

## Error Handling & Recovery Flow

```mermaid
flowchart TD
    subgraph "Error Detection"
        MONITOR[System Monitoring]
        ALERT[Alert Generation]
        CLASSIFY[Error Classification]
    end
    
    subgraph "Error Processing"
        RETRY[Automatic Retry]
        FALLBACK[Fallback Mechanism]
        ESCALATE[Escalation Process]
    end
    
    subgraph "Recovery Actions"
        RESTART[Service Restart]
        ROLLBACK[Data Rollback]
        NOTIFY[Team Notification]
    end
    
    subgraph "Resolution"
        FIX[Manual Fix]
        VERIFY[Verification]
        RESUME[Resume Processing]
    end
    
    MONITOR --> ALERT
    ALERT --> CLASSIFY
    
    CLASSIFY --> RETRY
    CLASSIFY --> FALLBACK
    CLASSIFY --> ESCALATE
    
    RETRY --> RESTART
    FALLBACK --> ROLLBACK
    ESCALATE --> NOTIFY
    
    RESTART --> FIX
    ROLLBACK --> FIX
    NOTIFY --> FIX
    
    FIX --> VERIFY
    VERIFY --> RESUME
```

## Data Lineage Tracking

```mermaid
graph LR
    subgraph "Source Systems"
        SRC1[Looker Dashboards]
        SRC2[BigQuery Tables]
        SRC3[Google Sheets]
    end
    
    subgraph "Processing Steps"
        STEP1[Data Extraction]
        STEP2[Data Transformation]
        STEP3[Data Validation]
        STEP4[Data Loading]
    end
    
    subgraph "Target Systems"
        TGT1[Audit Database]
        TGT2[GCS Storage]
        TGT3[Email Reports]
        TGT4[Updated Sheets]
    end
    
    subgraph "Metadata Tracking"
        META1[Extraction Metadata]
        META2[Transformation Metadata]
        META3[Validation Metadata]
        META4[Loading Metadata]
    end
    
    SRC1 --> STEP1
    SRC2 --> STEP1
    SRC3 --> STEP1
    
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> STEP4
    
    STEP4 --> TGT1
    STEP4 --> TGT2
    STEP4 --> TGT3
    STEP4 --> TGT4
    
    STEP1 --> META1
    STEP2 --> META2
    STEP3 --> META3
    STEP4 --> META4
```

## Performance Monitoring Flow

```mermaid
flowchart TD
    subgraph "Metrics Collection"
        CPU[CPU Usage]
        MEM[Memory Usage]
        DISK[Disk Usage]
        NET[Network Usage]
    end
    
    subgraph "Application Metrics"
        DAG_TIME[DAG Execution Time]
        TASK_TIME[Task Duration]
        SUCCESS_RATE[Success Rate]
        ERROR_RATE[Error Rate]
    end
    
    subgraph "Business Metrics"
        DATA_VOLUME[Data Volume Processed]
        QUALITY_SCORE[Data Quality Score]
        USER_SATISFACTION[User Satisfaction]
        SLA_COMPLIANCE[SLA Compliance]
    end
    
    subgraph "Monitoring Dashboard"
        REAL_TIME[Real-time Metrics]
        TRENDS[Trend Analysis]
        ALERTS[Alert Management]
        REPORTS[Performance Reports]
    end
    
    CPU --> REAL_TIME
    MEM --> REAL_TIME
    DISK --> REAL_TIME
    NET --> REAL_TIME
    
    DAG_TIME --> TRENDS
    TASK_TIME --> TRENDS
    SUCCESS_RATE --> TRENDS
    ERROR_RATE --> TRENDS
    
    DATA_VOLUME --> ALERTS
    QUALITY_SCORE --> ALERTS
    USER_SATISFACTION --> ALERTS
    SLA_COMPLIANCE --> ALERTS
    
    REAL_TIME --> REPORTS
    TRENDS --> REPORTS
    ALERTS --> REPORTS
```

## Data Security Flow

```mermaid
flowchart TD
    subgraph "Data Classification"
        PUBLIC[Public Data]
        INTERNAL[Internal Data]
        CONFIDENTIAL[Confidential Data]
        RESTRICTED[Restricted Data]
    end
    
    subgraph "Access Control"
        AUTH[Authentication]
        RBAC[Role-Based Access]
        PERM[Permissions Check]
        AUDIT[Access Audit]
    end
    
    subgraph "Data Protection"
        ENCRYPT[Data Encryption]
        MASK[Mask Sensitive Data]
        ANONYMIZE[Data Anonymization]
        BACKUP[Secure Backup]
    end
    
    subgraph "Compliance"
        GDPR[GDPR Compliance]
        SOX[SOX Compliance]
        HIPAA[HIPAA Compliance]
        AUDIT_LOG[Audit Logging]
    end
    
    PUBLIC --> AUTH
    INTERNAL --> AUTH
    CONFIDENTIAL --> AUTH
    RESTRICTED --> AUTH
    
    AUTH --> RBAC
    RBAC --> PERM
    PERM --> AUDIT
    
    AUDIT --> ENCRYPT
    ENCRYPT --> MASK
    MASK --> ANONYMIZE
    ANONYMIZE --> BACKUP
    
    BACKUP --> GDPR
    BACKUP --> SOX
    BACKUP --> HIPAA
    BACKUP --> AUDIT_LOG
```
