import argparse
from manifest_cli import generate, verify, sign


def main():
    parser = argparse.ArgumentParser(description="HashTraceAI CLI")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Generate manifest
    gen_parser = subparsers.add_parser('generate', help='Generate a manifest')
    gen_parser.add_argument('path', nargs='?', help='Directory path to model files')
    gen_parser.add_argument('--hf-id', help='Hugging Face model ID')
    gen_parser.add_argument('--mlflow-uri', help='MLflow model URI')
    gen_parser.add_argument('--created-by', required=True, help='Creator identifier')
    gen_parser.add_argument('--out', required=True, help='Output path for manifest')
    gen_parser.add_argument('--sign', help='Path to RSA private key to sign the manifest')

    # Verify manifest
    verify_parser = subparsers.add_parser('verify', help='Verify files against a manifest')
    verify_parser.add_argument('path', help='Directory containing model files')
    verify_parser.add_argument('--manifest', required=True, help='Path to the manifest file')
    verify_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    verify_parser.add_argument('--verify-sig', help='Public key path to verify signature')

    # Sign a manifest
    sign_parser = subparsers.add_parser('sign', help='Sign an existing manifest')
    sign_parser.add_argument('--manifest', required=True, help='Path to manifest to sign')
    sign_parser.add_argument('--key', required=True, help='Path to RSA private key')
    sign_parser.add_argument('--out', help='Path to save signature (default: manifest.sig)')

    # Key generation
    keygen_parser = subparsers.add_parser('keygen', help='Generate RSA key pair')
    keygen_parser.add_argument('--private', default='private.pem', help='Output path for private key')
    keygen_parser.add_argument('--public', default='public.pem', help='Output path for public key')

    args = parser.parse_args()

    if args.command == 'generate':
        generate.run(
            path=args.path,
            created_by=args.created_by,
            out_path=args.out,
            hf_id=args.hf_id,
            mlflow_uri=args.mlflow_uri,
            sign_key=args.sign
        )
    elif args.command == 'verify':
        verify.run(
            path=args.path,
            manifest_file=args.manifest,
            output_format=args.format,
            verify_sig=args.verify_sig
        )
    elif args.command == 'sign':
        sign.sign_manifest(
            manifest_path=args.manifest,
            private_key_path=args.key,
            signature_output_path=args.out
        )
    elif args.command == 'keygen':
        sign.generate_key_pair(
            private_key_path=args.private,
            public_key_path=args.public
        )


if __name__ == '__main__':
    main()