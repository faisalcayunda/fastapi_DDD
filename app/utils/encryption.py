import base64
import json
import os
from typing import Dict

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


class CredentialEncryption:
    """
    Kelas untuk mengenkripsi dan mendekripsi data kredensial.

    Menggunakan Fernet (implementasi AES-128-CBC) dengan salt dan PBKDF2
    untuk meningkatkan keamanan.
    """

    def __init__(self):
        self.master_key = settings.SECRET_KEY

    def _derive_key(self, salt):
        master_key_bytes = self.master_key.encode()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        key = base64.urlsafe_b64encode(kdf.derive(master_key_bytes))
        return key

    def encrypt(self, data):
        iv = os.urandom(16)
        iv_b64 = base64.b64encode(iv).decode("utf-8")

        key = self._derive_key(iv)

        cipher = Fernet(key)

        data_json = json.dumps(data)

        encrypted_data = cipher.encrypt(data_json.encode("utf-8"))
        encrypted_b64 = base64.b64encode(encrypted_data).decode("utf-8")

        return encrypted_b64, iv_b64

    def decrypt(self, encrypted_data, iv) -> Dict:
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            iv_bytes = base64.b64decode(iv)

            key = self._derive_key(iv_bytes)

            cipher = Fernet(key)

            decrypted_data = cipher.decrypt(encrypted_bytes)
            decrypted_str = decrypted_data.decode("utf-8")

            data = json.loads(decrypted_str)

            return data
        except Exception as e:
            raise e


# Inisialisasi singleton instance
credential_encryption = CredentialEncryption()
