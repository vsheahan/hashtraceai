import os
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
import getpass
import colorama

colorama.init(autoreset=True)

def generate_key_pair(name, out_dir):
    print("[DEBUG] generate_key_pair called")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    password = getpass.getpass("Enter password to encrypt private key (leave blank for no encryption): ")
    confirm = getpass.getpass("Confirm password: ") if password else ""

    if password and password != confirm:
        print(colorama.Fore.RED + "Passwords do not match. Key generation aborted.")
        return

    encryption = serialization.NoEncryption()
    if password:
        encryption = serialization.BestAvailableEncryption(password.encode('utf-8'))
    else:
        print(colorama.Fore.YELLOW + "Warning: Private key will be generated unencrypted.")

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    os.makedirs(out_dir, exist_ok=True)

    private_path = os.path.join(out_dir, f"{name}.key")
    public_path = os.path.join(out_dir, f"{name}.pub")

    with open(private_path, "wb") as f:
        f.write(private_pem)
    with open(public_path, "wb") as f:
        f.write(public_pem)

    print(f"Private key written to: {private_path}")
    print(f"Public key written to: {public_path}")

    # Add to trusted_keys.json
    trust_file = Path("trusted_keys.json")
    if trust_file.exists():
        with open(trust_file, "r") as tf:
            trusted_keys = json.load(tf)
    else:
        trusted_keys = {}

    trusted_keys[name] = public_pem.decode("utf-8")

    with open(trust_file, "w") as tf:
        json.dump(trusted_keys, tf, indent=2)

    print(f"Public key added to trusted_keys.json under name: '{name}'")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate RSA key pair and add public key to trusted_keys.json")
    parser.add_argument("--name", required=True, help="Name of the key pair")
    parser.add_argument("--out-dir", default="keys", help="Directory to save the keys")
    args = parser.parse_args()

    generate_key_pair(args.name, args.out_dir)