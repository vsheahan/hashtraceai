import os
import json
import hashlib
import base64
import getpass
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def compute_file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def sign_data(sign_key, data):
    with open(sign_key, "rb") as key_file:
        key_bytes = key_file.read()

    try:
        private_key = serialization.load_pem_private_key(
            key_bytes,
            password=None,
        )
    except TypeError:
        password = getpass.getpass("Enter password for private key: ").encode("utf-8")
        private_key = serialization.load_pem_private_key(
            key_bytes,
            password=password,
        )

    message = json.dumps(data, sort_keys=True).encode("utf-8")
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")

def run(
    path,
    created_by,
    sign_key,
    out_file=None,
    model_name=None,
    model_version=None,
    hf_id=None,
    mlflow_uri=None,
    verbose=False
):
    file_hashes = {}
    for root, _, files in os.walk(path):
        for name in files:
            if name.endswith(".pyc") or name.startswith(".") or "venv" in root:
                continue
            filepath = os.path.join(root, name)
            rel_path = os.path.relpath(filepath, path)
            file_hashes[rel_path] = {"SHA256": compute_file_hash(filepath)}

    utc_timestamp = datetime.utcnow().isoformat() + "Z"
    local_timestamp = datetime.now().isoformat()

    signed_data = {
        "created_by": created_by,
        "model_name": model_name,
        "model_version": model_version,
        "timestamp": utc_timestamp,
        "local_timestamp": local_timestamp,
        "files": file_hashes,
    }

    if hf_id:
        signed_data["hf_id"] = hf_id
    if mlflow_uri:
        signed_data["mlflow_uri"] = mlflow_uri

    signature = sign_data(sign_key, signed_data)

    manifest = {
        "signature": signature,
        "signed_data": signed_data,
    }

    if not out_file:
        if model_name and model_version:
            out_file = f"{model_name}_{model_version}_manifest.json"
        else:
            out_file = "manifest.json"

    with open(out_file, "w") as f:
        json.dump(manifest, f, indent=2)

    sig_file = out_file + ".sig"
    with open(sig_file, "w") as f:
        f.write(signature)

    if verbose:
        print(f"Manifest written to {out_file}")
        print(f"Signature written to {sig_file}")
        print(json.dumps(manifest, indent=2))