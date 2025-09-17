#!/usr/bin/env python3
"""
Looker Dashboard Soft Deletion Script

This script automatically identifies and soft deletes Looker dashboards
that haven't been accessed for more than 6 months (180 days).

Updated to use Google Cloud Secret Manager for secure credential management.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from dataclasses import dataclass

import looker_sdk
from looker_sdk import models40 as models
from looker_sdk import error as looker_error

# Google Cloud imports
try:
    from google.cloud import secretmanager
    from google.auth import default
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    print("Warning: Google Cloud libraries not available. Install with: pip install google-cloud-secret-manager")


@dataclass
class Config:
    """Configuration class for the dashboard deletion script."""
    base_url: str = "https://gillcapital.cloud.looker.com/"
    gcp_project_id: str = "gillcapital-datalake"
    secret_name: str = "looker-pinyapat-client-id-secret"
    days_before_soft_delete: int = 180
    days_before_hard_delete: int = 180
    notification_email: str = "pinyapat.a@hthai.co.th"
    gcs_bucket_name: str = "gc_looker_test"
    timeout: int = 300
    test_mode_limit: int = 10
    # Credentials will be loaded from Secret Manager
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class LookerDashboardManager:
    """Manages Looker dashboard operations with GCP Secret Manager integration."""
    
    def __init__(self, config: Config):
        """Initialize the Looker SDK with configuration."""
        self.config = config
        self.logger = self._setup_logging()
        
        # Load credentials from Google Cloud Secret Manager
        self._load_credentials_from_secret_manager()
        
        # Initialize SDK after credentials are loaded
        self.sdk = self._initialize_sdk()
    
    def _load_credentials_from_secret_manager(self):
        """Load Looker credentials from Google Cloud Secret Manager."""
        try:
            if not GCP_AVAILABLE:
                raise ImportError("Google Cloud libraries not available")
            
            # Initialize Secret Manager client
            client = secretmanager.SecretManagerServiceClient()
            
            # Construct the secret name
            secret_name = f"projects/{self.config.gcp_project_id}/secrets/{self.config.secret_name}/versions/latest"
            
            self.logger.info(f"Loading credentials from Secret Manager: {secret_name}")
            
            # Access the secret
            response = client.access_secret_version(request={"name": secret_name})
            secret_data = response.payload.data.decode("UTF-8")
            
            # Parse JSON secret
            credentials = json.loads(secret_data)
            
            # Set credentials in config
            self.config.client_id = credentials.get("client_id")
            self.config.client_secret = credentials.get("client_secret")
            
            if not self.config.client_id or not self.config.client_secret:
                raise ValueError("Invalid credentials format in Secret Manager")
            
            self.logger.info("Successfully loaded credentials from Secret Manager")
            
        except Exception as e:
            self.logger.error(f"Failed to load credentials from Secret Manager: {e}")
            # Fallback to environment variables for local development
            self.config.client_id = os.getenv("LOOKER_CLIENT_ID")
            self.config.client_secret = os.getenv("LOOKER_CLIENT_SECRET")
            
            if not self.config.client_id or not self.config.client_secret:
                raise ValueError(
                    "Could not load credentials from Secret Manager or environment variables. "
                    "Ensure you have proper GCP authentication and the secret exists."
                )
            
            self.logger.warning("Using environment variables as fallback")
    
    def _initialize_sdk(self):
        """Initialize and configure the Looker SDK."""
        # Set environment variables
        os.environ.update({
            "LOOKERSDK_BASE_URL": self.config.base_url,
            "LOOKERSDK_API_VERSION": "4.0",
            "LOOKERSDK_VERIFY_SSL": "true",
            "LOOKERSDK_TIMEOUT": str(self.config.timeout),
            "LOOKERSDK_CLIENT_ID": self.config.client_id,
            "LOOKERSDK_CLIENT_SECRET": self.config.client_secret,
        })
        
        try:
            sdk = looker_sdk.init40()
            self.logger.info('Looker SDK 4.0 initialized successfully with GCP Secret Manager credentials.')
            return sdk
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Looker SDK: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_dashboard_last_access(self, dashboard_id: str) -> Optional[datetime]:
        """
        Get the last access time for a dashboard.
        
        Args:
            dashboard_id: The ID of the dashboard
            
        Returns:
            The last access time as a datetime object, or None if error
        """
        try:
            dashboard = self.sdk.dashboard(dashboard_id=dashboard_id)
            
            # Priority: last_accessed_at > last_viewed_at > created_at
            if hasattr(dashboard, 'last_accessed_at') and dashboard.last_accessed_at:
                return dashboard.last_accessed_at
            elif hasattr(dashboard, 'last_viewed_at') and dashboard.last_viewed_at:
                return dashboard.last_viewed_at
            else:
                return dashboard.created_at
                
        except Exception as e:
            self.logger.error(f"Error getting dashboard info for {dashboard_id}: {e}")
            return None
    
    def get_all_dashboards(self, limit: Optional[int] = None) -> List:
        """
        Get all dashboards from Looker.
        
        Args:
            limit: Optional limit on number of dashboards to return
            
        Returns:
            List of dashboard objects
        """
        try:
            dashboards = self.sdk.all_dashboards()
            if limit:
                dashboards = dashboards[:limit]
            return dashboards
        except Exception as e:
            self.logger.error(f"Error getting dashboards: {e}")
            return []
    
    def is_dashboard_inactive(self, dashboard_id: str, days_threshold: Optional[int] = None) -> bool:
        """
        Check if a dashboard has been inactive for more than the threshold days.
        
        Args:
            dashboard_id: The ID of the dashboard
            days_threshold: Days threshold for inactivity (defaults to config value)
            
        Returns:
            True if dashboard is inactive, False otherwise
        """
        if days_threshold is None:
            days_threshold = self.config.days_before_soft_delete
            
        last_access = self.get_dashboard_last_access(dashboard_id)
        if not last_access:
            return False
        
        # Convert to datetime if it's a string
        if isinstance(last_access, str):
            last_access = datetime.fromisoformat(last_access.replace('Z', '+00:00'))
        
        # Calculate days since last access
        days_since_access = (datetime.now(last_access.tzinfo) - last_access).days
        
        return days_since_access > days_threshold
    
    def soft_delete_dashboard(self, dashboard_id: str, safe_mode: bool = True) -> bool:
        """
        Soft delete the given dashboard.
        
        Args:
            dashboard_id: The ID of the dashboard to delete
            safe_mode: If True, doesn't actually delete (default: True)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Safe mode prevents actual deletion
            deleted_status = False if safe_mode else True
            dashboard = models.WriteDashboard(deleted=deleted_status)
            
            self.sdk.update_dashboard(dashboard_id, body=dashboard)
            
            if safe_mode:
                self.logger.info(f"SAFE MODE: Would soft delete dashboard: {dashboard_id}")
            else:
                self.logger.info(f"Successfully soft deleted dashboard: {dashboard_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error soft deleting dashboard ({dashboard_id}): {e}")
            return False
    
    def find_inactive_dashboards(self, test_mode: bool = False) -> List[Dict[str, Union[str, datetime]]]:
        """
        Find all dashboards that haven't been accessed for more than the threshold.
        
        Args:
            test_mode: If True, limits to first few dashboards for testing
            
        Returns:
            List of inactive dashboard dictionaries
        """
        self.logger.info("Fetching all dashboards...")
        limit = self.config.test_mode_limit if test_mode else None
        dashboards = self.get_all_dashboards(limit=limit)
        
        if not dashboards:
            self.logger.info("No dashboards found.")
            return []
        
        inactive_dashboards = []
        self.logger.info(f"Checking {len(dashboards)} dashboards for inactivity...")
        
        for dashboard in dashboards:
            try:
                dashboard_id = str(dashboard.id)
                dashboard_title = dashboard.title
                
                self.logger.info(f"Checking dashboard: {dashboard_title} (ID: {dashboard_id})")
                
                if self.is_dashboard_inactive(dashboard_id):
                    inactive_dashboards.append({
                        'id': dashboard_id,
                        'title': dashboard_title,
                        'last_access': self.get_dashboard_last_access(dashboard_id)
                    })
                    self.logger.info(f"  -> INACTIVE: {dashboard_title}")
                else:
                    self.logger.info(f"  -> Active: {dashboard_title}")
                    
            except Exception as e:
                self.logger.error(f"Error checking dashboard {dashboard.id}: {e}")
                continue
        
        return inactive_dashboards


def print_configuration(config: Config) -> None:
    """Print the current configuration."""
    print("=" * 60)
    print("LOOKER DASHBOARD SOFT DELETE SCRIPT")
    print("=" * 60)
    print("Configuration:")
    print(f"  - Days before soft delete: {config.days_before_soft_delete}")
    print(f"  - Notification email: {config.notification_email}")
    print(f"  - GCS Bucket: {config.gcs_bucket_name}")
    print(f"  - Timeout: {config.timeout}s")
    print("=" * 60)


def main():
    """Main execution function."""
    # Initialize configuration
    config = Config()
    
    # Print configuration
    print_configuration(config)
    
    # Initialize dashboard manager
    try:
        manager = LookerDashboardManager(config)
    except RuntimeError as e:
        print(f"Failed to initialize: {e}")
        return 1
    
    # Find inactive dashboards (test mode first)
    print("Running in TEST MODE - checking only first 10 dashboards")
    inactive_dashboards = manager.find_inactive_dashboards(test_mode=True)
    
    if not inactive_dashboards:
        print("No inactive dashboards found.")
        return 0
    
    print(f"\nFound {len(inactive_dashboards)} inactive dashboards:")
    for dashboard in inactive_dashboards:
        print(f"  - {dashboard['title']} (ID: {dashboard['id']})")
        print(f"    Last access: {dashboard['last_access']}")
    
    # Safety check
    print(f"\n{'='*60}")
    print("SAFETY CHECK: Soft delete is currently DISABLED (safe mode)")
    print("To enable soft delete, modify the main() function")
    print("by changing safe_mode=True to safe_mode=False")
    print(f"{'='*60}")
    
    # Process inactive dashboards
    success_count = 0
    for dashboard in inactive_dashboards:
        print(f"\nProcessing dashboard: {dashboard['title']}")
        if manager.soft_delete_dashboard(dashboard['id'], safe_mode=True):
            success_count += 1
    
    print(f"\nCompleted processing {success_count}/{len(inactive_dashboards)} dashboards.")
    return 0


if __name__ == "__main__":
    exit(main())
