import os
import json
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_signature(manifest_path, signature_path, public_key_path):
    with open(manifest_path, 'rb') as f:
        manifest_bytes = f.read()

    with open(signature_path, 'rb') as f:
        signature = f.read()

    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())

    try:
        public_key.verify(
            signature,
            manifest_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


def run(path, manifest_file, output_format='text', verify_sig=None):
    if not os.path.exists(manifest_file):
        print("\033[91m[ERROR]\033[0m Manifest file not found: " + manifest_file)
        return

    if verify_sig:
        sig_file = manifest_file + ".sig"
        if not os.path.exists(sig_file):
            print("\033[91m[ERROR]\033[0m Signature file not found: " + sig_file)
            return

        if not os.path.exists(verify_sig):
            print("\033[91m[ERROR]\033[0m Public key file not found: " + verify_sig)
            return

        if not verify_signature(manifest_file, sig_file, verify_sig):
            print("\033[91mSignature verification failed.\033[0m")
            return
        else:
            print("\033[92mSignature verified successfully.\033[0m")

    with open(manifest_file, 'r') as f:
        manifest = json.load(f)

    mismatches = []
    for file_record in manifest.get("files", []):
        expected_path = os.path.join(path, file_record["path"])
        if not os.path.exists(expected_path):
            mismatches.append({"type": "missing", "file": file_record["path"]})
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

         