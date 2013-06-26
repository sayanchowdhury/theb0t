# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.internet import defer

# system imports
import time, sys, os
import datetime
import random

now = datetime.datetime.now()

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""
    
    nickname = "ekan0ra"

    def  __init__(self, channel):
        self.chn = '#'+channel
        self.channel_admin = ['kushal', 'sayan']

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.islogging = False
        self._namescallback = {}

    def startlogging(self, user, msg):
        self.filename = "Logs-%s"%now.strftime("%Y-%m-%d-%H-%M")
        self.logger = MessageLogger(open(self.filename, "a"))

        self.logger.log("[## Class Started at %s ##]" %
                    time.asctime(time.localtime(time.time())))
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        self.islogging = True

    def stoplogging(self, channel):
        self.logger.log("[## Class Ended at %s ##]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()
        self.upload_logs(channel)
        self.islogging = False

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()

    def upload_logs(self, channel):
        cmd = 'scp ./%s sayanchowdhury@dgplug.org:/home/sayanchowdhury/sayanchowdhury.dgplug.org/irclogs/' %self.filename
        os.system(cmd)
        #msg = 'The logs are updated to: http://sayanchowdhury.dgplug.org/irclogs/%s'%self.filename
        #self.say(channel, msg)
    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def pingall(self, nicklist):
        """Called to ping all with a message"""
        msg = ', '.join([nick for nick in nicklist if nick != self.nickname and nick not in self.channel_admin])
        self.msg(self.chn, msg)
        self.msg(self.chn, self.pingmsg.lstrip())

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        if self.islogging:
            user = user.split('!', 1)[0]
            self.logger.log("<%s> %s" % (user, msg))

        # Check to see if they're sending me a private message
        user_cond = user in self.channel_admin
        if channel == self.nickname:
        
            if msg.lower().endswith('startclass') and user_cond:
                self.startlogging(user, msg)
    
            if msg.lower().endswith('endclass') and user_cond:
                self.stoplogging(channel)

        if msg.lower().startswith('pingall:') and user_cond:
            self.pingmsg = msg.lower().lstrip('pingall:')
            self.names(channel).addCallback(self.pingall)

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        if self.islogging:
            self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        if self.islogging:
            self.logger.log("%s is now known as %s" % (old_nick, new_nick))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'

    def names(self, channel):
        channel = channel.lower()
        d = defer.Deferred()
        if channel not in self._namescallback:
            self._namescallback[channel] = ([], [])

        self._namescallback[channel][0].append(d)
        self.sendLine("NAMES %s" % channel)
        return d

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = params[2].lower()
        nicklist = params[3].split(' ')

        if channel not in self._namescallback:
            return

        n = self._namescallback[channel][1]
        n += nicklist

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = params[1].lower()
        if channel not in self._namescallback:
            return

        callbacks, namelist = self._namescallback[channel]

        for cb in callbacks:
            cb.callback(namelist)

        del self._namescallback[channel]

class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel):
        self.channel = channel

    def buildProtocol(self, addr):
        p = LogBot(self.channel)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)
    
    # create factory protocol and application
    f = LogBotFactory(sys.argv[1])

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()
