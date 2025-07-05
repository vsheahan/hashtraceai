import os
import hashlib
import json
from datetime import datetime

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def build_sbom(path, created_by):
    sbom = {
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
                sbom["files"].append({
                    "path": relative_path,
                    "sha256": file_hash
                })

    return sbom

def run(path, created_by, out_file):
    sbom = build_sbom(path, created_by)
    with open(out_file, 'w') as f:
        json.dump(sbom, f, indent=2)
    print(f"SBOM written to {out_file}")