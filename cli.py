import argparse
from manifest_cli import generate, verify


def main():
    parser = argparse.ArgumentParser(description="HashTraceAI CLI")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: generate
    gen_parser = subparsers.add_parser("generate", help="Generate a manifest")
    gen_parser.add_argument("path", nargs="?", help="Path to model directory")
    gen_parser.add_argument("--created-by", required=True, help="Creator metadata for manifest")
    gen_parser.add_argument("--out", default="manifest.json", help="Output manifest file path")
    gen_parser.add_argument("--sign", help="Path to RSA private key to sign the manifest")
    gen_parser.add_argument("--hf-id", help="Hugging Face model ID")
    gen_parser.add_argument("--mlflow-uri", help="MLflow artifact URI (e.g. runs:/RUN_ID/model)")

    # Subcommand: verify
    ver_parser = subparsers.add_parser("verify", help="Verify files against a manifest")
    ver_parser.add_argument("path", help="Path to directory with model files")
    ver_parser.add_argument("--manifest", required=True, help="Path to manifest file")
    ver_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    ver_parser.add_argument("--verify-sig", help="Path to RSA public key to verify signature")

    args = parser.parse_args()

    if args.command == "generate":
        generate.run(
            path=args.path,
            hf_id=args.hf_id,
            mlflow_uri=args.mlflow_uri,
            created_by=args.created_by,
            out_file=args.out,
            sign_key_path=args.sign
        )

    elif args.command == "verify":
        verify.run(
            path=args.path,
            manifest_file=args.manifest,
            output_format=args.format,
            verify_sig=args.verify_sig
        )


if __name__ == "__main__":
    main()