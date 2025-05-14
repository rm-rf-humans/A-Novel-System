import os
from cryptography.fernet import Fernet

class CredentialsManager:
    def __init__(self, key_file='security/credentials.key', creds_file='security/credentials.enc'):
        self.key_file = key_file
        self.creds_file = creds_file
        self.key = self.load_or_generate_key()

    def load_or_generate_key(self):
        # Generate a key if it doesn't exist
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
