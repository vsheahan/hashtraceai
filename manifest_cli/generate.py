import os
import json
import hashlib
import tempfile
import shutil

from datetime import datetime

try:
    from huggingface_hub import snapshot_download
except ImportError:
    snapshot_download = None

try:
    import mlflow
except ImportError:
    mlflow = None

from .sign import sign_manifest

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

def run(path=None, created_by=None, out_file='manifest.json', hf_id=None, mlflow_uri=None, sign_key_path=None):
    temp_dir = None

    # Priority: MLflow > Hugging Face > local path
    if mlflow_uri:
        if mlflow is None:
            print("\033[91m[ERROR]\033[0m mlflow is not installed. Run: pip install mlflow")
            return
        temp_dir = tempfile.mkdtemp()
        model_path = mlflow.artifacts.download_artifacts(artifact_uri=mlflow_uri, dst_path=temp_dir)
        print(f"Downloaded MLflow model to {model_path}")
        path = model_path
    elif hf_id:
        if snapshot_download is None:
            print("\033[91m[ERROR]\033[0m huggingface_hub is not installed. Run: pip install huggingface_hub")
            return
        path = snapshot_download(hf_id)
        print(f"Downloaded Hugging Face model to {path}")
    elif not path:
        print("\033[91m[ERROR]\033[0m You must provide a local path, --hf-id, or --mlflow-uri")
        return

    manifest = build_manifest(path, created_by)

    with open(out_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written to {out_file}")

    if sign_key_path:
        sign_manifest(out_file, sign_key_path)

    if temp_dir:
        shutil.rmtree(temp_dir)