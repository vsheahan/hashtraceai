import os
import json
import hashlib
import tempfile
from huggingface_hub import snapshot_download
import mlflow
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


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
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

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
    # Priority: MLflow > Hugging Face > local path
    if mlflow_uri:
        if mlflow is None:
            print("\033[91m[ERROR]\033[0m mlflow is not installed. Run: pip install mlflow")
            return
        temp_dir = tempfile.mkdtemp()
        mlflow.artifacts.download_artifacts(artifact_uri=mlflow_uri, dst_path=temp_dir)
        print(f"Downloaded MLflow model to '{temp_dir}'")
        path = temp_dir

    elif hf_id:
        if snapshot_download is None:
            print("\033[91m[ERROR]\033[0m huggingface_hub is not installed. Run: pip install huggingface_hub")
            return
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