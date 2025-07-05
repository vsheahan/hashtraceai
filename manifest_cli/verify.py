import os
import json
import hashlib

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def run(path, manifest_file, output_format='text'):
    if not os.path.exists(manifest_file):
        print("\033[91m[ERROR]\033[0m Manifest file not found: " + manifest_file)
        return

    with open(manifest_file, 'r') as f:
        manifest = json.load(f)

    mismatches = []

    for file_record in manifest.get("files", []):
        expected_path = os.path.join(path, file_record["path"])
        if not os.path.exists(expected_path):
            mismatches.append({
                "type": "missing",
                "file": file_record["path"]
            })
        else:
            actual_hash = hash_file(expected_path)
            if actual_hash != file_record["sha256"]:
                mismatches.append({
                    "type": "hash_mismatch",
                    "file": file_record["path"]
                })

    if output_format == 'json':
        print(json.dumps({
            "result": "fail" if mismatches else "success",
            "mismatches": mismatches
        }, indent=2))
    else:
        if mismatches:
            print("\033[91mVerification failed:\033[0m")
            for m in mismatches:
                if m["type"] == "missing":
                    print(f"  \033[93m[MISSING]\033[0m {m['file']}")
                elif m["type"] == "hash_mismatch":
                    print(f"  \033[91m[MISMATCH]\033[0m {m['file']}")
        else:
            print("\033[92mAll files verified successfully.\033[0m")