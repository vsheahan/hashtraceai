import argparse
import os
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from getpass import getpass

def generate_keys(name, out_dir):
    """
    Generates a new RSA key pair and saves them to the specified directory.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    password = getpass("Enter a password to protect the private key: ")

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode()),
    )

    private_key_path = os.path.join(out_dir, f"{name}.pem")
    with open(private_key_path, "wb") as f:
        f.write(pem)

    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    public_key_path = os.path.join(out_dir, f"{name}.pub")
    with open(public_key_path, "wb") as f:
        f.write(pem)

    # Add the public key to the trusted keys file
    trusted_keys_file = "trusted_keys.json"
    if os.path.exists(trusted_keys_file):
        with open(trusted_keys_file, "r") as f:
            trusted_keys = json.load(f)
    else:
        trusted_keys = {"keys": []}

    trusted_keys["keys"].append({
        "name": name,
        "key": pem.decode(),
    })

    with open(trusted_keys_file, "w") as f:
        json.dump(trusted_keys, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a new key pair."
    )
    parser.add_argument(
        "--name",
        required=True,
        help="The name for the key pair."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="The directory to save the keys to."
    )
    args = parser.parse_args()

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    generate_keys(args.name, args.out_dir)