import unittest
from chat.main import answer_health_question


class TestChat(unittest.TestCase):
    def setUp(self):
        self.user_id = "test"
        self.question = "Why is a kabuodlle a blake knot?"  # "Is there anything abnormal with my health?"

    def test_answer_health_question(self):
        answer_health_question(self.user_id, self.question)
