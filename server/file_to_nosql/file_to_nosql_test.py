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
        self.jpg_file = Path(__file__).parent.parent.parent / "test/jpg/page1.jpg"
        self.file = FakeFile(
            "page1.jpg", open(self.jpg_file, "rb").read(), "image/jpeg"
        )
        self.test_doc_id = "Akyc7QWwIbVk8rxrKaaT"

    def test_extract_table_data_tesseract_from_bytes_jpg(self):
        with open(self.jpg_file, "rb") as f:
            image_bytes = f.read()
            val = extract_table_data_tesseract_from_bytes(image_bytes)
            print(val)

    def test_file_to_nosql(self):
        file_to_nosql(self.file, "test")

    def test_enqueue_embeddings_task(self):
        enqueue_embeddings_task(self.test_doc_id)
