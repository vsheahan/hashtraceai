import os
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import hashlib

TRUSTED_KEYS_FILE = "trusted_keys.json"

def generate_key_pair(private_key_path, public_key_path, key_name="Unnamed Key"):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(private_key_path, 'wb') as f:
        f.write(private_pem)

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(public_key_path, 'wb') as f:
        f.write(public_pem)

    fingerprint = compute_fingerprint(public_pem)
    record_trusted_key(key_name, public_key_path, fingerprint)

def compute_fingerprint(public_key_bytes):
    digest = hashlib.sha256(public_key_bytes).hexdigest()
    return ":".join(digest[i:i+2] for i in range(0, len(digest), 2))

def record_trusted_key(name, path, fingerprint):
    entry = {
        "name": name,
        "key_path": path,
        "fingerprint": fingerprint
    }

    if os.path.exists(TRUSTED_KEYS_FILE):
        with open(TRUSTED_KEYS_FILE, 'r') as f:
            try:
                keys = json.load(f)
            except json.JSONDecodeError:
                keys = []
    else:
        keys = []

    keys.append(entry)
    with open(TRUSTED_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)