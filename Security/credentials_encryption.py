import os
from cryptography.fernet import Fernet, InvalidToken
from abc import ABC, abstractmethod

class BaseCredentialsManager(ABC):
    @abstractmethod
    def encrypt_credentials(self, email, password):
        pass

    @abstractmethod
    def decrypt_credentials(self):
        pass

class CredentialsManager(BaseCredentialsManager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, key_file='Security/credentials.key', creds_file='Security/credentials.enc'):
        if not hasattr(self, 'initialized'):
            self.key_file = key_file
            self.creds_file = creds_file

            key_dir = os.path.dirname(self.key_file)
            if key_dir and not os.path.exists(key_dir):
                os.makedirs(key_dir, exist_ok=True)

            creds_dir = os.path.dirname(self.creds_file)
            if creds_dir and not os.path.exists(creds_dir):
                os.makedirs(creds_dir, exist_ok=True)

            self.key = self.load_or_generate_key()
            self.initialized = True

    def load_or_generate_key(self):
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read().strip()
                _ = Fernet(key)
                return key
            except (ValueError, InvalidToken):
                print('Invalid key found; generating a new key.')

        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as f:
            f.write(key)
        print('New encryption key generated.')
        return key

    def encrypt_credentials(self, email, password):
        fernet = Fernet(self.key)
        data = f"{email}:{password}".encode()
        encrypted = fernet.encrypt(data)
        with open(self.creds_file, 'wb') as f:
            f.write(encrypted)
        print('Credentials encrypted and saved.')

    def decrypt_credentials(self):
        if not os.path.exists(self.creds_file):
            print('No encrypted credentials found.')
            return None, None

        with open(self.creds_file, 'rb') as f:
            encrypted = f.read()

        fernet = Fernet(self.key)
        try:
            decrypted = fernet.decrypt(encrypted).decode()
            email, password = decrypted.split(':', 1)
            return email, password
        except InvalidToken:
            print('Decryption failed. Data may be corrupted or key is invalid.')
            return None, None
