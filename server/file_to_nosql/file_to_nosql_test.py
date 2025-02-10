import io
import unittest
from pathlib import Path
from main import (
    extract_table_data_tesseract_from_bytes,
    file_to_nosql,
    enqueue_embeddings_task,
)


class FakeFile:
    def __init__(self, filename: str, content: bytes, mimetype: str):
        self.filename = filename
        self._buffer = io.BytesIO(content)
        self.mimetype = mimetype
        self.content_type = mimetype

    def read(self, size=-1) -> bytes:
        return self._buffer.read(size)

    def seek(self, offset, whence=0):
        return self._buffer.seek(offset, whence)

    def tell(self):
        return self._buffer.tell()


class TestFileToSql(unittest.TestCase):
    def setUp(self):
        self.jpg_file = Path(__file__).parent.parent.parent / "test/jpg/test1.jpg"
        self.jpg_file = Path(__file__).parent.parent.parent / "test/pdf/test1.pdf"

        self.file_jpg = FakeFile(
            "test1.jpg", open(self.jpg_file, "rb").read(), "image/jpeg"
        )
        self.file_pdf = FakeFile(
            "test1.pdf", open(self.jpg_file, "rb").read(), "application/pdf"
        )
        self.test_doc_id = "Akyc7QWwIbVk8rxrKaaT"

    def test_extract_table_data_tesseract_from_bytes_jpg(self):
        with open(self.jpg_file, "rb") as f:
            image_bytes = f.read()
            val = extract_table_data_tesseract_from_bytes(image_bytes)
            print(val)

    def test_file_to_nosql_jpg(self):
        file_to_nosql(self.file_jpg, "test")

    def test_file_to_nosql_pdf(self):
        file_to_nosql(self.file_pdf, "test")

    def _test_enqueue_embeddings_task(self):
        # import google.auth

        # creds, project_id = google.auth.default()
        # print("Using credentials:", creds.service_account_email)
        enqueue_embeddings_task(self.test_doc_id)
