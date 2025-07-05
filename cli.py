import argparse
from manifest_cli import generate, verify

def main():
    parser = argparse.ArgumentParser(description='HashTraceAI CLI')
    subparsers = parser.add_subparsers(dest='command')

    # Generate subcommand
    gen = subparsers.add_parser('generate')
    gen.add_argument('path', nargs='?', help='Path to model directory')
    gen.add_argument('--hf-id', help='Hugging Face model ID to fetch')
    gen.add_argument('--created-by', required=True, help='Creator metadata')
    gen.add_argument('--out', default='manifest.json', help='Output manifest file')

    # Verify subcommand
    ver = subparsers.add_parser('verify')
    ver.add_argument('path', help='Path to model directory')
    ver.add_argument('--sbom', default='manifest.json', help='Manifest file to verify against')
    ver.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    args = parser.parse_args()

    if args.command == 'generate':
        generate.run(args.path, args.hf_id, args.created_by, args.out)
    elif args.command == 'verify':
        verify.run(args.path, args.sbom, args.format)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()