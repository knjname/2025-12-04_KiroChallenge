"""
Configuration module for the Events API.

This module provides centralized configuration management for the application.
"""

import os
import boto3
from typing import Optional


class Config:
    """Application configuration."""
    
    def __init__(self, table_name: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            table_name: DynamoDB table name. If None, reads from EVENTS_TABLE_NAME env var.
        """
        self.table_name = table_name or os.environ.get('EVENTS_TABLE_NAME', 'Events')
        self._dynamodb_resource: Optional[boto3.resource] = None
    
    @property
    def dynamodb_resource(self) -> boto3.resource:
        """
        Get DynamoDB resource, creating it if necessary.
        
        Returns:
            boto3 DynamoDB resource
        """
        if self._dynamodb_resource is None:
            self._dynamodb_resource = boto3.resource('dynamodb')
        return self._dynamodb_resource
    
    def get_table(self):
        """
        Get DynamoDB table.
        
        Returns:
            DynamoDB Table resource
        """
        return self.dynamodb_resource.Table(self.table_name)
