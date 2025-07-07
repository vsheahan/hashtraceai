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
    ignore_files = {".DS_Store", "manifest.json"}

    # Initialize the full manifest structure with all metadata
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
        # Remove ignored directories from the walk
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file in ignore_files:
                continue

            file_path = os.path.join(root, file)
            
            if verbose:
                print(f"  ...hashing {os.path.relpath(file_path, directory)}")
                
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                
            manifest["files"].append({
                "name": file,
                "path": os.path.relpath(file_path, directory),
                "sha256": file_hash,
            })

    # The data to be signed ONLY includes the file list for integrity
    data_to_sign = {"files": manifest["files"]}
    message = json.dumps(data_to_sign, sort_keys=True).encode()

    # Sign the file list
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

    # Add the final signature to the full manifest
    manifest["signature"] = base64.b64encode(signature).decode()

    # Write the complete manifest to the output file
    with open(output_file, "w") as f:
        json.dump(manifest, f, indent=4)
        
    if verbose:
        print(f"Manifest generation complete.")