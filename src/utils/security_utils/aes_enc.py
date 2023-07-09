from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from src.common.settings import config

class AESCipher:
    """
    A classical AES Cipher. Can use any size of data and any size of password thanks to padding.
    Also ensure the coherence and the type of the data with a unicode to byte converter.
    """

    def __init__(self):
        self.key = config.encryption_key.encode()

    def encrypt(self, message):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
        iv = cipher.iv
        encrypted_message = iv + ciphertext
        return b64encode(encrypted_message).decode()

    def decrypt(self, ciphertext):
        ciphertext = b64decode(ciphertext)
        iv = ciphertext[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext[16:]), AES.block_size)
        return decrypted.decode()