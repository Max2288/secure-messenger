import base64
import json
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256, HMAC

class EncryptionModule:
    @staticmethod
    def generate_aes_key():
        return get_random_bytes(32)  # AES-256

    @staticmethod
    def encrypt_message(message: str, aes_key: bytes):
        cipher = AES.new(aes_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(message.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

    @staticmethod
    def encrypt_aes_key(aes_key: bytes, recipient_public_key: str):
        rsa_key = RSA.import_key(recipient_public_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_key = cipher_rsa.encrypt(aes_key)
        return base64.b64encode(encrypted_key).decode()

    @staticmethod
    def sign_message(message: str, sender_secret: bytes):
        hmac = HMAC.new(sender_secret, message.encode(), digestmod=SHA256)
        return base64.b64encode(hmac.digest()).decode()

    @staticmethod
    def encrypt_payload(message: str, recipient_public_key: str, sender_secret: bytes):
        aes_key = EncryptionModule.generate_aes_key()
        encrypted_message = EncryptionModule.encrypt_message(message, aes_key)
        encrypted_aes_key = EncryptionModule.encrypt_aes_key(aes_key, recipient_public_key)
        signature = EncryptionModule.sign_message(message, sender_secret)

        return json.dumps({
            "encrypted_message": encrypted_message,
            "encrypted_aes_key": encrypted_aes_key,
            "signature": signature
        })
