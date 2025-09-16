#!/bin/bash

# Looker Dashboard Deletion - Airflow Setup Script
# This script starts the Airflow services for the Looker dashboard deletion project

set -e

echo "🚀 Starting Looker Dashboard Deletion Airflow Services"
echo "=================================================="

# Set environment variables for Airflow UID/GID
export AIRFLOW_UID=$(id -u)
export AIRFLOW_GID=$(id -g)

echo "📁 Project Structure:"
echo "  - DAGs: ./dags/"
echo "  - Services: ./services/"
echo "  - Plugins: ./plugins/"
echo "  - Logs: ./logs/"
echo "  - Config: ./config/"
echo ""

# Check if .env files exist for services
if [ ! -f "services/looker/config/.env" ]; then
    echo "⚠️  Warning: .env file not found in services/looker/config/"
    echo "   Please copy services/looker/config/env.example to services/looker/config/.env and update with your credentials"
    echo ""
fi

# Initialize Airflow database and create admin user (only run once)
echo "🔧 Initializing Airflow database..."
docker compose up airflow-init

# Start all Airflow services in detached mode
echo "🚀 Starting Airflow services..."
docker compose up -d

echo ""
echo "✅ Airflow services started successfully!"
echo ""
echo "🌐 Access the Web UI at: http://localhost:8080"
echo "👤 Username: airflow"
echo "🔑 Password: airflow"
echo ""
echo "📊 Available DAGs:"
echo "  - bigquery_sales_query (Manual trigger)"
echo "  - google_sheet_trigger_dag (Every 5 minutes)"
echo "  - looker_dashboard_deletion (Monthly)"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop services: docker compose down"
echo "  - Restart services: docker compose restart"
echo ""
echo "🔍 Check service status:"
docker compose ps