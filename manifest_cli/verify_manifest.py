"""
This script verifies a manifest file by checking the integrity of listed files via SHA256 hashes
and confirming the manifest signature using a trusted or provided public key.
"""

import os
import json
import hashlib
from colorama import Fore
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def hash_file(filepath):
    """
    Computes the SHA256 hash of the specified file.
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_signature(manifest_bytes, signature_path, public_key_path):
    """
    Verifies the digital signature on the manifest using the provided public key.
    Returns True if valid, False otherwise.
    """
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


def load_trusted_key_path(key_name):
    """
    Loads the path of a trusted public key from trusted_keys.json by key name.
    Returns the path string if found, otherwise None.
    """
    try:
        with open("trusted_keys.json", "r") as f:
            trusted_keys = json.load(f)
        return trusted_keys.get(key_name)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def run(path, manifest_file, verify_sig, output_format='text', trusted_key_name=None):
    """
    Verifies the integrity and authenticity of files listed in a manifest file.

    Args:
        path: Base directory to verify files against.
        manifest_file: Path to the manifest JSON file.
        output_format: Output format, either 'text' or 'json'. Defaults to 'text'.
        verify_sig: Path to the public key file for signature verification (required).
        trusted_key_name: Optional name of a trusted key (from trusted_keys.json) to use for verification.
    """
    if not os.path.exists(manifest_file):
        print(Fore.RED + f"[ERROR] Manifest file not found: {manifest_file}")
        return

    try:
        with open(manifest_file, 'rb') as f:
            manifest_bytes = f.read()
    except (IOError, PermissionError) as e:
        print(Fore.RED + f"[ERROR] Could not read manifest file: {e}")
        return

    sig_file = manifest_file + ".sig"
    if not os.path.exists(sig_file):
        print(Fore.RED + f"[ERROR] Signature file not found: {sig_file}")
        return

    public_key_path = None
    if trusted_key_name:
        public_key_path = load_trusted_key_path(trusted_key_name)
        if not public_key_path or not os.path.exists(public_key_path):
            print(Fore.RED + f"[ERROR] Public key for '{trusted_key_name}' not found or path invalid")
            return
    else:
        if not os.path.exists(verify_sig):
            print(Fore.RED + f"[ERROR] Public key file not found: {verify_sig}")
            return
        public_key_path = verify_sig

    if not verify_signature(manifest_bytes, sig_file, public_key_path):
        print(Fore.RED + "Signature verification failed.")
        return
    else:
        print(Fore.GREEN + "Signature verified successfully.")

    try:
        manifest = json.loads(manifest_bytes.decode('utf-8'))
    except json.JSONDecodeError:
        print(Fore.RED + "[ERROR] Manifest file is not valid JSON.")
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
                    mismatches.append({
                        "type": "hash_mismatch",
                        "file": relative_path,
                        "expected": file_record["sha256"],
                        "actual": actual_hash
                    })
            except (IOError, PermissionError) as e:
                mismatches.append({"type": "read_error", "file": relative_path, "error": str(e)})

    if output_format == 'json':
        print(json.dumps({"result": "fail" if mismatches else "success", "mismatches": mismatches}, indent=2))
    else:
        if mismatches:
            print(Fore.RED + "Verification failed:")
            for m in mismatches:
                if m["type"] == "missing":
                    print(Fore.YELLOW + f"  [MISSING]    {m['file']}")
                elif m["type"] == "hash_mismatch":
                    print(Fore.RED + f"  [MISMATCH]   {m['file']}")
                    print(Fore.RED + f"    Expected: {m['expected']}")
                    print(Fore.RED + f"    Actual:   {m['actual']}")
                elif m["type"] == "invalid_path":
                    print(Fore.RED + f"  [INVALID]    Path is outside the base directory: {m['file']}")
                elif m["type"] == "not_a_file":
                    print(Fore.YELLOW + f"  [WRONG TYPE] Path is not a file: {m['file']}")
                elif m["type"] == "read_error":
                    print(Fore.RED + f"  [READ ERROR] {m['file']} ({m['error']})")
        else:
            print(Fore.GREEN + "All files verified successfully.")