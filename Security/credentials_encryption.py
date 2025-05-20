import os 
from cryptography.fernet import Fernet
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

    def __init__(self, key_file='security/credentials.key', creds_file='security/credentials.enc'):
        if not hasattr(self, 'initialized'):
            self.key_file = key_file
            self.creds_file = creds_file
            self.key = self.load_or_generate_key()
            self.initialized = True

    def load_or_generate_key(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
            print('New encryption key generated.')
        else:
            with open(self.key_file, 'rb') as key_file:
                key = key_file.read()
        return key

    def encrypt_credentials(self, email, password):
        fernet = Fernet(self.key)
        encrypted_data = fernet.encrypt(f"{email}:{password}".encode())
        with open(self.creds_file, 'wb') as enc_file:
            enc_file.write(encrypted_data)
        print('Credentials encrypted and saved.')

    def decrypt_credentials(self):
        fernet = Fernet(self.key)
        if os.path.exists(self.creds_file):
            with open(self.creds_file, 'rb') as enc_file:
                encrypted_data = enc_file.read()
            decrypted_data = fernet.decrypt(encrypted_data).decode()
            email, password = decrypted_data.split(':')
            return email, password
        else:
            print('No encrypted credentials found.')
            return None, None
