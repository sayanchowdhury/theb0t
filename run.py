#!/usr/bin/env python
# standard library imports
import logging
import os
import sys

# third-party imports
from twisted.internet import reactor

# local imports
from config import config_modes
from ekan0ra import setup_app_logger, APP_LOGGER
from ekan0ra.factory import LogBotFactory

# Create an instance* of the configuration mode to use,
# so we can access its __repr__ for logging.
#
# * Note the trailing parentheses: '()'
#
# Valid values for `config_modes()` are:
#   'default', 'dev', 'test', 'deploy'
config = config_modes.get(os.getenv('LOGBOT_CONFIG', 'default'))()


def create_bot(config):
    """Creates an IRC log bot using a factory."""
    log_bot_factory = LogBotFactory(config)
    return log_bot_factory


def run_bot(bot_factory, config):
    """Connects bot to server."""
    server, port = config.IRC_SERVER, config.IRC_SERVER_PORT
    APP_LOGGER.info('Connecting to SERVER(%s) on PORT(%d)', server, port)
    reactor.connectTCP(server, port, bot_factory)
    reactor.run()


if __name__ == '__main__':
    setup_app_logger(config=config)  # initialize application logging
    run_bot(create_bot(config=config), config)
    if APP_LOGGER:
        APP_LOGGER.info('Shutting down gracefully...')
        logging.shutdown()
    sys.exit(0)