# -*- coding: utf-8 -*-
"""
    ekan0ra.factory
    ~~~~~~~~~~~~~~~

    This module implements a factory for creating an IRC bot.

    :copyright: 
    :license:
"""
# third-party imports
from twisted.internet import reactor, protocol

# local imports
from . import APP_LOGGER
from .bot import LogBot


class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the
    server.
    """
    def __init__(self, config):
        self.config = config
        self.channel = self.config.CHANNEL
        self.nickname = self.config.BOTNICK
        self.channel_admins_list = self.config.ADMINS

    def buildProtocol(self, addr):
        self.bot = LogBot(self.config)
        self.bot.factory = self
        APP_LOGGER.info('Bot protocol finished initializing.')
        return self.bot

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        APP_LOGGER.warning('Client got disconnected! Trying reconnect...')
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        APP_LOGGER.warning('Client connection failed! Reason: %r', reason)
        reactor.stop()