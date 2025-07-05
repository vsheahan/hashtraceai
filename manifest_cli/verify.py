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


def verify_signature(manifest_bytes, signature_path, public_key_path):
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
        print(f"\033[91m[ERROR]\033[0m Manifest file not found: {manifest_file}")
        return

    try:
        with open(manifest_file, 'rb') as f:
            manifest_bytes = f.read()
    except (IOError, PermissionError) as e:
        print(f"\033[91m[ERROR]\033[0m Could not read manifest file: {e}")
        return

    if verify_sig:
        sig_file = manifest_file + ".sig"
        if not os.path.exists(sig_file):
            print(f"\033[91m[ERROR]\033[0m Signature file not found: {sig_file}")
            return
        if not os.path.exists(verify_sig):
            print(f"\033[91m[ERROR]\033[0m Public key file not found: {verify_sig}")
            return

        if not verify_signature(manifest_bytes, sig_file, verify_sig):
            print("\033[91mSignature verification failed.\033[0m")
            return
        else:
            print("\033[92mSignature verified successfully.\033[0m")

    try:
        manifest = json.loads(manifest_bytes.decode('utf-8'))
    except json.JSONDecodeError:
        print("\033[91m[ERROR]\033[0m Manifest file is corrupted or not valid JSON.")
        return
    except UnicodeDecodeError:
        print("\033[91m[ERROR]\033[0m Manifest file is not encoded in UTF-8.")
        return

    mismatches = []
    base_path = os.path.abspath(path)

    for file_record in manifest.get("files", []):
        relative_path = file_record["path"]
        full_path = os.path.abspath(os.path.join(base_path, relative_path))

        if not full_path.startswith(base_path):
            mismatches.append({"type": "invalid_path", "file": relative_path})
            continue

        if not os.path.exists(full_path):
            mismatches.append({"type": "missing", "file": relative_path})
        elif not os.path.isfile(full_path):
            mismatches.append({"type": "not_a_file", "file": relative_path})
        else:
            try:
                actual_hash = hash_file(full_path)
                if actual_hash != file_record["sha256"]:
                    mismatches.append({"type": "hash_mismatch", "file": relative_path})
            except (IOError, PermissionError) as e:
                mismatches.append({"type": "read_error", "file": relative_path, "error": str(e)})

    if output_format == 'json':
        print(json.dumps({"result": "fail" if mismatches else "success", "mismatches": mismatches}, indent=2))
    else:
        if mismatches:
            print("\033[91mVerification failed:\033[0m")
            for m in mismatches:
                if m["type"] == "missing":
                    print(f"  \033[93m[MISSING]\033[0m    {m['file']}")
                elif m["type"] == "hash_mismatch":
                    print(f"  \033[91m[MISMATCH]\033[0m   {m['file']}")
                elif m["type"] == "invalid_path":
                    print(f"  \033[91m[INVALID]\033[0m    Path is outside the base directory: {m['file']}")
                elif m["type"] == "not_a_file":
                    print(f"  \033[93m[WRONG TYPE]\033[0m Path is not a file: {m['file']}")
                elif m["type"] == "read_error":
                    print(f"  \033[91m[READ ERROR]\033[0m {m['file']} ({m['error']})")
        else:
            print("\033[92mAll files verified successfully.\033[0m")