# stdlib imports
import os, sys
import unittest
import random

# library imports
import mock


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# local imports
from ekan0ra.bot import LogBot
from ekan0ra.user import IRCUser, InvalidUserError
from ekan0ra.commands import commands
from config import config_modes


config = config_modes.get('test')


class BotCommandsTest(unittest.TestCase):

    @mock.patch.object(LogBot, 'load_links', auto_spec=True) # Fake links data load
    @mock.patch('ekan0ra.bot.get_logger_instance') # Fake logger creation
    @mock.patch('ekan0ra.bot.irc.IRCClient')
    def setUp(
            self, mock_irc_IRCClient, mock_get_logger_instance,
            mock_links_reload):
        ####TODO: Add more valid hostmask patterns to test
        self.validhostmasks = [
            'sawkateca!~sawkateca@41.203.71.181',
            '29cb47b5!29cb47b5@gateway/web/freenode/ip.41.203.71.181',
            'acetakwas!~acetakwas@41.203.71.181'
        ]
        ####TODO: Add more invalid hostmask patterns to test
        self.invalidhostmasks = [
            '~sawkateca@41.203.71.181',
            '29cb47b5@gateway/web/freenode/ip.41.203.71.181',
            '~acetakwas@41.203.71.181'
        ]

        self.assertFalse(
            mock_links_reload.called,
            'Reload links was called too early')
        self.assertFalse(
            mock_get_logger_instance.called,
            'Get logger instance was called too early')
        self.bot = LogBot(config)
        self.bot.connectionMade()
        self.bot.islogging = True # Fake logging
        
        mock_irc_IRCClient.connectionMade.assert_called_with(self.bot)

    @mock.patch('ekan0ra.bot.irc.IRCClient')
    @mock.patch.object(LogBot, 'describe', auto_spec=True) # Fake links data load
    def test_join_question_queue_command(self, mock_describe,
            mock_irc_IRCClient):
        self.assertListEqual([], self.bot.qs_queue) # Ensure queue is empty
        
        command = '!'
        self.assertIn(command, commands.keys())

        # Add users to queue
        for hostmask in self.validhostmasks:
            self.bot.privmsg(hostmask, self.bot.channel, '!')
            assert(mock_describe.called)
            self.assertIn(IRCUser(self.bot, hostmask).nick, self.bot.qs_queue)
            self.assertEquals(IRCUser(self.bot, hostmask).nick, self.bot.qs_queue[-1])

    @mock.patch.object(LogBot, 'describe', auto_spec=True) # Fake links data load
    @mock.patch('ekan0ra.bot.irc.IRCClient')
    def test_leave_question_queue_command(self, mock_irc_IRCClient,
            mock_describe):
        self.assertListEqual([], self.bot.qs_queue) # Ensure queue is empty
        
        leave_queue_commands = ('!!', '!-')
        join_queue_command = '!'
        self.assertIn(join_queue_command, commands.keys())

        for command in leave_queue_commands:
            self.assertIn(command, commands.keys())

            # First, join queue
            hostmask = self.validhostmasks[0]
            self.bot.privmsg(hostmask, self.bot.channel, join_queue_command)
            assert(mock_describe.called)
            self.assertIn(IRCUser(self.bot, hostmask).nick, self.bot.qs_queue)
            self.assertEquals(IRCUser(self.bot, hostmask).nick, self.bot.qs_queue[-1])

            # Then, leave queue
            # Only one user in queue, it should be empty afterwards
            self.bot.privmsg(hostmask, self.bot.channel, command)
            assert(mock_describe.called)
            self.assertListEqual([], self.bot.qs_queue)

    # @mock.patch('ekan0ra.bot.sys')
    # @mock.patch('ekan0ra.bot.fpaste')
    # @mock.patch('ekan0ra.bot.irc.IRCClient')
    # def test_givemelogs_command(self, mock_irc_IRCClient,
    #         mock_fpaste, mock_sys):
    #     command = '.givemelogs'
    #     self.assertIn(command, commands.keys())
    #     hostmask = self.validhostmasks[0]
        
    #     self.bot.last_log_filename = True # fake value for last_log_filename attribute
    #     self.bot.privmsg(hostmask, self.bot.channel, command)
    #     self.assertEquals(2, len(mock_sys.argv))
    #     self.assertIn('fpaste', mock_sys.argv)
    #     self.assertEquals(self.bot.last_log_filename, mock_sys.argv[1])
    #     self.assertTrue(mock_fpaste.main.called)

    @mock.patch.object(LogBot, 'say', auto_spec=True)
    @mock.patch('ekan0ra.bot.irc.IRCClient')
    def test_help_command(self, mock_irc_IRCClient, mock_say):
        command = '.help'
        self.assertIn(command, commands.keys())
        hostmask = self.validhostmasks[0]

        self.bot.privmsg(hostmask, self.bot.channel, command)
        self.assertTrue(mock_say.called)
        

    # def tearDown(self):
    #     self.bot.stoplogging()
    #     self.bot.quit()


def main():
    unittest.main()


if __name__ == '__main__':
    unittest.main()