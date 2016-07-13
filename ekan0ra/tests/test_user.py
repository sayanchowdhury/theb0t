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
from config import config_modes


config = config_modes.get('test')


class UserTest(unittest.TestCase):

    def setUp(self):
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

        self.bot = LogBot(config)

    def test_hostmask_parsing(self):
        for hostmask in self.invalidhostmasks:
            self.assertRaises(InvalidUserError, IRCUser, self.bot, hostmask)
        for hostmask in self.validhostmasks:
            self.assertIsInstance(IRCUser(self.bot, hostmask), IRCUser, msg='Could not parse: %s' %hostmask)

    def test_default_admins_works(self):
        self.assertEquals(list(config.ADMINS), self.bot.channel_admins_list)

    def test_not_admin_by_default(self):
        hostmask = random.choice(self.validhostmasks)
        self.user = IRCUser(self.bot, hostmask)
        self.assertIsInstance(self.user, IRCUser)
        # New user should not be an admin by default
        # unless listed as a default admin in config
        if self.user.nick not in config.ADMINS:
            self.assertFalse(self.user.is_admin())
            self.bot.channel_admins_list.append(self.user.nick)
            self.assertTrue(self.user.is_admin())
        else:
            self.assertTrue(self.user.is_admin())

        

    # def tearDown(self):
    #     self.bot.stoplogging()
    #     self.bot.quit()


def main():
    unittest.main()


if __name__ == '__main__':
    unittest.main()