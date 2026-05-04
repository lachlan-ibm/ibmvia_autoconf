"""
API Failure Tracker - Singleton for tracking failed API requests.

This module provides a singleton class to track failed API requests across
the IBM Verify Identity Access (IVIA) configurator project and print a
summary at the end of module execution.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import os
import json
from . import constants as const


class APIFailureTracker:
    """Singleton for tracking failed API requests."""
    
    _instance: Optional['APIFailureTracker'] = None
    _failures: List[Dict]
    _enabled: bool
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._failures = []
            cls._instance._enabled = os.environ.get(const.API_TRACK_FAILURES, 'true').lower() == 'true'
        return cls._instance
    
    def is_enabled(self) -> bool:
        """Check if tracking is enabled."""
        return self._enabled
    
    def record_failure(
        self,
        module: str,
        operation: str,
        error_message: str,
        api_endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_content: Optional[Any] = None,
        request_data: Optional[Dict] = None
    ):
        """
        Record a failed API request with comprehensive context.
        
        Args:
            module: The module being activated (e.g., 'access_control', 'webseal')
            operation: The specific operation/function being performed
            error_message: The error message from the API response
            api_endpoint: The API endpoint that was called (optional)
            status_code: HTTP status code from the response (optional)
            response_content: Full response content/data from the API (optional)
            request_data: The request payload/parameters sent (optional)
        """
        if not self._enabled:
            return
            
        self._failures.append({
            'timestamp': datetime.utcnow().isoformat(),
            'module': module,
            'operation': operation,
            'error_message': error_message,
            'api_endpoint': api_endpoint,
            'status_code': status_code,
            'response_content': response_content,
            'request_data': request_data
        })
    
    def get_failures(self) -> List[Dict]:
        """Get all recorded failures."""
        return self._failures.copy()
    
    def get_failure_count(self) -> int:
        """Get total number of failures."""
        return len(self._failures)
    
    def clear(self):
        """Clear all recorded failures."""
        self._failures.clear()
    
    def print_summary(self):
        """Print a formatted summary of all failures."""
        if not self._enabled:
            return
        
        # Check if JSON format is requested
        use_json_format = os.environ.get(const.LOG_FORMAT, '').lower() == 'json'
        
        if not self._failures:
            if use_json_format:
                output = {
                    "api_failure_summary": {
                        "total_failures": 0,
                        "message": "No API failures recorded during execution"
                    }
                }
                print(json.dumps(output))
            else:
                print("\n✓ No API failures recorded during execution.")
            return
        
        # Group failures by module
        by_module = {}
        for failure in self._failures:
            module = failure['module']
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(failure)
        
        if use_json_format:
            # Output JSON format
            module_counts = {module: len(failures) for module, failures in by_module.items()}
            output = {
                "api_failure_summary": {
                    "total_failures": len(self._failures),
                    "by_module": module_counts
                },
                "failures": self._failures
            }
            print(json.dumps(output, indent=2))
        else:
            # Output human-readable format
            print(f"\n{'='*80}")
            print(f"API FAILURE SUMMARY - {len(self._failures)} Failed Request(s)")
            print(f"{'='*80}\n")
            
            for module, failures in by_module.items():
                print(f"Module: {module} ({len(failures)} failure(s))")
                print("-" * 80)
                for i, failure in enumerate(failures, 1):
                    print(f"  {i}. Operation: {failure['operation']}")
                    print(f"     Error: {failure['error_message']}")
                    
                    if failure['api_endpoint']:
                        print(f"     API Endpoint: {failure['api_endpoint']}")
                    
                    if failure['status_code']:
                        print(f"     Status Code: {failure['status_code']}")
                    
                    if failure['response_content']:
                        print(f"     Response: {failure['response_content']}")
                    
                    if failure['request_data']:
                        print(f"     Request Data: {failure['request_data']}")
                    
                    print(f"     Timestamp: {failure['timestamp']}")
                    print()
                
                print()
            
            print(f"{'='*80}\n")


def get_tracker() -> APIFailureTracker:
    """Get the global API failure tracker instance."""
    return APIFailureTracker()


def track_failure(module: str, operation: str, rsp, request_data: Optional[Dict] = None):
    """
    Convenience function to track API failures from response objects.
    
    This function extracts common attributes from PyIVIA response objects
    and records the failure automatically. Handles None response objects safely.
    
    Args:
        module: The module name (e.g., 'access_control', 'webseal')
        operation: The operation being performed
        rsp: The PyIVIA response object (can be None)
        request_data: Optional request data/payload
    """
    if rsp is None:
        get_tracker().record_failure(
            module=module,
            operation=operation,
            error_message='No response object available',
            api_endpoint=None,
            status_code=None,
            response_content=None,
            request_data=request_data
        )
    else:
        get_tracker().record_failure(
            module=module,
            operation=operation,
            error_message=str(rsp.data) if hasattr(rsp, 'data') else 'Unknown error',
            api_endpoint=getattr(rsp, 'url', None),
            status_code=getattr(rsp, 'status_code', None),
            response_content=getattr(rsp, 'data', None),
            request_data=request_data
        )

# Made with Bob
