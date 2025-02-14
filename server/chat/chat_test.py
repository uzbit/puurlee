import unittest
from chat.main import answer_health_question


class TestChat(unittest.TestCase):
    def setUp(self):
        self.user_id = "test"
        self.question = "Are there any abnormal results in my tests?"

    def test_answer_health_question(self):
        answer_health_question(self.user_id, self.question)
