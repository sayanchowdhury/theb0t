# -*- coding: utf-8 -*-
"""
    ekan0ra.user
    ~~~~~~~~~~~~

    This module implements an IRC User wrapper the Twisted-framework-based bot object.

    :copyright: 
    :license:
"""
import re


class IRCUser(object):
    """Wrapper around an IRC user.

    It contains the following basic info about a user:
        nick,
        ident,
        mask

    Args:
        bot: A `LogBot` instance which will interact with this 
            IRCUser.
        user_hostmask: IRC hostmask of that will be parsed to create
            this User.

    Attributes:
        bot: LogBot instance registered with this IRCUser.
        hostmask: Hostmask for parse this IRCUser instance.
        nick: User's IRC nickname.
        ident: Ident part of user's hostmask.
        mask: Mask part of user's hostmask.

    Raises:
        InvalidUserError: Raised if an invalid hostmask is given for
        parsing.
    """

    # 'hostmask' is of the form: username!ident@hostmask
    # Every user has access to the bot object
    def __init__(self, bot, user_hostmask):
        self.bot = bot
        self.hostmask = user_hostmask
        hostmask_pattern = re.compile(r'\w*![~\w]*@\w*')
        if hostmask_pattern.search(user_hostmask):
            self.nick, self.ident, self.mask = re.split('[!@]', user_hostmask) # split into nick, ident, mask
        else:
            raise InvalidUserError

    def __repr__(self):
        return 'User [Nick: %s; Ident: %s; Mask: %s]' % (self.nick, self.ident, self.mask)

    def is_admin(self):
        """Is this user an admin?

        Ask bot who registered on this `IRCUser` if they've made this
        user an admin.
        """
        return self.nick in self.bot.channel_admins_list


class InvalidUserError(Exception):
    pass
