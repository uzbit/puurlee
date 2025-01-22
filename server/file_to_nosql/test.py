import unittest
from pathlib import Path
from main import extract_table_data_tesseract_from_bytes


class TestFileToSql(unittest.TestCase):
    def setUp(self):
        self.jpgImg = Path(__file__).parent.parent.parent / "test/jpg/page1.jpg"
        
    def test_extract_table_data_tesseract_from_bytes_jpg(self):
        with open(self.jpgImg, "rb") as f:
            image_bytes = f.read()
            val = extract_table_data_tesseract_from_bytes(image_bytes)
            print(val)
