# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys
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
    
    nickname = "dpr0"

    global angry
    angry = [ 
        'I am getting angry now.',
        'I am feeling disturbed.',
        'Let me log.',
        'Logging is the most important task.',
        'My owner will kill me.',
        'Do your job.',
        'Did you see the movie "Himmatwala"?',
        'I see what you did there',
        "I feel you are free but i'm not",
        "Go, and do your job.",
        "Ping subho, if you are free",
        "Almost all absurdity of conduct arises from the imitation of those who we cannot resemble.",
        "Don't bother just to be better than your contemporaries or predecessors.  Try to be better than yourself.",
        "When you look long into an abyss, the abyss looks into you.",
        "It is only in love and murder that we still remain sincere.",
        "Sooner strangle an infant in its cradle than nurse unacted desires.",
        "Worse than telling a lie is spending your whole life staying true to a lie.",
        "I'm drinking beer. Don't disturb",
        "Anybody can become angry - that is easy, but to be angry with the right person and to the right degree and at the right time and for the right purpose, and in the right way - that is not within everybody's power and is not easy.",
        "For every minute you remain angry, you give up sixty seconds of peace of mind.",
        "Please I beg you",
        "I am fuming",
        "I am cheesed off"]

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.islogging = False
        self.arr = angry

    def startlogging(self, user, msg):
        self.logger.close()
        self.logger = MessageLogger(open("Logs-%s"%now.strftime("%Y-%m-%d-%H-%M"), "a"))

        self.logger.log("[## Class Started at %s ##]" %
                    time.asctime(time.localtime(time.time())))
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        self.islogging = True

    def stoplogging(self):
        self.logger.log("[## Class Ended at %s ##]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()
        self.islogging = False

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()


    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        if self.islogging:
            user = user.split('!', 1)[0]
            self.logger.log("<%s> %s" % (user, msg))

        # Check to see if they're sending me a private message
        if channel == self.nickname:

            # Otherwise check to see if it is a message directed at me
            if msg.startswith(self.nickname):
                user = user.split('!', 1)[0]
                if user not in self.arr:
                    msg = "%s: I am a LogBot and i am busy logging. Please don't disturb me." % user
                    self.arr.append(user)
                else:
                    msg = "%s: %s" %(user, random.choice(self.arr))
                self.msg(channel, msg)
    
            if msg.lower().endswith('startclass'):
                self.startlogging(user, msg)
    
            if msg.lower().endswith('endclass'):
                self.stoplogging()

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
