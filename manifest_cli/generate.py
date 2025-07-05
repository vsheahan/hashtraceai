import os
import json
import hashlib
from pathlib import Path
from urllib.parse import urlparse
import colorama
from huggingface_hub import snapshot_download
import mlflow
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Initialize colorama to make ANSI color codes work on all platforms
colorama.init(autoreset=True)

# --- Helper functions (unchanged, as they were correct) ---

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


def sign_manifest(manifest_bytes, private_key_path):
    """Signs the manifest bytes with a private key."""
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
    """Builds the manifest dictionary by hashing all files in a directory."""
    manifest = {
        "version": "1.0",
        "created_by": created_by,
        "files": []
    }

    for root, _, files in os.walk(path):
        for name in files:
            # Ignore the manifest and its signature if they are in the same directory
            if name == 'manifest.json' or name.endswith('.sig'):
                continue
            filepath = os.path.join(root, name)
            rel_path = os.path.relpath(filepath, path)
            file_hash = hash_file(filepath)
            manifest["files"].append({
                "path": rel_path.replace('\\', '/'), # Normalize path separators
                "sha256": file_hash
            })
    return manifest

# --- Main logic function (Corrected) ---

def run(
    path=None,
    created_by=None,
    out_file="manifest.json",
    hf_id=None,
    mlflow_uri=None,
    sign_key_path=None
):
    """
    Generates a manifest for model files from a local path, Hugging Face, or MLflow.
    """
    if mlflow_uri:
        # Create a unique, safe directory name by hashing the URI.
        # This is robust and works with any MLflow URI format.
        uri_hash = hashlib.sha256(mlflow_uri.encode()).hexdigest()
        cache_path = Path(".cache/hashtraceai/mlflow") / uri_hash
        
        # Only download if the cache directory doesn't already exist.
        if not cache_path.exists():
            cache_path.mkdir(parents=True, exist_ok=True)
            print(f"Downloading MLflow model from '{mlflow_uri}'...")
            # mlflow.artifacts.download_artifacts is versatile and can handle various URIs
            mlflow.artifacts.download_artifacts(artifact_uri=mlflow_uri, dst_path=str(cache_path))
            print(f"Downloaded MLflow model to cache: '{cache_path}'")
        else:
            print(f"Using cached MLflow model from: '{cache_path}'")
        path = str(cache_path)

    elif hf_id:
        print(f"Downloading Hugging Face model '{hf_id}'...")
        # snapshot_download from huggingface_hub handles its own caching
        path = snapshot_download(hf_id)
        print(f"Using Hugging Face model at: '{path}'")

    elif not path:
        print(colorama.Fore.RED + "[ERROR] You must provide a local path, --hf-id, or --mlflow-uri")
        return None # Return None to indicate failure

    manifest = build_manifest(path, created_by)

    # Use a with statement to ensure the file is closed properly
    with open(out_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(colorama.Fore.GREEN + f"Manifest written to '{out_file}'")

    if sign_key_path:
        with open(out_file, 'rb') as f:
            manifest_bytes = f.read()

        signature = sign_manifest(manifest_bytes, sign_key_path)
        sig_file = out_file + '.sig'
        with open(sig_file, 'wb') as f:
            f.write(signature)

        print(colorama.Fore.GREEN + f"Signature written to '{sig_file}'")

    return path