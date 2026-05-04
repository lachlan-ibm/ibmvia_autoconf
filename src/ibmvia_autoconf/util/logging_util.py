#!/bin/python
"""
@copyright: IBM
"""
import os
import sys
import logging
from pythonjsonlogger.json import JsonFormatter
from . import constants as const


def setup_logging():
    """
    Configure logging based on environment variables.
    Returns the configured log level.
    """
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

    if use_json_format:
        logHandler = logging.StreamHandler(sys.stdout) \
                                                if not log_file else logging.FileHandler(log_file)
        formatter = JsonFormatter('%(asctime)s %(levelname)s %(message)s')
        logHandler.setFormatter(formatter)
        logHandler.setLevel(log_level)
        logging.root.setLevel(log_level)
        logging.root.addHandler(logHandler)
    elif log_file:
        logging.basicConfig(level=log_level, filename=log_file, format=log_fmt)
    else:
        logging.basicConfig(stream=sys.stdout, level=log_level, format=log_fmt)

    return log_level

# Made with Bob
