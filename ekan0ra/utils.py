# -*- coding: utf-8 -*-
"""
    ekan0ra.utils
    ~~~~~~~~~~~~~

    A bunch of utility functions for the program.

    :copyright: 
    :license:
"""
# local imports
from .commands import commands


# Returns a properly formatted channel name
# by making sure it begins with a '#'
def validate_channel(channel):
    assert type(channel) is str # defensive programming
    channel = '#' + channel.lstrip('#')
    return channel


# returns a list of valid link names
# def get_link_names(links_data):
#     return links_list.keys()


def get_help_info(command=None):
    """Retrieve and format help text for `command`."""
    if command is None:
        basic_cmds = [cmd.split()[0] for cmd in commands.keys()]    
        return 'To see details of a command, type:\n\t`.help [command]`' \
            '\nCommands are:\n\t{}'.format(', '.join(sorted(basic_cmds)))
    else:
        command = str(command).strip()
        key, value = command, commands.get(command, None)
        if value is None:
            for k, v in commands.iteritems():
                if k.find(command) == 0:
                    key, value = k, v
                    break
            else:
                return '%s is not a valid command.' % command

        return 'Usage:\n\t{cmd}\nDescription:\n\t{desc}'.format(
            cmd=key, desc=value)
