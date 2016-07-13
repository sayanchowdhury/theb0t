# -*- coding: utf-8 -*-
"""
    ekan0ra.commands
    ~~~~~~~~~~~~~~~~

    This module holds a dict that maps bot commands to their
    descriptions.

    :copyright: 
    :license:
"""


commands = {
    '.help' : 'List all the commands',
    '!' : 'Queue yourself to ask a question during a session',
    '!!' : 'Remove yourself from question queue during a session',
    '!-' : 'Remove yourself from question queue during a session',
    '.givemelogs' : 'Give you an fpaste link with the latest log',
    '.clearqueue' : 'Clear the question queue',
    '.showqueue' : 'Show the status of the question queue',
    '.next' : 'Ping the next person in the queue to ask their question',
    '.masters' : 'Show the list of all the masters (admins)',
    '.add [nick]' : 'Add [nick] to masters list',
    '.rm [nick]' : 'Remove [nick] from masters list',
    '.startclass [topic]' :
        'Start logging a class; Append optional [topic] to channel topic',
    '.endclass' : 'Stop logging a class',
    '.pingall [message]' : 'Ping all present channel members with [message]',
    '.link [resource]' : 'Show the URL of requested `resource`'
}
