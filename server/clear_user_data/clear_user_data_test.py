import unittest
from clear_user_data.main import clear_pinecone


class TestClearUserData(unittest.TestCase):
    def setUp(self):
        self.user_id = "test"

    def test_clear_pinecone(self):
        clear_pinecone(self.user_id)
