# -*- coding: utf-8 -*-
"""
    ekan0ra.logger
    ~~~~~~~~~~~~~~

    This module implements a logger for IRC class sessions and a factory
    function to go with it.

    :copyright: 
    :license:
"""
# standard library imports
import logging
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# local imports
from . import APP_LOGGER


class MessageLogger(object):
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self):
        self.logger = None
        self.filename = None

    def create_new_log(self,
            filename=None,
            format_str='[%(asctime)15s]: %(message)s',
            date_fmt='[%H:%M:%S]',
            when='midnight',
            interval=1,
            backupCount=10):
        assert when.lower() in ('s', 'm', 'h', 'd', 'midnight',
                                'w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6',)
        assert interval > 0
        assert backupCount > 0

        self.logger = logging.getLogger('classLogger')
        self.filename = filename or 'Logs-{}.txt'.format(
            datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

        log_formatter = logging.Formatter(
            fmt=format_str, datefmt=date_fmt)

        file_handler = TimedRotatingFileHandler(
            self.filename,
            when=when,
            interval=interval,
            backupCount=backupCount)
        file_handler.setLevel('INFO')
        file_handler.setFormatter(log_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel('ERROR')
        console_handler.setFormatter(log_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel('INFO')

    def log(self, message):
        """Log `message` to a log file."""
        # timestamp = time.strftime(config.CLASS_LOG_DATE_FORMAT_STR,
        #     time.localtime(time.time()))
        # log_msg =  ''.join(['[', timestamp, '] ', message])
        self.logger.info(message)

    def close(self):
        if self.logger is not None:
            for handler in self.logger.handlers:
                if isinstance(handler, TimedRotatingFileHandler):
                    handler.doRollover()   
                handler.flush()
                handler.close()
            del self.logger.handlers[:]

    def pastebin_log(self, logger=None):
        from fpaste import main
        import sys
        if self.filename is not None:
            sys.argv = ['fpaste', self.filename]
            try:
                short_url, url = main()
                return short_url, url
            except:
                if logger is not None:
                    logger.error('Log uploading to Fedora Paste failed!',
                        exc_info=True)
        return None    


# Get logger instance
def get_logger_instance():
    """Return an instance of `MessageLogger`."""
    return MessageLogger()