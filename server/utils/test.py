import unittest
from pathlib import Path
from utils.Utilities import PUURLEE_API_KEY, encrypt_text, decrypt_text


class TestUtilities(unittest.TestCase):
    def setUp(self):
        pass

    def test_optionsini(self):
        self.assertEqual(len(PUURLEE_API_KEY), 44)

    def test_encrypt_decrypt(self):
        text = "TESTING!$/\n\n¼µ"
        cypertext = encrypt_text(text)
        # print(text)
        # print(cypertext)
        decrypted = decrypt_text(cypertext)
        # print(decrypted)
        self.assertEqual(text, decrypted)
