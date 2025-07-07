import argparse
import json
import os
import hashlib
import base64
import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from getpass import getpass

def generate_manifest(directory, output_file, private_key_path, created_by, model_name, model_version, verbose):
    """
    Generates a manifest file for the specified directory with additional metadata
    and ignores common unnecessary files.
    """
    if verbose:
        print(f"Scanning directory: {directory}")

    # --- Directories and files to ignore ---
    ignore_dirs = {".git", "__pycache__", ".cache", "keys"}
    ignore_files = {".DS_Store"} # Removed "manifest.json"

    # Initialize the full manifest structure
    manifest = {
        "model_name": model_name,
        "model_version": model_version,
        "created_by": created_by,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "timestamp_local": datetime.datetime.now().isoformat(),
        "files": [],
        "signature": None,
    }

    # Populate the file list
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))
            # Skip the manifest file itself and other ignored files
            if os.path.basename(file_path) in ignore_files or file_path == os.path.abspath(output_file):
                continue
            
            if verbose:
                print(f"  ...hashing {os.path.relpath(file_path, directory)}")
                
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                
            manifest["files"].append({
                "name": file,
                "path": os.path.relpath(file_path, directory),
                "sha256": file_hash,
            })

    data_to_sign = {"files": manifest["files"]}
    message = json.dumps(data_to_sign, sort_keys=True).encode()

    if verbose:
        print("\nSigning the manifest...")
    password = getpass("Enter password for private key: ")
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=password.encode(),
        )

    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    manifest["signature"] = base64.b64encode(signature).decode()

    with open(output_file, "w") as f:
        json.dump(manifest, f, indent=4)
        
    if verbose:
        print(f"Manifest generation complete.")