import unittest
from embeddings.main import create_embeddings, store_embeddings_in_pinecone


class TestEmbeddings(unittest.TestCase):
    def setUp(self):
        self.test_doc_id = "g82ryS54hvY9MfzRzJyE"

    def test_create_embeddings(self):
        embeddings, user_id = create_embeddings(self.test_doc_id)
        print(embeddings, user_id)

    def test_store_embeddings_in_pinecone(self):
        embeddings, user_id = create_embeddings(self.test_doc_id)
        store_embeddings_in_pinecone(embeddings, user_id, self.test_doc_id)
