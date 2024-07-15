from cryptography.fernet import Fernet
import os


# Function to generate a key and save it to a file
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


# Function to load the key from the file
def load_key():
    return os.getenv("secret_key", None)


# Function to encrypt a password
def encrypt_password(password):
    key = load_key()
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password


# Function to decrypt a password
def decrypt_password(encrypted_password):
    key = load_key()
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password


# Generate and write a new key (only need to do this once)
# generate_key()

if __name__ == "__main__":
    generate_key()
