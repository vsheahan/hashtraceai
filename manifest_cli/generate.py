import os
import json
import hashlib
from pathlib import Path
from huggingface_hub import snapshot_download
import mlflow
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def sign_manifest(manifest_bytes, private_key_path):
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    signature = private_key.sign(
        manifest_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return signature


def build_manifest(path, created_by):
    manifest = {
        "version": "1.0",
        "created_by": created_by,
        "files": []
    }

    for root, _, files in os.walk(path):
        for name in files:
            filepath = os.path.join(root, name)
            rel_path = os.path.relpath(filepath, path)
            file_hash = hash_file(filepath)
            manifest["files"].append({
                "path": rel_path,
                "sha256": file_hash
            })

    return manifest


def run(
    path=None,
    created_by=None,
    out_file="manifest.json",
    hf_id=None,
    mlflow_uri=None,
    sign_key_path=None
):
    if mlflow_uri:
        run_id = mlflow_uri.split("/")[1].split("/")[0]
        cache_path = Path(".cache/hashtraceai/mlflow") / run_id
        cache_path.mkdir(parents=True, exist_ok=True)
        mlflow.artifacts.download_artifacts(artifact_uri=mlflow_uri, dst_path=str(cache_path))
        print(f"Downloaded MLflow model to '{cache_path}'")
        path = str(cache_path)

    elif hf_id:
        path = snapshot_download(hf_id)
        print(f"Downloaded Hugging Face model to '{path}'")

    elif not path:
        print("\033[91m[ERROR]\033[0m You must provide a local path, --hf-id, or --mlflow-uri")
        return

    manifest = build_manifest(path, created_by)

    with open(out_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\033[92mManifest written to '{out_file}'\033[0m")

    if sign_key_path:
        with open(out_file, 'rb') as f:
            manifest_bytes = f.read()

        signature = sign_manifest(manifest_bytes, sign_key_path)
        sig_file = out_file + '.sig'
        with open(sig_file, 'wb') as f:
            f.write(signature)

        print(f"\033[92mSignature written to '{sig_file}'\033[0m")

    return path