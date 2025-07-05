import argparse
import os
from manifest_cli import generate, verify

parser = argparse.ArgumentParser(
    description="HashTraceAI CLI – Generate or verify model integrity manifests."
)
subparsers = parser.add_subparsers(dest="command", required=True)

# Generate command
generate_parser = subparsers.add_parser("generate", help="Generate a manifest")
generate_parser.add_argument("path", nargs="?", help="Path to the model directory")
generate_parser.add_argument(
    "--out", default="manifest.json", help="Output manifest filename"
)
generate_parser.add_argument(
    "--created-by", default="unknown", help="Creator of the manifest"
)
generate_parser.add_argument(
    "--hf-id", help="Optional Hugging Face model ID to download and hash"
)
generate_parser.add_argument(
    "--mlflow-uri", help="Optional MLflow model URI to hash"
)
generate_parser.add_argument(
    "--sign", help="Optional path to private key to sign the manifest"
)

# Verify command
verify_parser = subparsers.add_parser("verify", help="Verify files against a manifest")
verify_parser.add_argument(
    "path", help="Path to the model directory to verify"
)
verify_parser.add_argument(
    "--manifest", required=True, help="Path to manifest JSON file"
)
verify_parser.add_argument(
    "--format", choices=["text", "json"], default="text", help="Output format"
)
verify_parser.add_argument(
    "--verify-sig", help="Optional path to public key for signature verification"
)

args = parser.parse_args()

if args.command == "generate":
    generate.run(
        path=args.path,
        output_file=args.out,
        created_by=args.created_by,
        hf_id=args.hf_id,
        mlflow_uri=args.mlflow_uri,
        sign_key=args.sign
    )
elif args.command == "verify":
    verify.run(
        path=args.path,
        manifest_file=args.manifest,
        output_format=args.format,
        verify_sig=args.verify_sig
    )