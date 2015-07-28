# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.internet import defer

# system imports
import time, sys, os
import datetime
import config as conf

import fpaste

now = datetime.datetime.now()

commands = [
    ('!', 'Queue yourself to ask a question during a session'),
    ('givemelogs', 'Give you a fpaste link with the latest log'),
    ('clearqueue', 'Clear the ask question queue'),
    ('next', 'ping the person in the queue to ask question'),
    ('masters', 'returns the list of all the masters'),
    ('add:[nick]', 'adds the nick to masters list'),
    ('rm:[nick]', 'removes the nick to masters list'),
    ('startclass', 'start logging the class'),
    ('endclass', 'ends logging the class'),
    ('pingall:[message]', 'pings the message to all'),
    ('help', 'list all the commands'),
]

help_template = """
{command} - {help_text}
"""

class MessageLogger(object):
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

    nickname = conf.botnick

    def  __init__(self, channel):
        self.chn = '#'+channel
        self.channel_admin = conf.channel_admin
        self.qs_queue = []
        self.logger = None

    def clearqueue(self):
        self.qs_queue = []

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
        if not self.logger:
            return
        self.logger.log("[## Class Ended at %s ##]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()
        #self.upload_logs(channel)
        self.islogging = False

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.islogging = False

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
        if msg == '!'  and self.islogging:
            self.qs_queue.append(user)
        if msg == '!' and not self.islogging:
            self.msg(self.chn, '%s no session is going on, feel free to ask a question. You do not have to type !' % user)
            return
        if msg == 'givemelogs':
            import sys
            sys.argv = ['fpaste', self.filename]
            try:
                short_url, url = fpaste.main()
                self.msg(user, url)
            except:
                self.msg(user, '500: I have a crash on you')
        if msg == 'clearqueue' and user_cond:
            self.clearqueue()
            self.msg(self.chn, "Queue is cleared.")
        if msg == 'next' and user_cond:
            if len(self.qs_queue) > 0:
                name = self.qs_queue.pop(0)
                msg = "%s please ask your question." % name
                if len(self.qs_queue) > 0:
                    msg = "%s. %s you are next. Get ready with your question." % (msg, self.qs_queue[0])
                self.msg(self.chn, msg)
            else:
                self.msg(self.chn, "No one is in queue.")
        if msg == 'masters' and user_cond:
            self.msg(self.chn, "My current masters are: %s" % ",".join(self.channel_admin))
        if msg.startswith('add:') and user_cond:
            try:
                name = msg.split()[1]
                print name
                self.channel_admin.append(name)
                self.msg(self.chn,'%s is a master now.' % name)
            except Exception, err:
                print err
        if msg.startswith('rm:') and user_cond:
            try:
                name = msg.split()[1]
                self.channel_admin = filter(lambda x: x != name, self.channel_admin)
            except Exception, err:
                print err

        if msg == 'help':
            for command, help_txt in commands:
                self.msg(user, help_template.format(command=command,
                                                    help_text=help_txt))

        if channel == self.nickname:

            if msg.lower().endswith('startclass') and user_cond:
                self.startlogging(user, msg)
                self.msg(user, 'Session logging started successfully')
                self.msg(self.chn, '----------SESSION STARTS----------')

            if msg.lower().endswith('endclass') and user_cond:
                self.msg(self.chn, '----------SESSION ENDS----------')
                self.stoplogging(channel)
                self.msg(user, 'Session logging terminated successfully')

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
