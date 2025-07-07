import os
import subprocess
import argparse
from huggingface_hub import snapshot_download

def download_and_generate_manifest(model_id, created_by, sign_key, model_version, verbose):
    """
    Downloads a model from the Hugging Face Hub and generates a manifest for it.
    """
    try:
        # 1. Download the model snapshot from Hugging Face
        print(f"--- Downloading model: {model_id} ---")
        # The snapshot_download function returns the path to the downloaded directory
        model_path = snapshot_download(repo_id=model_id)
        print(f"Model downloaded successfully to: {model_path}")
        print("-" * 20)

        # 2. Prepare the arguments for our existing cli.py script
        # Note: We need the full path for the signing key
        sign_key_path = os.path.abspath(sign_key)
        
        # Extract the model name from the model_id (e.g., "distilbert-base-uncased")
        model_name = model_id.split('/')[-1]

        # 3. Call the cli.py 'generate' command using subprocess
        print(f"--- Generating manifest for {model_name} ---")
        command = [
            "python3",
            "cli.py",
            "generate",
            "--path", model_path,
            "--created-by", created_by,
            "--sign-key", sign_key_path,
            "--model-name", model_name,
            "--model-version", model_version,
        ]
        
        # Add the --verbose flag if requested
        if verbose:
            command.append("--verbose")

        # Run the command
        subprocess.run(command, check=True)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a model from Hugging Face and generate a manifest.")
    parser.add_argument("--model-id", required=True, help="The ID of the model on Hugging Face (e.g., 'distilbert-base-uncased').")
    parser.add_argument("--created-by", required=True, help="The name of the manifest creator.")
    parser.add_argument("--sign-key", required=True, help="The path to the private key for signing.")
    parser.add_argument("--model-version", default="1.0", help="The version to assign to the model.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")

    args = parser.parse_args()

    download_and_generate_manifest(
        model_id=args.model_id,
        created_by=args.created_by,
        sign_key=args.sign_key,
        model_version=args.model_version,
        verbose=args.verbose
    )