import os
import hashlib
import json
from datetime import datetime
from huggingface_hub import snapshot_download

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def build_manifest(path, created_by, model_id=None):
    manifest = {
        "version": "1.0",
        "created": datetime.utcnow().isoformat() + "Z",
        "created_by": created_by,
        "model_id": model_id if model_id else None,
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

def run(path, created_by, out_file, hf_id=None):
    if hf_id:
        # Download model from Hugging Face and set new path
        local_dir = snapshot_download(repo_id=hf_id)
        path = local_dir
        model_id = hf_id
    else:
        if not path:
            raise ValueError("Must specify a local path or --hf-id")
        model_id = None

    manifest = build_manifest(path, created_by, model_id)

    with open(out_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written to {out_file}")