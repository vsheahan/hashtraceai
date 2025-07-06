import os
import json
import hashlib
import getpass
from pathlib import Path
import colorama
from huggingface_hub import snapshot_download
import mlflow
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

colorama.init(autoreset=True)

def hash_file(filepath):
    """Calculates the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

def sign_manifest(manifest_bytes, private_key_path, password):
    """Signs the manifest bytes with a password-protected private key."""
    if not password:
        raise ValueError("A password is required to load the private key for signing.")
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=password.encode('utf-8')
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

def build_manifest(path, created_by, model_name=None, model_version=None):
    """Builds the manifest dictionary by hashing all files in a directory."""
    manifest = {
        "version": "1.0",
        "created_by": created_by,
        "model_name": model_name,
        "model_version": model_version,
        "files": []
    }
    for root, _, files in os.walk(path):
        for name in files:
            if name == 'manifest.json' or name.endswith('.sig') or name == '.DS_Store':
                continue
            filepath = os.path.join(root, name)
            rel_path = os.path.relpath(filepath, path)
            file_hash = hash_file(filepath)
            manifest["files"].append({
                "path": rel_path.replace('\\', '/'),
                "sha256": file_hash
            })
    return manifest

def generate_manifest(
    path=None,
    created_by=None,
    out_file="manifest.json",
    hf_id=None,
    mlflow_uri=None,
    sign_key_path=None,
    model_name=None,
    model_version=None
):
    """Generates a manifest, prompting for a password if signing is required."""
    # Logic for finding/downloading files remains the same...
    if mlflow_uri:
        uri_hash = hashlib.sha256(mlflow_uri.encode()).hexdigest()
        cache_path = Path(".cache/hashtraceai/mlflow") / uri_hash
        if not cache_path.exists():
            cache_path.mkdir(parents=True, exist_ok=True)
            print(f"Downloading MLflow model from '{mlflow_uri}'...")
            mlflow.artifacts.download_artifacts(artifact_uri=mlflow_uri, dst_path=str(cache_path))
            print(f"Downloaded MLflow model to cache: '{cache_path}'")
        else:
            print(f"Using cached MLflow model from: '{cache_path}'")
        path = str(cache_path)
    elif hf_id:
        print(f"Downloading Hugging Face model '{hf_id}'...")
        path = snapshot_download(hf_id)
        print(f"Using Hugging Face model at: '{path}'")
    elif not path:
        print(colorama.Fore.RED + "[ERROR] You must provide a local path, --hf-id, or --mlflow-uri")
        return None

    if out_file == "manifest.json" and model_name:
        version_suffix = f"_{model_version}" if model_version else ""
        out_file = f"{model_name}{version_suffix}_manifest.json"

    manifest = build_manifest(path, created_by, model_name, model_version)

    with open(out_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(colorama.Fore.GREEN + f"Manifest written to '{out_file}'")

    if sign_key_path:
        # Securely prompt for the password to unlock the private key
        try:
            password = getpass.getpass("Enter private key password to sign manifest: ")
            if not password.strip():
                print(colorama.Fore.RED + "[ERROR] A password is required to sign the manifest.")
                return None
        except Exception as error:
            print(f"\nCould not read password: {error}")
            return None

        with open(out_file, 'rb') as f:
            manifest_bytes = f.read()

        try:
            signature = sign_manifest(manifest_bytes, sign_key_path, password)
            sig_file = out_file + '.sig'
            with open(sig_file, 'wb') as f:
                f.write(signature)
            print(colorama.Fore.GREEN + f"Signature written to '{sig_file}'")
        except Exception as e:
            print(colorama.Fore.RED + f"\n[ERROR] Failed to sign manifest: {e}")
            return None

    return path