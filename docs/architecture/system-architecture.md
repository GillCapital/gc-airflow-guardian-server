# System Architecture Diagram

## High-Level Architecture

```mermaid
graph TB
    subgraph "External Systems"
        LS[Looker API]
        BQ[BigQuery]
        GS[Google Sheets API]
    end
    
    subgraph "Airflow Guardian Server"
        subgraph "Services Layer"
            LSV[Looker Service]
            BQSV[BigQuery Service]
            GSV[Google Sheets Service]
        end
        
        subgraph "Orchestration Layer"
            SCH[Scheduler]
            WS[Webserver]
            WK[Worker]
            TR[Triggerer]
        end
        
        subgraph "Infrastructure Layer"
            PG[PostgreSQL]
            RD[Redis]
            DC[Docker Containers]
        end
    end
    
    subgraph "Output & Storage"
        AL[Audit Logs]
        GCS[GCS Backup]
        NT[Notifications]
        DB[Data Warehouse]
    end
    
    LS --> LSV
    BQ --> BQSV
    GS --> GSV
    
    LSV --> SCH
    BQSV --> SCH
    GSV --> SCH
    
    SCH --> WS
    SCH --> WK
    SCH --> TR
    
    WS --> PG
    WK --> RD
    TR --> RD
    
    SCH --> AL
    SCH --> GCS
    SCH --> NT
    SCH --> DB
```

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph "Data Sources"
        A[Looker Dashboards]
        B[BigQuery Tables]
        C[Google Sheets]
    end
    
    subgraph "Processing Pipeline"
        D[Data Ingestion]
        E[Data Validation]
        F[Data Transformation]
        G[Data Quality Checks]
    end
    
    subgraph "Output Destinations"
        H[Cleaned Data]
        I[Audit Reports]
        J[Notifications]
        K[Backup Storage]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    E --> F
    F --> G
    
    G --> H
    G --> I
    G --> J
    G --> K
```

## Service Dependencies

```mermaid
graph TD
    subgraph "Airflow Core"
        AF[Airflow Scheduler]
        AW[Airflow Webserver]
        AWF[Airflow Worker]
    end
    
    subgraph "Data Services"
        LD[Looker Dashboard Deletion]
        BQ[BigQuery Sales Query]
        GS[Google Sheets Trigger]
    end
    
    subgraph "Infrastructure"
        PG[(PostgreSQL)]
        RD[(Redis)]
        DC[Docker Containers]
    end
    
    AF --> LD
    AF --> BQ
    AF --> GS
    
    AW --> PG
    AWF --> RD
    
    LD --> PG
    BQ --> PG
    GS --> PG
    
    DC --> AF
    DC --> AW
    DC --> AWF
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Local Docker]
        DEV_GIT[Git Repository]
    end
    
    subgraph "CI/CD Pipeline"
        BUILD[Docker Build]
        TEST[Automated Tests]
        STAGE[Staging Deploy]
    end
    
    subgraph "Production Environment"
        PROD[Production Containers]
        PROD_MON[Monitoring]
        PROD_LOG[Logging]
    end
    
    DEV_GIT --> BUILD
    BUILD --> TEST
    TEST --> STAGE
    STAGE --> PROD
    
    PROD --> PROD_MON
    PROD --> PROD_LOG
```

## Security Architecture

```mermaid
graph TB
    subgraph "External Access"
        USER[Users]
        API[External APIs]
    end
    
    subgraph "Security Layer"
        AUTH[Authentication]
        AUTHZ[Authorization]
        ENC[Encryption]
        AUDIT[Audit Logging]
    end
    
    subgraph "Application Layer"
        AF[Airflow Services]
        SVC[Business Services]
    end
    
    subgraph "Data Layer"
        DB[(Database)]
        STORAGE[File Storage]
        SECRETS[Secret Management]
    end
    
    USER --> AUTH
    API --> AUTH
    
    AUTH --> AUTHZ
    AUTHZ --> ENC
    ENC --> AUDIT
    
    AUDIT --> AF
    AF --> SVC
    
    SVC --> DB
    SVC --> STORAGE
    SVC --> SECRETS
```

## Monitoring & Observability

```mermaid
graph TB
    subgraph "Data Sources"
        DAG[DAG Executions]
        LOG[Application Logs]
        MET[Metrics]
        ALERT[Alerts]
    end
    
    subgraph "Collection Layer"
        AGENT[Monitoring Agents]
        EXPORTER[Metric Exporters]
        LOG_COLL[Log Collectors]
    end
    
    subgraph "Processing Layer"
        AGG[Aggregation]
        TRANS[Transformation]
        CORR[Correlation]
    end
    
    subgraph "Storage & Visualization"
        TSDB[Time Series DB]
        DASH[Dashboards]
        REPORTS[Reports]
    end
    
    subgraph "Alerting"
        RULES[Alert Rules]
        NOTIF[Notifications]
        ESC[Escalation]
    end
    
    DAG --> AGENT
    LOG --> LOG_COLL
    MET --> EXPORTER
    ALERT --> AGENT
    
    AGENT --> AGG
    EXPORTER --> AGG
    LOG_COLL --> TRANS
    
    AGG --> TSDB
    TRANS --> TSDB
    CORR --> TSDB
    
    TSDB --> DASH
    TSDB --> REPORTS
    
    TSDB --> RULES
    RULES --> NOTIF
    NOTIF --> ESC
```
