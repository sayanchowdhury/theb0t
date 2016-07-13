# -*- coding: utf-8 -*-
"""
    ekan0ra
    ~~~~~~~

    An logging bot for IRC-based class sessions.

    :copyright:
    :license:
"""
import logging
import os
import sys

APP_LOGGER = logging.getLogger(__name__)


def setup_app_logger(config):
    from logging.handlers import TimedRotatingFileHandler
    global APP_LOGGER

    # log file rotation scheduling
    when, interval, backupCount = config.APP_LOG_ROTATION_TIME, \
        config.APP_LOG_ROTATION_INTERVAL, config.APP_LOG_BACKUP_COUNT
    assert when.lower() in ('s', 'm', 'h', 'd', 'midnight',
                            'w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6',)
    assert interval > 0
    assert backupCount > 0

    if not os.path.exists(config.APP_LOG_DIR):
        os.mkdir(config.APP_LOG_DIR)
    log_file_path = os.path.join(config.APP_LOG_DIR, config.APP_LOG_FILENAME)

    formatter = logging.Formatter(config.APP_LOG_FORMAT_STR)

    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when=when,
        interval=interval,
        backupCount=backupCount)
    file_handler.setLevel('INFO')
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel('DEBUG')
    console_handler.setFormatter(formatter)
    
    APP_LOGGER.addHandler(file_handler)
    APP_LOGGER.addHandler(console_handler)
    APP_LOGGER.setLevel('DEBUG')