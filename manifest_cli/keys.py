import os
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path

def generate_key_pair(name, out_dir):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b"password"),
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