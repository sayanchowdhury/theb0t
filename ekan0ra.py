# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

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

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.islogging = False

    def startlogging(self, user, msg):
        self.logger.close()
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

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        if self.islogging:
            user = user.split('!', 1)[0]
            self.logger.log("<%s> %s" % (user, msg))

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            user_cond = user == 'kushal' or user == 'sayan'
            if msg.lower().endswith('startclass') and user_cond:
                self.startlogging(user, msg)
    
            if msg.lower().endswith('endclass') and user_cond:
                self.stoplogging(channel)

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



class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = LogBot()
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
    f = LogBotFactory(sys.argv[1], sys.argv[2])

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()
