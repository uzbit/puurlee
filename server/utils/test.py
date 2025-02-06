import unittest
from pathlib import Path
from utils.Utilities import API_KEY


class TestUtilities(unittest.TestCase):
    def setUp(self):
        pass

    def test_optionsini(self):
        self.assertEqual(len(API_KEY), 44)
