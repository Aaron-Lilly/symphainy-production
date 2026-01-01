#!/usr/bin/env python3
"""
Error Handler Micro-Module

Handles and formats API errors with user-friendly messages.

WHAT (Micro-Module): I handle and format API errors
HOW (Implementation): I provide user-friendly error messages and proper error formatting
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from config.environment_loader import EnvironmentLoader
from experience.interfaces.frontend_integration_interface import APIEndpoint, ResponseStatus
from utilities import UserContext


class ErrorHandlerModule:
    """
    Error Handler Micro-Module
    
    Handles and formats API errors with user-friendly messages and proper error formatting.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, environment: Optional[EnvironmentLoader] = None):
        """Initialize Error Handler Module."""
        self.logger = logger or logging.getLogger(__name__)
        self.environment = environment
        self.is_initialized = False
        
        # User-friendly error messages
        self.user_friendly_messages = {
            '400': 'Invalid request. Please check your input and try again.',
            '401': 'Authentication required. Please log in again.',
            '403': 'Access denied. You may not have permission for this operation.',
            '404': 'Resource not found. The requested resource may have been moved or deleted.',
            '422': 'Invalid data format. Please ensure your data is in the correct format.',
            '500': 'Server error. Please try again later or contact support.',
            '502': 'Service temporarily unavailable. Please try again later.',
            '503': 'Service temporarily unavailable. Please try again later.',
            '504': 'Request timeout. Please try again with a smaller request.',
        }
        
        self.logger.info("⚠️ Error Handler Module initialized")
    
    async def initialize(self):
        """Initialize the Error Handler Module."""
        self.logger.info("🚀 Initializing Error Handler Module...")
        self.is_initialized = True
        self.logger.info("✅ Error Handler Module initialized successfully")
    
    async def handle_error(
        self, 
        error: Exception, 
        endpoint: APIEndpoint, 
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        Handle and format API errors.
        
        Args:
            error: The error that occurred
            endpoint: The API endpoint where the error occurred
            user_context: Context of the user
            
        Returns:
            A dictionary containing formatted error information
        """
        self.logger.error(f"Handling error for {endpoint.value}: {str(error)}")
        
        try:
            # Determine error type and status
            error_type = type(error).__name__
            status_code = getattr(error, 'status_code', 500)
            
            # Get user-friendly message
            friendly_message = self.user_friendly_messages.get(
                str(status_code), 
                f"An error occurred: {str(error)}"
            )
            
            # Create error response
            error_response = {
                "success": False,
                "error": friendly_message,
                "error_type": error_type,
                "status_code": status_code,
                "status": ResponseStatus.ERROR.value,
                "endpoint": endpoint.value,
                "user_id": user_context.user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add technical details for debugging (in development)
            if self.environment and self.environment.get_environment() == "development":
                error_response["technical_details"] = {
                    "original_error": str(error),
                    "error_class": error_type,
                    "traceback": getattr(error, '__traceback__', None)
                }
            
            return error_response
            
        except Exception as e:
            self.logger.error(f"Failed to handle error: {str(e)}")
            return {
                "success": False,
                "error": "An unexpected error occurred while processing your request.",
                "status_code": 500,
                "status": ResponseStatus.ERROR.value,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def handle_api_error(
        self, 
        error: Exception, 
        endpoint: APIEndpoint, 
        user_context: UserContext,
        response_text: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Handle and format API errors with user-friendly messages.
        
        Args:
            error: The error that occurred
            endpoint: The API endpoint where the error occurred
            user_context: Context of the user
            response_text: Raw response text from the server
            status_code: HTTP status code
            
        Returns:
            A dictionary containing formatted error information
        """
        self.logger.error(f"Handling API error for {endpoint.value}: {str(error)}")
        
        try:
            # Determine status code
            actual_status_code = status_code or getattr(error, 'status_code', 500)
            
            # Parse error message from response text if available
            error_message = str(error)
            if response_text:
                try:
                    import json
                    error_data = json.loads(response_text)
                    error_message = error_data.get('detail', error_data.get('message', error_message))
                except:
                    error_message = response_text
            
            # Get user-friendly message
            friendly_message = self.user_friendly_messages.get(
                str(actual_status_code), 
                error_message
            )
            
            # Create error response
            error_response = {
                "success": False,
                "error": friendly_message,
                "status_code": actual_status_code,
                "status": ResponseStatus.ERROR.value,
                "endpoint": endpoint.value,
                "user_id": user_context.user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add response details if available
            if response_text:
                error_response["response_details"] = response_text
            
            # Add technical details for debugging (in development)
            if self.environment and self.environment.get_environment() == "development":
                error_response["technical_details"] = {
                    "original_error": str(error),
                    "error_class": type(error).__name__,
                    "response_text": response_text
                }
            
            return error_response
            
        except Exception as e:
            self.logger.error(f"Failed to handle API error: {str(e)}")
            return {
                "success": False,
                "error": "An unexpected error occurred while processing your request.",
                "status_code": 500,
                "status": ResponseStatus.ERROR.value,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_error_response(
        self, 
        message: str, 
        status_code: int = 500, 
        endpoint: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            status_code: HTTP status code
            endpoint: API endpoint where error occurred
            user_id: User ID
            
        Returns:
            A dictionary containing the error response
        """
        return {
            "success": False,
            "error": message,
            "status_code": status_code,
            "status": ResponseStatus.ERROR.value,
            "endpoint": endpoint,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def log_error(
        self, 
        error: Exception, 
        endpoint: APIEndpoint, 
        user_context: UserContext,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log error details for monitoring and debugging.
        
        Args:
            error: The error that occurred
            endpoint: The API endpoint where the error occurred
            user_context: Context of the user
            additional_context: Additional context information
        """
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "endpoint": endpoint.value,
            "user_id": user_context.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if additional_context:
            error_details["additional_context"] = additional_context
        
        self.logger.error(f"API Error: {error_details}")
    
    async def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        # In a real implementation, this would query error logs
        return {
            "total_errors": 0,
            "errors_by_status_code": {},
            "errors_by_endpoint": {},
            "recent_errors": [],
            "timestamp": datetime.utcnow().isoformat()
        }
