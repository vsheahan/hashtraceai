import argparse
import manifest_cli.generate as generate
import manifest_cli.verify as verify
import manifest_cli.sign as sign
import manifest_cli.keys as keys

def main():
    parser = argparse.ArgumentParser(prog="cli.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate
    gen_parser = subparsers.add_parser("generate", help="Generate a manifest from a local path, MLflow URI, or Hugging Face ID")
    gen_parser.add_argument("--path", help="Path to the model directory")
    gen_parser.add_argument("--hf-id", help="Hugging Face model ID")
    gen_parser.add_argument("--mlflow-uri", help="MLflow artifact URI")
    gen_parser.add_argument("--created-by", required=True, help="Name of the entity generating the manifest")
    gen_parser.add_argument("--out", default="manifest.json", help="Output manifest file")
    gen_parser.add_argument("--sign-key", help="Path to private key to sign the manifest")

    # Verify
    ver_parser = subparsers.add_parser("verify", help="Verify a manifest against a local model directory")
    ver_parser.add_argument("path", help="Path to the model directory")
    ver_parser.add_argument("--manifest", required=True, help="Path to manifest.json")
    ver_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    ver_parser.add_argument("--verify-sig", help="Path to public key for verifying the signature")

    # Keys
    keys_parser = subparsers.add_parser("keys", help="Key management commands")
    keys_subparsers = keys_parser.add_subparsers(dest="keys_command", required=True)

    keys_gen = keys_subparsers.add_parser("generate", help="Generate a new RSA key pair and add public key to trusted store")
    keys_gen.add_argument("--name", required=True, help="Name of the key")
    keys_gen.add_argument("--out-dir", required=True, help="Directory to write the key files")

    args = parser.parse_args()

    if args.command == "generate":
        generate.run(
            path=args.path,
            created_by=args.created_by,
            out_file=args.out,
            hf_id=args.hf_id,
            mlflow_uri=args.mlflow_uri,
            sign_key_path=args.sign_key
        )

    elif args.command == "verify":
        verify.run(
            path=args.path,
            manifest_file=args.manifest,
            output_format=args.format,
            verify_sig=args.verify_sig
        )

    elif args.command == "keys":
        if args.keys_command == "generate":
            keys.generate_key_pair(
                name=args.name,
                out_dir=args.out_dir
            )

if __name__ == "__main__":
    main()