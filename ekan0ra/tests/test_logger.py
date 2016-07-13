# stdlib imports
import os, sys
import unittest
import logging
import time

# library imports
import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# local imports
from ekan0ra.logger import MessageLogger
from ekan0ra.logger import get_logger_instance


class LoggerTest(unittest.TestCase):

    def setUp(self):
        self.logger = get_logger_instance()
        self.logger.logger = mock.MagicMock()
        #self.logger.create_new_log()

    def test_get_logger_instance(self):
        self.assertIsInstance(get_logger_instance(), MessageLogger)

    @mock.patch('ekan0ra.logger.logging')
    def test_create_new_log(self, mock_logging):
        fake_filename = 'fake_filename.log'
        self.logger.create_new_log()
        self.assertTrue(mock_logging.getLogger.called)
        self.assertTrue(mock_logging.FileHandler.called_with(fake_filename))
        self.assertTrue(mock_logging.StreamHandler.called_with(sys.stdout))
        self.assertTrue(mock_logging.Formatter.called)
        self.assertTrue(self.logger.logger.addHandler.called)
        self.assertTrue(self.logger.logger.setLevel.called_with('INFO'))
        
    def test_log(self):
        fake_log_message = 'Random log message'
        self.logger.log(fake_log_message)
        self.assertTrue(self.logger.logger.info.called)

    #def close(self):
        
    def tearDown(self):
        logging.shutdown()


def main():
    unittest.main()


# if __name__ == '__main__':
#     unittest.main()