#!/bin/python
"""
@copyright: IBM
"""
import os
import sys
import logging
import socket
import threading
from datetime import datetime, timezone
from pythonjsonlogger.json import JsonFormatter
from . import constants as const

# Flag to ensure logging is only configured once
_logging_configured = False


class IBMVIAJsonFormatter(JsonFormatter):
    """
    Custom JSON formatter that matches IBM Verify Access container log format.
    
    Output format:
    {
        "type": "ibmvia-autoconf",
        "host": "<hostname>",
        "timestamp": "<ISO 8601 timestamp>",
        "message": "<log message>",
        "ibm_threadId": "<thread_id>",
        "loglevel": "<numeric_level>"
    }
    """
    
    # Map Python log levels to IBM numeric levels
    LEVEL_MAP = {
        logging.DEBUG: "5",      # Debug
        logging.INFO: "3",       # Info
        logging.WARNING: "2",    # Warning
        logging.ERROR: "1",      # Error
        logging.CRITICAL: "0"    # Critical
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = socket.gethostname()
    
    def add_fields(self, log_data, record, message_dict):
        """
        Override to add custom fields in IBM VIA format.
        """
        super().add_fields(log_data, record, message_dict)
        
        # Add IBM VIA specific fields
        log_data['type'] = 'ibmvia-autoconf'
        log_data['host'] = self.hostname
        
        # Add ISO 8601 timestamp with timezone
        if 'asctime' in log_data:
            # Convert to ISO 8601 format with timezone
            dt = datetime.now(timezone.utc)
            log_data['timestamp'] = dt.isoformat()
            del log_data['asctime']
        
        # Convert levelname to IBM numeric loglevel
        if 'levelname' in log_data:
            level_num = getattr(record, 'levelno', logging.INFO)
            log_data['loglevel'] = self.LEVEL_MAP.get(level_num, "3")
            del log_data['levelname']
        
        # Add thread ID
        log_data['ibm_threadId'] = str(threading.get_ident())
        
        # Remove fields we don't want in the output
        for field in ['levelno', 'name', 'pathname', 'filename', 'module',
                      'funcName', 'lineno', 'created', 'msecs', 'relativeCreated',
                      'thread', 'threadName', 'processName', 'process']:
            log_data.pop(field, None)


def setup_logging():
    """
    Configure logging based on environment variables.
    Returns the configured log level.
    
    This function is idempotent - it will only configure logging once,
    even if called multiple times. This prevents duplicate log messages
    from multiple handlers being added to the root logger.
    """
    global _logging_configured
    
    # If logging is already configured, return early
    if _logging_configured:
        return logging.root.level
    
    log_level = logging.INFO
    if const.LOG_LEVEL in os.environ.keys():
        log_level = str(os.environ.get(const.LOG_LEVEL))
    elif const.LEGACY_LOG_LEVEL in os.environ.keys():
        log_level = str(os.environ.get(const.LEGACY_LOG_LEVEL))

    log_file = None
    if const.LOG_FILE in os.environ.keys():
        log_file = os.environ.get(const.LOG_FILE)

    use_json_format = False
    log_fmt = "%(asctime)s - %(levelname)s - %(message)s"
    if const.LOG_FORMAT in os.environ.keys():
        env_fmt = str(os.environ.get(const.LOG_FORMAT))
        if env_fmt.lower() == "json":
            use_json_format = True
        else:
            log_fmt = env_fmt

    # Clear any existing handlers to prevent duplicates
    logging.root.handlers.clear()
    
    if use_json_format:
        logHandler = logging.StreamHandler(sys.stdout) \
                                                if not log_file else logging.FileHandler(log_file)
        # Use IBM VIA compatible JSON formatter
        formatter = IBMVIAJsonFormatter('%(asctime)s %(levelname)s %(message)s')
        logHandler.setFormatter(formatter)
        logHandler.setLevel(log_level)
        logging.root.setLevel(log_level)
        logging.root.addHandler(logHandler)
    elif log_file:
        logging.basicConfig(level=log_level, filename=log_file, format=log_fmt, force=True)
    else:
        logging.basicConfig(stream=sys.stdout, level=log_level, format=log_fmt, force=True)

    # Mark logging as configured
    _logging_configured = True
    
    return log_level

# Made with Bob
