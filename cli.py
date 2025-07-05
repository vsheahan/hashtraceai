import argparse
from manifest_cli import generate, verify

def main():
    parser = argparse.ArgumentParser(description='HashTraceAI CLI')
    subparsers = parser.add_subparsers(dest='command')

    # Generate command
    gen = subparsers.add_parser('generate')
    gen.add_argument('path', nargs='?', help='Path to local model directory (optional if using --hf-id or --mlflow-uri)')
    gen.add_argument('--hf-id', help='Hugging Face model ID (e.g., bert-base-uncased)')
    gen.add_argument('--mlflow-uri', help='MLflow model URI')
    gen.add_argument('--created-by', required=True, help='Creator metadata')
    gen.add_argument('--out', default='manifest.json', help='Output manifest file')
    gen.add_argument('--sign', help='Path to RSA private key for signing the manifest')

    # Verify command
    ver = subparsers.add_parser('verify')
    ver.add_argument('path', help='Path to model directory')
    ver.add_argument('--manifest', default='manifest.json', help='Manifest file to verify against')
    ver.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    ver.add_argument('--verify-sig', help='Path to RSA public key for signature verification')

    args = parser.parse_args()

    if args.command == 'generate':
        generate.run(
            path=args.path,
            created_by=args.created_by,
            out_file=args.out,
            hf_id=args.hf_id,
            mlflow_uri=args.mlflow_uri,
            sign_key_path=args.sign
        )
    elif args.command == 'verify':
        verify.run(
            path=args.path,
            manifest_file=args.manifest,
            output_format=args.format,
            verify_sig=args.verify_sig
        )
    else:
        parser.print_help()

if __name__ == '__main__':
    main()