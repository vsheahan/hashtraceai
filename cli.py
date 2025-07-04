import argparse
from sbom_cli import generate, verify

def main():
    parser = argparse.ArgumentParser(description='HashTrace CLI')
    subparsers = parser.add_subparsers(dest='command')

    gen = subparsers.add_parser('generate')
    gen.add_argument('path', help='Path to model directory')
    gen.add_argument('--created-by', required=True, help='Creator metadata')
    gen.add_argument('--out', default='sbom.json', help='Output SBOM file')

    ver = subparsers.add_parser('verify')
    ver.add_argument('path', help='Path to model directory')
    ver.add_argument('--sbom', default='sbom.json', help='SBOM file to verify against')

    args = parser.parse_args()

    if args.command == 'generate':
        print("Generating SBOM...")
        # generate.run(args.path, args.created_by, args.out)
    elif args.command == 'verify':
        print("Verifying SBOM...")
        # verify.run(args.path, args.sbom)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()