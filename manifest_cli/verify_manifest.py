import json
import os
import hashlib
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


def get_key_from_trusted(key_name):
    """
    Retrieves a public key from the trusted_keys.json file.
    """
    with open("trusted_keys.json", "r") as f:
        trusted_keys = json.load(f)
    for key in trusted_keys["keys"]:
        if key["name"] == key_name:
            return serialization.load_pem_public_key(key["key"].encode())
    return None


def verify_manifest(
    manifest_file, directory, public_key_path=None, trusted_key_name=None
):
    """
    Verifies the integrity of the files listed in the manifest.
    """
    with open(manifest_file, "r") as f:
        manifest = json.load(f)

    public_key = None
    if public_key_path:
        with open(public_key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
    elif trusted_key_name:
        public_key = get_key_from_trusted(trusted_key_name)
        if not public_key:
            print(f"Error: Trusted key '{trusted_key_name}' not found.")
            return

    if not public_key:
        print("Error: No public key provided for verification.")
        return

    try:
        data_to_verify = {"files": manifest["files"]}
        message = json.dumps(data_to_verify, sort_keys=True).encode()
        signature = base64.b64decode(manifest["signature"])

        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        print("Signature is valid.")
    except InvalidSignature:
        print("Signature is invalid.")
        return
    except KeyError:
        print(
            "Manifest is missing required fields (files or signature). Cannot verify."
        )
        return

    # --- Verify file hashes ---
    all_good = True
    # ANSI color codes
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    print("--- Verifying File Integrity ---")
    for file_info in manifest["files"]:
        file_path = os.path.join(directory, file_info["path"])
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()

            if actual_hash == file_info["sha256"]:
                # --- GREEN SUCCESS OUTPUT ---
                print(f"{GREEN}OK:{RESET} {file_info['path']}")
            else:
                # --- RED FAILURE OUTPUT ---
                print(f"{RED}FAIL:")
                print(f"  filename: {file_info['name']}")
                print(f"  path: {file_info['path']}")
                print(f"  Expected SHA256: {file_info['sha256']}")
                print(f"  Actual SHA256:   {actual_hash}{RESET}")
                all_good = False
        else:
            print(f"{RED}FAIL: {file_info['path']} (file not found){RESET}")
            all_good = False

    if all_good:
        print(f"\n{GREEN}All file hashes are valid.{RESET}")
