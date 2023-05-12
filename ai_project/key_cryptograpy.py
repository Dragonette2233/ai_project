from cryptography.fernet import Fernet
import base64
import os

def generete_cipher(api_key):

    SECRET_KEY = base64.urlsafe_b64decode(os.getenv('CRYPT'))
    cipher_suite = Fernet(SECRET_KEY)
    ciphered_apikey = cipher_suite.encrypt(api_key.encode())
    return ciphered_apikey

def decrypt_cipher(cipher):

    SECRET_KEY = base64.urlsafe_b64decode(os.getenv('CRYPT'))
    cipher_suite = Fernet(SECRET_KEY)
    unciphered_apikey = cipher_suite.decrypt(cipher).decode('utf-8')
    return unciphered_apikey

    