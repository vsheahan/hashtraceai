import argparse
import os
from manifest_cli import generate_keys, generate_manifest, verify_manifest

def main():
    parser = argparse.ArgumentParser(description="A tool for managing file manifests.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Generate keys command ---
    keys_parser = subparsers.add_parser("keys", help="Generate a new key pair.")
    keys_parser.add_argument("--name", required=True, help="The name for the key pair.")
    keys_parser.add_argument("--out-dir", default=".", help="The directory to save the keys to.")

    # --- Generate manifest command ---
    generate_parser = subparsers.add_parser("generate", help="Generate a manifest.")
    generate_parser.add_argument("--path", required=True, dest="directory", help="The root directory to scan.")
    generate_parser.add_argument("--created-by", required=True, help="The name of the manifest creator.")
    generate_parser.add_argument("--sign-key", required=True, dest="private_key_path", help="The path to the private key for signing.")
    generate_parser.add_argument("--model-name", required=True, help="The name of the model or project.")
    generate_parser.add_argument("--model-version", required=True, help="The version of the model or project.")
    generate_parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")

    # --- Verify manifest command ---
    verify_parser = subparsers.add_parser("verify", help="Verify a manifest.")
    verify_parser.add_argument("--manifest-file", required=True, help="The manifest file to verify.")
    verify_parser.add_argument("--directory", default=".", help="The root directory of the project files to verify against.")
    group = verify_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--public-key", help="The public key to verify with.")
    group.add_argument("--trusted-key", help="The name of the trusted key to use for verification.")

    args = parser.parse_args()

    # --- Command routing ---
    if args.command == "keys":
        generate_keys.generate_keys(args.name, args.out_dir)
        print(f"Generated keys: {args.name}.pub and {args.name}.pem in {args.out_dir}")

    elif args.command == "generate":
        output_file = os.path.join(args.directory, "manifest.json")
        generate_manifest.generate_manifest(
            directory=args.directory,
            output_file=output_file,
            private_key_path=args.private_key_path,
            created_by=args.created_by,
            model_name=args.model_name,
            model_version=args.model_version,
            verbose=args.verbose
        )
        print(f"\nSuccessfully generated manifest at: {output_file}")

    elif args.command == "verify":
        verify_manifest.verify_manifest(args.manifest_file, args.directory, args.public_key, args.trusted_key)

if __name__ == "__main__":
    main()