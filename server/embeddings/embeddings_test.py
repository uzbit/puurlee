import unittest
from embeddings.main import create_embeddings


class TestEmbeddings(unittest.TestCase):
    def setUp(self):
        self.test_doc_id = "M4t8kcwdWY1Chu8cKtjZ"

    def test_create_embeddings(self):
        embeddings = create_embeddings(self.test_doc_id)
        print(embeddings)
