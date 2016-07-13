# standard library imports
import os, sys
import unittest

# library imports
import mock


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# local imports
from ekan0ra.utils import validate_channel#, get_link_names


class UtilsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
        
    def test_verify_channel(self):
        self.assertEqual(validate_channel("chan"), "#chan")
        self.assertEqual(validate_channel("#someunknownchannel"), "#someunknownchannel")
        self.assertEqual(validate_channel("####anotherchan"), "#anotherchan")


def main():
    unittest.main()


if __name__ == '__main__':
    unittest.main()