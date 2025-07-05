import argparse
import manifest_cli.generate as generate
import manifest_cli.verify as verify


def main():
    parser = argparse.ArgumentParser(description="HashTraceAI CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Generate
    parser_generate = subparsers.add_parser('generate', help='Generate manifest')
    parser_generate.add_argument('path', nargs='?', help='Path to model files')
    parser_generate.add_argument('--created-by', required=True, help='Creator or system name')
    parser_generate.add_argument('--out', default='manifest.json', help='Output manifest file name')
    parser_generate.add_argument('--sign', help='Path to private key for signing')
    parser_generate.add_argument('--hf-id', help='Hugging Face model ID')
    parser_generate.add_argument('--mlflow-uri', help='MLflow model URI')
    parser_generate.add_argument('--auto-verify', action='store_true', help='Immediately verify after generation')

    # Verify
    parser_verify = subparsers.add_parser('verify', help='Verify manifest')
    parser_verify.add_argument('path', help='Path to model files')
    parser_verify.add_argument('--manifest', required=True, help='Path to manifest.json')
    parser_verify.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser_verify.add_argument('--verify-sig', help='Public key to verify signature')

    args = parser.parse_args()

    if args.command == 'generate':
        gen_path = generate.run(
            path=args.path,
            created_by=args.created_by,
            out_file=args.out,
            hf_id=args.hf_id,
            mlflow_uri=args.mlflow_uri,
            sign_key_path=args.sign
        )

        if args.auto_verify:
            verify.run(
                path=args.path or gen_path,
                manifest_file=args.out,
                output_format='text'
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
