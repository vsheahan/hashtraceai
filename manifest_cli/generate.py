import os
import hashlib
import json
from datetime import datetime
from typing import Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def build_manifest(path, created_by):
    manifest = {
        "version": "1.0",
        "created": datetime.utcnow().isoformat() + "Z",
        "created_by": created_by,
        "files": []
    }

    for root, _, files in os.walk(path):
        for filename in files:
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path):
                relative_path = os.path.relpath(full_path, path)
                file_hash = hash_file(full_path)
                manifest["files"].append({
                    "path": relative_path,
                    "sha256": file_hash
                })

    return manifest

def sign_manifest(manifest_dict, private_key_path: str) -> str:
    manifest_bytes = json.dumps(manifest_dict, sort_keys=True).encode('utf-8')

    with open(private_key_path, 'rb') as key_file:
        private_key = load_pem_private_key(key_file.read(), password=None)

    signature = private_key.sign(
        manifest_bytes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature.hex()

def run(path, created_by, out_file, sign_key_path: Optional[str] = None):
    manifest = build_manifest(path, created_by)

    if sign_key_path:
        signature = sign_manifest(manifest, sign_key_path)
        manifest["signature"] = signature

    with open(out_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written to {out_file}")