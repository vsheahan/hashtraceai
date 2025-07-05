## cli.py

import argparse
import getpass
import manifest_cli.generate as generate
import manifest_cli.verify as verify
import manifest_cli.keys as keys

def main():
    parser = argparse.ArgumentParser(description="HashTraceAI CLI")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # --- Keys Command ---
    parser_keys = subparsers.add_parser('keys', help='Manage cryptographic keys')
    keys_subparsers = parser_keys.add_subparsers(dest='keys_command', required=True)
    parser_keys_generate = keys_subparsers.add_parser('generate', help='Generate a new encrypted key pair')
    parser_keys_generate.add_argument('--priv', default='private_key.pem', help='Output private key file')
    parser_keys_generate.add_argument('--pub', default='public_key.pem', help='Output public key file')

    # --- Generate Command ---
    parser_generate = subparsers.add_parser('generate', help='Generate manifest')
    # ... arguments remain the same

    # --- Verify Command ---
    parser_verify = subparsers.add_parser('verify', help='Verify manifest')
    # ... arguments remain the same

    # (Re-adding generate and verify arguments for completeness)
    parser_generate.add_argument('path', nargs='?', help='Path to model files')
    parser_generate.add_argument('--created-by', required=True, help='Creator or system name')
    parser_generate.add_argument('--out', default='manifest.json', help='Output manifest file name')
    parser_generate.add_argument('--sign', help='Path to private key for signing')
    parser_generate.add_argument('--hf-id', help='Hugging Face model ID')
    parser_generate.add_argument('--mlflow-uri', help='MLflow model URI')
    parser_generate.add_argument('--auto-verify', action='store_true', help='Immediately verify after generation')

    parser_verify.add_argument('path', help='Path to model files')
    parser_verify.add_argument('--manifest', required=True, help='Path to manifest.json')
    parser_verify.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser_verify.add_argument('--verify-sig', help='Public key to verify signature')

    args = parser.parse_args()

    if args.command == 'keys':
        if args.keys_command == 'generate':
            try:
                password = getpass.getpass("Enter a new password for the private key: ")
                if not password:
                    print("Password cannot be empty.")
                    return
                confirm_password = getpass.getpass("Confirm password: ")
                if password != confirm_password:
                    print("Passwords do not match.")
                    return
                keys.generate_keys(args.priv, args.pub, password)
                print(f"\nSuccessfully generated key pair:\n  Private Key: {args.priv}\n  Public Key:  {args.pub}")
            except Exception as e:
                print(f"\n[ERROR] Could not generate keys: {e}")

    elif args.command == 'generate':
        gen_path = generate.run(
            path=args.path,
            created_by=args.created_by,
            out_file=args.out,
            hf_id=args.hf_id,
            mlflow_uri=args.mlflow_uri,
            sign_key_path=args.sign
        )
        if gen_path and args.auto_verify:
            # Verification does not require a password as it uses the public key
            verify.run(
                path=args.path or gen_path,
                manifest_file=args.out,
                output_format='text',
                verify_sig=None # auto-verify can't know the public key path, this remains a manual step
            )

    elif args.command == 'verify':
        verify.run(
            path=args.path,
            manifest_file=args.manifest,
            output_format=args.format,
            verify_sig=args.verify_sig
        )

if __name__ == '__main__':
    main()