''' 
This script generates an RSA key pair and adds the public key to a local trusted_keys.json file.
It supports optional password encryption for the private key.
'''
import os
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
import getpass
import colorama

colorama.init(autoreset=True)

'''
generate_key_pair(name, out_dir)

Generates an RSA key pair, saves the private and public keys to files,
and adds the public key to trusted_keys.json under the given name.
'''
def generate_key_pair(name, out_dir):

    '''
    Generate RSA private key
    '''
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    '''
    Prompt user for a required password to encrypt the private key.
    Re-prompt until a valid and confirmed password is entered.
    '''
    while True:
        password = getpass.getpass("Enter password to encrypt private key: ")
        if not password:
            print(colorama.Fore.RED + "Password is required. Please try again.")
            continue
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print(colorama.Fore.RED + "Passwords do not match. Please try again.")
        else:
            break

    '''
    Set encryption method with the confirmed password.
    '''
    encryption = serialization.BestAvailableEncryption(password.encode('utf-8'))

    '''
    Serialize the private key with selected encryption.
    '''
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )

    '''
    Generate and serialize the public key.
    '''
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    '''
    Create output directory and write private and public keys to files.
    '''
    os.makedirs(out_dir, exist_ok=True)

    private_path = os.path.join(out_dir, f"{name}.key")
    public_path = os.path.join(out_dir, f"{name}.pub")

    with open(private_path, "wb") as f:
        f.write(private_pem)
    with open(public_path, "wb") as f:
        f.write(public_pem)

    print(f"Private key written to: {private_path}")
    print(f"Public key written to: {public_path}")

    '''
    Load or initialize trusted_keys.json and add the new public key.
    '''
    trust_file = Path("trusted_keys.json")
    if trust_file.exists():
        try:
            with open(trust_file, "r") as tf:
                content = tf.read().strip()
                trusted_keys = json.loads(content) if content else {}
        except json.JSONDecodeError:
            print(colorama.Fore.RED + "[ERROR] trusted_keys.json is not valid JSON. Reinitializing.")
            trusted_keys = {}
    else:
        trusted_keys = {}

    trusted_keys[name] = public_pem.decode("utf-8")

    with open(trust_file, "w") as tf:
        json.dump(trusted_keys, tf, indent=2)

    print(f"Public key added to trusted_keys.json under name: '{name}'")

'''
CLI interface for generating key pair from command line arguments.
'''
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate RSA key pair and add public key to trusted_keys.json")
    parser.add_argument("--name", required=True, help="Name of the key pair")
    parser.add_argument("--out-dir", default="keys", help="Directory to save the keys")
    args = parser.parse_args()

    generate_key_pair(args.name, args.out_dir)