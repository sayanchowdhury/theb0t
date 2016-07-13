"""Configuration for the bot."""
# standard library imports
import os

# Template string for building string 
# representations for config classes
running_mode = 'App running in {mode} mode. With configs:\n{configs}'

# Directory to store application data like logs, links...
DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


# Base configuration class that will be extended
class Config(object): 

    # Main application log config

    # directory to store application logs
    APP_LOG_DIR = os.path.join(DATA_DIR, 'app_logs')
    APP_LOG_FILENAME = 'application_log.log'
    APP_LOG_FORMAT_STR = \
        '\n%(asctime)s - %(name)s - %(levelname)6s: %(message)s'
    
    # App log file rotation scheduling
    
    # Valid values for rotation time:
    #     'S','M','H','D','W0'-'W6','midnight'
    APP_LOG_ROTATION_TIME = 'midnight'
    APP_LOG_ROTATION_INTERVAL = 1  # Don't set to less than 1
    APP_LOG_BACKUP_COUNT = 10  # Don't set to less than 1

    # Class session log config
    
    # directory to store class session logs
    CLASS_LOG_DIR = os.path.join(DATA_DIR, 'class_logs')
    CLASS_LOG_FILENAME_FORMAT_STR = 'Logs-{}.txt'
    CLASS_LOG_FORMAT_STR = '%(asctime)s %(message)s'
    CLASS_LOG_DATE_FORMAT_STR = '[%H:%M:%S]'
    CLASS_LOG_NICK_PADDING = 16
    
    # Class log file rotation scheduling

    # Valid values for rotation time:
    #     'S','M','H','D','W0'-'W6','midnight'
    CLASS_LOG_ROTATION_TIME = 'midnight'
    CLASS_LOG_ROTATION_INTERVAL = 1  # Don't set to less than 1
    CLASS_LOG_BACKUP_COUNT = 10  # Don't set to less than 1

    # File that contains URLs
    LINKS_FILE = os.path.join(DATA_DIR, 'links.json')

    # Other config data

    SESSION_START_MSG = '----------SESSION STARTS----------'
    SESSION_END_MSG = '----------SESSION ENDS----------'
    BASE_TOPIC = "Welcome to Linux User's Group of Durgapur | Mailing list at http://lists.dgplug.org/listinfo.cgi/users-dgplug.org | Old classes https://www.dgplug.org/irclogs/ | https://docs.python.org/3/tutorial/ | https://dgplug.org/summertraining16/"
    IRC_SERVER = 'irc.freenode.net'
    IRC_SERVER_PORT = 6667

    # Enabled/disabled commands or features

    SHOW_QUEUE_STATUS_ENABLED = True
    LEAVE_QUEUE_ENABLED = True
    GIVEMELOGS_ENABLED = True
    LINKS_ENABLED = True
    PINGALL_ENABLED = True
    CHANGE_TOPIC_ENABLED = True


# Configuration used during
# the development of our bot
class DevConfig(Config):

    ######################
    # COMPULSORY CONFIGS #
    ######################
    # You must set bot's attributes to get things running.
    #
    # Uncomment the following bot attributes and set
    # desired values if you want to use this config class
    
    # Bot attributes

    BOTNICK = 'sawkateca'  # The IRC nick of the bot
    # IRC channel to log; use appropriate channel
    # prefix like '#';
    # #test-my-bot is not a registered channel,
    # but you can join it (effectively creating it,
    # unless someone else has joined it) to test the bot
    CHANNEL = '#test-my-bot'
    # List of IRC nicks of bot's admins/masters
    ADMINS = ('acetakwas', )


    ####################
    # OPTIONAL CONFIGS #
    ####################
    # You may optionally override any of these configs:
    
    # Main application log config

    # directory to store application logs
    #APP_LOG_DIR = os.path.join(DATA_DIR, 'app_logs')
    #APP_LOG_FILENAME = 'application_log.log'
    #APP_LOG_FORMAT_STR = \
    #     '\n%(asctime)s - %(name)s - %(levelname)6s: %(message)s'
    
    # App log file rotation scheduling
    
    # Valid values for rotation time:
    #     'S','M','H','D','W0'-'W6','midnight'
    APP_LOG_ROTATION_TIME = 'M'
    APP_LOG_ROTATION_INTERVAL = 60  # Don't set to less than 1
    APP_LOG_BACKUP_COUNT = 5  # Don't set to less than 1

    # Class session log config

    # directory to store class session logs
    #CLASS_LOG_DIR = os.path.join(DATA_DIR, 'class_logs')
    #CLASS_LOG_FILENAME_FORMAT_STR = 'Logs-{}.txt'
    #CLASS_LOG_FORMAT_STR = '%(asctime)s %(message)s'
    #CLASS_LOG_DATE_FORMAT_STR = '[%H:%M:%S]'
    #CLASS_LOG_NICK_PADDING = 16
    
    # Class log file rotation scheduling
    
    # Valid values for rotation time:
    #     'S','M','H','D','W0'-'W6','midnight'
    CLASS_LOG_ROTATION_TIME = 'M'
    CLASS_LOG_ROTATION_INTERVAL = 60  # Don't set to less than 1
    CLASS_LOG_BACKUP_COUNT = 5  # Don't set to less than 1

    # File that contains URLs
    #LINKS_FILE = os.path.join(DATA_DIR, 'links.json')

    # Other config data

    #SESSION_START_MSG = '----------SESSION STARTS----------'
    #SESSION_END_MSG = '----------SESSION ENDS----------'
    #BASE_TOPIC = "Welcome to Linux User's Group of Durgapur | Mailing list at http://lists.dgplug.org/listinfo.cgi/users-dgplug.org | Old classes https://www.dgplug.org/irclogs/ | https://docs.python.org/3/tutorial/ | https://dgplug.org/summertraining16/"
    #IRC_SERVER = 'irc.freenode.net'
    #IRC_SERVER_PORT = 6667

    # Enabled/disabled commands or features

    SHOW_QUEUE_STATUS_ENABLED = True
    #LEAVE_QUEUE_ENABLED = True
    #GIVEMELOGS_ENABLED = True
    #LINKS_ENABLED = True
    #PINGALL_ENABLED = True
    #CHANGE_TOPIC_ENABLED = True

    def __repr__(self):
        data = self.__class__.__dict__.copy()
        data.pop('__doc__', None)
        data.pop('__repr__', None)
        data.pop('__module__', None)
        return running_mode.format(mode='development', configs=data)


# Configuration for testing the functionalities
# of our bot
class TestConfig(Config):

    ######################
    # COMPULSORY CONFIGS #
    ######################
    # You must set bot's attributes to get things running.
    #
    # Uncomment the following bot attributes and set
    # desired values if you want to use this config class
    
    # Bot attributes

    BOTNICK = 'sawkat'  # The IRC nick of the bot
    # IRC channel to log; use appropriate channel
    # prefix like '#'; #botters-test is a standard
    # IRC bot testing channel
    CHANNEL = '#botters-test'
    # List of IRC nicks of bot's admins/masters 
    ADMINS = ('acetakwas', )


    ####################
    # OPTIONAL CONFIGS #
    ####################
    # You may optionally override any of these configs:

    # Main application log config

    # directory to store application logs
    #APP_LOG_DIR = os.path.join(DATA_DIR, 'app_logs')
    #APP_LOG_FILENAME = 'application_log.log'
    #APP_LOG_FORMAT_STR = \
    #     '\n%(asctime)s - %(name)s - %(levelname)6s: %(message)s'
    
    # App log file rotation scheduling
    
    # Valid values for rotation time:
    #     'S','M','H','D','W0'-'W6','midnight'
    #APP_LOG_ROTATION_TIME = 'midnight'
    #APP_LOG_ROTATION_INTERVAL = 1  # Don't set to less than 1
    #APP_LOG_BACKUP_COUNT = 10  # Don't set to less than 1

    # Class session log config

    # directory to store class session logs
    #CLASS_LOG_DIR = os.path.join(DATA_DIR, 'class_logs')
    #CLASS_LOG_FILENAME_FORMAT_STR = 'Logs-{}.txt'
    #CLASS_LOG_FORMAT_STR = '%(asctime)s %(message)s'
    #CLASS_LOG_DATE_FORMAT_STR = '[%H:%M:%S]'
    #CLASS_LOG_NICK_PADDING = 16
    
    # Class log file rotation scheduling
    
    # Valid values for rotation time:
    #     'S','M','H','D','W0'-'W6','midnight'
    #CLASS_LOG_ROTATION_TIME = 'midnight'
    #CLASS_LOG_ROTATION_INTERVAL = 1  # Don't set to less than 1
    #CLASS_LOG_BACKUP_COUNT = 10  # Don't set to less than 1

    # File that contains URLs
    #LINKS_FILE = os.path.join(DATA_DIR, 'links.json')

    # Other config data

    #SESSION_START_MSG = '----------SESSION STARTS----------'
    #SESSION_END_MSG = '----------SESSION ENDS----------'
    #BASE_TOPIC = "Welcome to Linux User's Group of Durgapur | Mailing list at http://lists.dgplug.org/listinfo.cgi/users-dgplug.org | Old classes https://www.dgplug.org/irclogs/ | https://docs.python.org/3/tutorial/ | https://dgplug.org/summertraining16/"
    #IRC_SERVER = 'irc.freenode.net'
    #IRC_SERVER_PORT = 6667

    # Enabled/disabled commands or features

    #SHOW_QUEUE_STATUS_ENABLED = False
    #LEAVE_QUEUE_ENABLED = True
    #GIVEMELOGS_ENABLED = True
    #LINKS_ENABLED = True
    #PINGALL_ENABLED = True
    #CHANGE_TOPIC_ENABLED = True

    def __repr__(self):
        data = self.__class__.__dict__.copy()
        data.pop('__doc__', None)
        data.pop('__repr__', None)
        data.pop('__module__', None)
        return running_mode.format(mode='testing', configs=data)
    

# Main configuration for when our bot is deployed on a server
class DeployConfig(Config):

    ######################
    # COMPULSORY CONFIGS #
    ######################
    # You must set bot's attributes to get things running.
    #
    # Uncomment the following bot attributes and set
    # desired values if you want to use this config class
    
    # Bot attributes

    BOTNICK = 'batul'   # The IRC nick of the bot
    # IRC channel to log; use appropriate channel
    # prefix like '#'
    CHANNEL = '#dgplug'  
    # List of IRC nicks of bot's admins/masters
    ADMINS = ('kushal',
            'sayan',
            'mbuf',
            'rtnpro',
            'chandankumar',
            'praveenkumar',)  

    
    ####################
    # OPTIONAL CONFIGS #
    ####################
    # You may optionally override any of these configs:

    # Main application log config

    # directory to store application logs
    APP_LOG_DIR = os.path.join(DATA_DIR, 'app_logs')
    APP_LOG_FILENAME = 'application_log.log'
    APP_LOG_FORMAT_STR = \
         '\n%(asctime)s - %(name)s - %(levelname)6s: %(message)s'
    
    # App log file rotation scheduling
    
    # Valid values for rotation time:
    #     'S','M','H','D','W0'-'W6','midnight'
    APP_LOG_ROTATION_TIME = 'H'
    APP_LOG_ROTATION_INTERVAL = 72  # Don't set to less than 1
    APP_LOG_BACKUP_COUNT = 10  # Don't set to less than 1

    # Class session log config

    # directory to store class session logs
    CLASS_LOG_DIR = os.path.join(DATA_DIR, 'class_logs')
    CLASS_LOG_FILENAME_FORMAT_STR = 'Logs-{}.txt'
    CLASS_LOG_FORMAT_STR = '%(asctime)s %(message)s'
    CLASS_LOG_DATE_FORMAT_STR = '[%H:%M:%S]'
    CLASS_LOG_NICK_PADDING = 16
    
    # Class log file rotation scheduling
    
    # Valid values for rotation time:
    #     'S','M','H','D','W0'-'W6','midnight'
    CLASS_LOG_ROTATION_TIME = 'midnight'
    CLASS_LOG_ROTATION_INTERVAL = 1  # Don't set to less than 1
    CLASS_LOG_BACKUP_COUNT = 21  # Don't set to less than 1

    # File that contains URLs
    LINKS_FILE = os.path.join(DATA_DIR, 'links.json')

    # Other config data

    SESSION_START_MSG = '----------SESSION STARTS----------'
    SESSION_END_MSG = '----------SESSION ENDS----------'
    BASE_TOPIC = "Welcome to Linux User's Group of Durgapur | Mailing list at http://lists.dgplug.org/listinfo.cgi/users-dgplug.org | Old classes https://www.dgplug.org/irclogs/ | https://docs.python.org/3/tutorial/ | https://dgplug.org/summertraining16/"
    IRC_SERVER = 'irc.freenode.net'
    IRC_SERVER_PORT = 6667

    # Enabled/disabled commands or features

    SHOW_QUEUE_STATUS_ENABLED = False
    LEAVE_QUEUE_ENABLED = True
    GIVEMELOGS_ENABLED = True
    LINKS_ENABLED = True
    PINGALL_ENABLED = True
    CHANGE_TOPIC_ENABLED = True

    def __repr__(self):
        data = self.__class__.__dict__.copy()
        data.pop('__doc__', None)
        data.pop('__repr__', None)
        data.pop('__module__', None)
        return running_mode.format(mode='deploy', configs=data)


config_modes = {
    'default' : DevConfig,
    'dev' : DevConfig,
    'deploy' : DeployConfig,
    'test' : TestConfig
}
